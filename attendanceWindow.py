import os
from datetime import datetime, date

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLineEdit,
    QScrollArea,
    QBoxLayout,
    QStackedWidget,
    QComboBox,
    QTimeEdit,
    QDialog
)

from PySide6.QtCore import Qt, QTimer, QTime, QPoint, QDate, Signal
from PySide6.QtGui import QPainter, QColor

from database import Database

# =========================================================
# JALALI CONVERSION
# =========================================================

def gregorian_to_jalali(gy, gm, gd):

    g_d_m = [
        0, 31, 59, 90, 120, 151,
        181, 212, 243, 273, 304, 334
    ]

    if gm > 2:
        gy2 = gy + 1
    else:
        gy2 = gy

    days = (
        355666
        + (365 * gy)
        + ((gy2 + 3) // 4)
        - ((gy2 + 99) // 100)
        + ((gy2 + 399) // 400)
        + gd
        + g_d_m[gm - 1]
    )

    jy = -1595 + (33 * (days // 12053))
    days %= 12053

    jy += 4 * (days // 1461)
    days %= 1461

    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365

    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)

    return jy, jm, jd

def jalali_to_gregorian(jy, jm, jd):

    jy += 1595

    days = (
        -355668
        + (365 * jy)
        + ((jy // 33) * 8)
        + (((jy % 33) + 3) // 4)
        + jd
        + ((jm - 1) * 31 if jm < 7 else ((jm - 7) * 30) + 186)
    )

    gy = 400 * (days // 146097)
    days %= 146097

    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1

    gy += 4 * (days // 1461)
    days %= 1461

    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365

    gd = days + 1

    is_leap = (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)

    sal_a = [
        0, 31,
        29 if is_leap else 28,
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ]

    gm = 0
    while gm < 13 and gd > sal_a[gm]:
        gd -= sal_a[gm]
        gm += 1

    return gy, gm, gd

def is_jalali_leap(jy):

    try:
        gy, gm, gd = jalali_to_gregorian(jy, 12, 30)
        jy2, jm2, jd2 = gregorian_to_jalali(gy, gm, gd)

        return (
            jy2 == jy
            and jm2 == 12
            and jd2 == 30
        )

    except Exception:
        return False

def jalali_month_days(jy, jm):

    if jm <= 6:
        return 31

    if jm <= 11:
        return 30

    if is_jalali_leap(jy):
        return 30

    return 29

WEEKDAY_NAMES = [
    "دوشنبه",
    "سه‌شنبه",
    "چهارشنبه",
    "پنج‌شنبه",
    "جمعه",
    "شنبه",
    "یک‌شنبه"
]

WEEKDAY_SHORT = [
    "ش", "ی", "د", "س", "چ", "پ", "ج"
]

MONTH_NAMES = [
    "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند"
]

def jalali_string(qdate):

    jy, jm, jd = gregorian_to_jalali(
        qdate.year(), qdate.month(), qdate.day()
    )

    return f"{jy:04d}/{jm:02d}/{jd:02d}"

def persian_date_long(qdate):

    jy, jm, jd = gregorian_to_jalali(
        qdate.year(), qdate.month(), qdate.day()
    )

    weekday = WEEKDAY_NAMES[qdate.dayOfWeek() - 1]

    return f"{weekday} {jd} {MONTH_NAMES[jm - 1]} {jy}"

# =========================================================
# PERSIAN CALENDAR POPUP
# =========================================================

class PersianCalendarPopup(QFrame):

    dateSelected = Signal(QDate)

    def __init__(self, parent=None, current_qdate=None):

        super().__init__(parent)

        if current_qdate is None:
            current_qdate = QDate.currentDate()

        self.selected_qdate = current_qdate

        jy, jm, jd = gregorian_to_jalali(
            current_qdate.year(),
            current_qdate.month(),
            current_qdate.day()
        )

        self.view_year = jy
        self.view_month = jm

        self.selected_jy = jy
        self.selected_jm = jm
        self.selected_jd = jd

        self.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedSize(290, 330)

        self.build_ui()
        self.refresh_grid()

    def build_ui(self):

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("persianCalendarCard")

        card.setStyleSheet("""
            QFrame#persianCalendarCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 18px;
            }
        """)

        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # =================================================
        # HEADER — فلش‌ها: راست > / چپ <
        # =================================================

        header = QHBoxLayout()
        header.setSpacing(6)

        # فلش راست (>) → ماه قبل
        prev_btn = QPushButton(">")
        prev_btn.setObjectName("calNavBtn")
        prev_btn.setFixedSize(30, 30)
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.clicked.connect(self.go_prev_month)

        self.month_label = QLabel()
        self.month_label.setObjectName("calMonthLabel")
        self.month_label.setAlignment(Qt.AlignCenter)

        # فلش چپ (<) → ماه بعد
        next_btn = QPushButton("<")
        next_btn.setObjectName("calNavBtn")
        next_btn.setFixedSize(30, 30)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.clicked.connect(self.go_next_month)

        header.addWidget(prev_btn)
        header.addWidget(self.month_label, 1)
        header.addWidget(next_btn)

        layout.addLayout(header)

        # =================================================
        # WEEKDAY ROW
        # =================================================

        wd_layout = QHBoxLayout()
        wd_layout.setSpacing(2)

        for name in WEEKDAY_SHORT:
            lbl = QLabel(name)
            lbl.setObjectName("calWeekday")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(24)
            wd_layout.addWidget(lbl, 1)

        layout.addLayout(wd_layout)

        # =================================================
        # DAYS GRID
        # =================================================

        self.days_layout = QGridLayout()
        self.days_layout.setSpacing(2)

        for col in range(7):
            self.days_layout.setColumnStretch(col, 1)

        layout.addLayout(self.days_layout, 1)

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet("""

            QLabel#calMonthLabel {
                color: #17324D;
                font-size: 13px;
                font-weight: 700;
                background: transparent;
            }

            QPushButton#calNavBtn {
                background-color: #EAF3FF;
                color: #1961C7;
                border: 1px solid #C9DDF5;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
                padding: 0px;
            }

            QPushButton#calNavBtn:hover {
                background-color: #D8E9FF;
                border-color: #AFCFF0;
            }

            QPushButton#calNavBtn:pressed {
                background-color: #C8DDF5;
            }

            QLabel#calWeekday {
                color: #8290A1;
                font-size: 10px;
                font-weight: 700;
                background: transparent;
            }

            QPushButton#calDayBtn {
                background-color: transparent;
                color: #17324D;
                border: none;
                border-radius: 8px;
                font-size: 11px;
                font-weight: 600;
                min-height: 28px;
            }

            QPushButton#calDayBtn:hover {
                background-color: #EAF3FF;
                color: #1961C7;
            }

            QPushButton#calDayBtn[today="true"] {
                border: 2px solid #1961C7;
                color: #1961C7;
            }

            QPushButton#calDayBtn[selected="true"] {
                background-color: #1961C7;
                color: white;
                border: none;
            }

        """)

    def refresh_grid(self):

        while self.days_layout.count():

            item = self.days_layout.takeAt(0)
            w = item.widget()

            if w:
                w.deleteLater()

        self.month_label.setText(
            f"{MONTH_NAMES[self.view_month - 1]} {self.view_year}"
        )

        days_in_month = jalali_month_days(
            self.view_year,
            self.view_month
        )

        gy, gm, gd = jalali_to_gregorian(
            self.view_year,
            self.view_month,
            1
        )

        first_qdate = QDate(gy, gm, gd)

        persian_weekday = (first_qdate.dayOfWeek() + 1) % 7

        today_qdate = QDate.currentDate()

        tjy, tjm, tjd = gregorian_to_jalali(
            today_qdate.year(),
            today_qdate.month(),
            today_qdate.day()
        )

        row = 0
        col = persian_weekday

        for day in range(1, days_in_month + 1):

            btn = QPushButton(str(day))
            btn.setObjectName("calDayBtn")
            btn.setCursor(Qt.PointingHandCursor)

            is_today = (
                self.view_year == tjy
                and self.view_month == tjm
                and day == tjd
            )

            is_selected = (
                self.view_year == self.selected_jy
                and self.view_month == self.selected_jm
                and day == self.selected_jd
            )

            btn.setProperty(
                "today",
                "true" if is_today else "false"
            )

            btn.setProperty(
                "selected",
                "true" if is_selected else "false"
            )

            btn.clicked.connect(
                lambda checked=False, d=day: self.pick_day(d)
            )

            self.days_layout.addWidget(btn, row, col)

            col += 1

            if col > 6:
                col = 0
                row += 1

    def go_prev_month(self):

        self.view_month -= 1

        if self.view_month < 1:
            self.view_month = 12
            self.view_year -= 1

        self.refresh_grid()

    def go_next_month(self):

        self.view_month += 1

        if self.view_month > 12:
            self.view_month = 1
            self.view_year += 1

        self.refresh_grid()

    def pick_day(self, day):

        self.selected_jy = self.view_year
        self.selected_jm = self.view_month
        self.selected_jd = day

        gy, gm, gd = jalali_to_gregorian(
            self.selected_jy,
            self.selected_jm,
            self.selected_jd
        )

        self.selected_qdate = QDate(gy, gm, gd)

        self.dateSelected.emit(self.selected_qdate)

        self.close()

# =========================================================
# PERSIAN DATE BUTTON — قاب واحد
# =========================================================

class PersianDateButton(QFrame):

    dateChanged = Signal(QDate)

    def __init__(self, parent=None):

        super().__init__(parent)

        self._qdate = QDate.currentDate()

        self.setObjectName("persianDateFrame")
        self.setFixedHeight(42)
        self.setMinimumWidth(220)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 14, 0)
        layout.setSpacing(8)

        # آیکون تقویم — داخل قاب
        self.icon_label = QLabel("📅")
        self.icon_label.setObjectName("dateIconLabel")
        self.icon_label.setFixedSize(30, 30)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # دکمه تاریخ — بدون border
        self.date_btn = QPushButton()
        self.date_btn.setObjectName("persianDateButton")
        self.date_btn.setCursor(Qt.PointingHandCursor)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.date_btn, 1)

        self._refresh_text()

        # کلیک روی هر جای قاب → تقویم باز بشه
        self.mousePressEvent = self._frame_clicked
        self.date_btn.clicked.connect(self._open_dialog)

    def _frame_clicked(self, event):
        self._open_dialog()
        event.accept()

    def _refresh_text(self):

        jy, jm, jd = gregorian_to_jalali(
            self._qdate.year(),
            self._qdate.month(),
            self._qdate.day()
        )

        self.date_btn.setText(
            f"{jy:04d} / {jm:02d} / {jd:02d}"
        )

    def date(self):
        return self._qdate

    def setDate(self, qdate):
        self._qdate = qdate
        self._refresh_text()

    def _open_dialog(self):

        self._popup = PersianCalendarPopup(
            self,
            self._qdate
        )

        self._popup.dateSelected.connect(
            self._on_date_selected
        )

        global_pos = self.mapToGlobal(
            QPoint(0, self.height() + 4)
        )

        self._popup.move(global_pos)
        self._popup.show()

    def _on_date_selected(self, qdate):

        if qdate == self._qdate:
            return

        self._qdate = qdate
        self._refresh_text()
        self.dateChanged.emit(self._qdate)

# =========================================================
# NICE MESSAGE BOX
# =========================================================

class NiceMessageDialog(QDialog):

    def __init__(self, parent, title, text, kind="info"):

        super().__init__(parent)

        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedSize(380, 260)

        if kind == "success":
            icon_char = "✓"
            color = "#16A34A"
            bg = "#DCFCE7"
        elif kind == "error":
            icon_char = "✕"
            color = "#D93025"
            bg = "#FEE2E2"
        elif kind == "warning":
            icon_char = "!"
            color = "#F59E0B"
            bg = "#FEF3C7"
        else:
            icon_char = "i"
            color = "#1961C7"
            bg = "#DBEAFE"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("niceMsgCard")
        card.setStyleSheet("""
            QFrame#niceMsgCard {
                background-color: #FFFFFF;
                border-radius: 22px;
                border: 1px solid #E2EAF4;
            }
        """)

        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)

        icon_label = QLabel(icon_char)
        icon_label.setFixedSize(56, 56)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border-radius: 28px;
                font-size: 26px;
                font-weight: 700;
            }}
        """)

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()

        layout.addLayout(icon_row)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #1E2F43;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
                border: none;
            }
        """)

        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            QLabel {
                color: #526273;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)

        layout.addWidget(text_label)
        layout.addStretch()

        btn = QPushButton("تأیید")
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(120)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                padding: 0px 24px;
            }}
        """)

        btn.clicked.connect(self.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

class NiceMessageBox:

    @staticmethod
    def info(parent, title, text):
        NiceMessageDialog(parent, title, text, "info").exec()

    @staticmethod
    def success(parent, title, text):
        NiceMessageDialog(parent, title, text, "success").exec()

    @staticmethod
    def error(parent, title, text):
        NiceMessageDialog(parent, title, text, "error").exec()

    @staticmethod
    def warning(parent, title, text):
        NiceMessageDialog(parent, title, text, "warning").exec()

# =========================================================
# ATTENDANCE WINDOW
# =========================================================

class AttendanceWindow(QWidget):

    def __init__(self, phone_number, complex_id=None):

        super().__init__()

        self.phone_number = phone_number
        self.preselect_complex_id = complex_id

        self.db = Database()

        self.user_id = None
        self.member_id = None
        self.role = None
        self.complex_id = None
        self.complexes = []

        self.work_start = QTime(8, 0, 0)
        self.work_end = QTime(16, 0, 0)

        self.entry_time = None
        self.exit_time = None

        self.setWindowTitle("حضور و غیاب")
        self.resize(1000, 700)
        self.setMinimumSize(600, 500)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("attendanceWindow")

        self.load_user_data()
        self.setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    # =====================================================
    # LOAD USER DATA
    # =====================================================

    def load_user_data(self):

        try:

            user = self.db.fetch_one(
                """
                SELECT userId
                FROM users
                WHERE phoneNumber = %s
                LIMIT 1
                """,
                (self.phone_number,)
            )

            if not user:
                return

            self.user_id = user["userId"]

            rows = self.db.fetch_all(
                """
                SELECT
                    c.complexId,
                    c.name,
                    cm.memberId,
                    cm.role,
                    ep.workStartTime,
                    ep.workEndTime
                FROM complexes c
                INNER JOIN complex_members cm
                    ON cm.complexId = c.complexId
                LEFT JOIN employee_profiles ep
                    ON ep.memberId = cm.memberId
                WHERE cm.userId = %s
                  AND cm.isActive = '1'
                  AND c.isActive = '1'
                ORDER BY c.complexId ASC
                """,
                (self.user_id,)
            )

            self.complexes = rows or []

            if self.complexes:

                chosen = None

                if self.preselect_complex_id:
                    for c in self.complexes:
                        if c["complexId"] == self.preselect_complex_id:
                            chosen = c
                            break

                if not chosen:
                    chosen = self.complexes[0]

                self.set_active_complex(chosen)

        except Exception as e:
            print("LOAD USER DATA ERROR:", e)

    def set_active_complex(self, complex_row):

        self.complex_id = complex_row["complexId"]
        self.member_id = complex_row["memberId"]
        self.role = complex_row["role"]

        st = complex_row.get("workStartTime")
        et = complex_row.get("workEndTime")

        if st:
            try:
                if isinstance(st, str):
                    parts = st.split(":")
                    self.work_start = QTime(int(parts[0]), int(parts[1]), 0)
                else:
                    self.work_start = QTime(
                        st.seconds // 3600,
                        (st.seconds % 3600) // 60,
                        0
                    )
            except Exception:
                pass

        if et:
            try:
                if isinstance(et, str):
                    parts = et.split(":")
                    self.work_end = QTime(int(parts[0]), int(parts[1]), 0)
                else:
                    self.work_end = QTime(
                        et.seconds // 3600,
                        (et.seconds % 3600) // 60,
                        0
                    )
            except Exception:
                pass

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 15, 22, 15)
        main_layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(7)

        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(1)

        title = QLabel("حضور و غیاب")
        title.setStyleSheet("""
            font-size: 21px;
            font-weight: 700;
            color: #17324D;
        """)

        subtitle = QLabel("مدیریت ورود، خروج و ساعات کاری")
        subtitle.setStyleSheet("""
            font-size: 10px;
            color: #7890A8;
        """)

        title_text_layout.addWidget(title)
        title_text_layout.addWidget(subtitle)

        back_button = QPushButton("›")
        back_button.setFixedSize(36, 36)
        back_button.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                color: #1961C7;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #EAF3FF;
            }
        """)
        back_button.clicked.connect(self.close)

        title_layout.setDirection(QBoxLayout.LeftToRight)
        title_layout.addWidget(back_button)
        title_layout.addLayout(title_text_layout)

        header.addLayout(title_layout)
        header.addStretch()

        if len(self.complexes) > 1:

            self.complex_combo = QComboBox()
            self.complex_combo.setFixedHeight(36)
            self.complex_combo.setMinimumWidth(180)
            self.complex_combo.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    border: 1px solid #E2EAF4;
                    border-radius: 12px;
                    padding: 0 14px;
                    padding-left: 32px;
                    color: #17324D;
                    font-size: 12px;
                }
                QComboBox:focus {
                    border: 2px solid #4589E8;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: center left;
                    width: 28px;
                    border: none;
                    background: transparent;
                }
                QComboBox::down-arrow {
                    image: none;
                    width: 0px;
                    height: 0px;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 6px solid #4589E8;
                    margin-left: 10px;
                }
            """)

            for c in self.complexes:
                self.complex_combo.addItem(c["name"], c["complexId"])

            for i, c in enumerate(self.complexes):
                if c["complexId"] == self.complex_id:
                    self.complex_combo.setCurrentIndex(i)
                    break

            self.complex_combo.currentIndexChanged.connect(
                self.on_complex_changed
            )

            header.addWidget(self.complex_combo)

        main_layout.addLayout(header)

        # =================================================
        # TABS
        # =================================================

        self.is_owner = self.role in ("owner", "both")

        if self.is_owner:

            tabs = QHBoxLayout()
            tabs.setSpacing(6)

            self.my_tab_btn = QPushButton("حضور من")
            self.my_tab_btn.setObjectName("tabButton")
            self.my_tab_btn.setFixedHeight(40)
            self.my_tab_btn.setCursor(Qt.PointingHandCursor)
            self.my_tab_btn.clicked.connect(lambda: self.switch_tab(0))

            self.emp_tab_btn = QPushButton("حضور کارمندان")
            self.emp_tab_btn.setObjectName("tabButton")
            self.emp_tab_btn.setFixedHeight(40)
            self.emp_tab_btn.setCursor(Qt.PointingHandCursor)
            self.emp_tab_btn.clicked.connect(lambda: self.switch_tab(1))

            tabs.addWidget(self.my_tab_btn)
            tabs.addWidget(self.emp_tab_btn)
            tabs.addStretch()

            main_layout.addLayout(tabs)

            self.stack = QStackedWidget()
            self.stack.addWidget(self.build_my_attendance_tab())
            self.stack.addWidget(self.build_employees_tab())

            main_layout.addWidget(self.stack, 1)

            self.switch_tab(0)

        else:

            self.stack = QStackedWidget()
            self.stack.addWidget(self.build_my_attendance_tab())

            main_layout.addWidget(self.stack, 1)

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet("""

            QWidget#attendanceWindow {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
                color: #25364A;
            }

            QLabel {
                color: #18324D;
                background: transparent;
            }

            QPushButton#tabButton {
                background-color: #FFFFFF;
                color: #526273;
                border: 1px solid #E2EAF4;
                border-radius: 14px;
                padding: 0 24px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#tabButton:hover {
                background-color: #F0F5FC;
            }

            QPushButton#tabButton[selected="true"] {
                background-color: #1961C7;
                color: white;
                border: 1px solid #1961C7;
            }

            QFrame#todayCard {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 24px;
            }

            QLabel#todayTime {
                color: #1961C7;
                font-size: 48px;
                font-weight: 800;
                background: transparent;
            }

            QLabel#todayDate {
                color: #17324D;
                font-size: 15px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#todayStatus {
                color: #526273;
                font-size: 12px;
                background: transparent;
            }

            QPushButton#checkInButton {
                background-color: #16A34A;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0 40px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton#checkInButton:hover {
                background-color: #15803D;
            }
            QPushButton#checkInButton:disabled {
                background-color: #B8C9DD;
            }

            QPushButton#checkOutButton {
                background-color: #D93025;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0 40px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton#checkOutButton:hover {
                background-color: #B71C1C;
            }
            QPushButton#checkOutButton:disabled {
                background-color: #B8C9DD;
            }

            QLabel#sectionTitle {
                color: #17324D;
                font-size: 15px;
                font-weight: 700;
                background: transparent;
            }

            QFrame#historyCard {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }
            QFrame#historyCard:hover {
                border-color: #C9DDF5;
                background-color: #FAFCFF;
            }

            QLabel#historyDate {
                color: #17324D;
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#historyTime {
                color: #607D96;
                font-size: 11px;
                background: transparent;
            }

            QLabel#historyHours {
                color: #1961C7;
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#approvedBadge {
                color: #21844A;
                background-color: #EAF6EE;
                border: none;
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: 700;
            }

            QLabel#pendingBadge {
                color: #B87900;
                background-color: #FFF4DD;
                border: none;
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: 700;
            }

            QLabel#rejectedBadge {
                color: #C43D4B;
                background-color: #FDEBEC;
                border: none;
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: 700;
            }

            QFrame#filterBox {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }

            /* ==========================================
               DATE BUTTON — قاب واحد
               ========================================== */

            QFrame#persianDateFrame {
                background-color: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
            }

            QFrame#persianDateFrame:hover {
                background-color: #FFFFFF;
                border: 1px solid #C9DDF5;
            }

            QLabel#dateIconLabel {
                background-color: #EAF3FF;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
            }

            QPushButton#persianDateButton {
                background-color: transparent;
                border: none;
                padding: 0 4px;
                color: #17324D;
                font-size: 12px;
                font-weight: 700;
                text-align: center;
            }

            QPushButton#persianDateButton:hover {
                color: #1961C7;
            }

            QPushButton#persianDateButton:pressed {
                color: #1453AA;
            }

            QPushButton#refreshButton {
                background-color: #EAF3FF;
                color: #1961C7;
                border: 1px solid #C9DDF5;
                border-radius: 14px;
                padding: 0 20px;
                font-size: 12px;
                font-weight: 600;
                min-height: 42px;
            }
            QPushButton#refreshButton:hover {
                background-color: #D8E9FF;
            }

            QPushButton#editButton {
                background-color: #F1F6FD;
                color: #1961C7;
                border: none;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton#editButton:hover {
                background-color: #D8E9FF;
            }

            QPushButton#approveButton {
                background-color: #DCFCE7;
                color: #16A34A;
                border: none;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#approveButton:hover {
                background-color: #BBF7D0;
            }

            QPushButton#rejectButton {
                background-color: #FEE2E2;
                color: #D93025;
                border: none;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#rejectButton:hover {
                background-color: #FBD5D5;
            }

            QPushButton#saveButton {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 6px 16px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#saveButton:hover {
                background-color: #4589E8;
            }

            QFrame#emptyCard {
                background-color: white;
                border: 1px dashed #DCE6F2;
                border-radius: 20px;
            }
            QLabel#emptyText {
                color: #8290A1;
                font-size: 12px;
                background: transparent;
            }

            QScrollArea {
                background: transparent;
                border: none;
                border-radius: 16px;
            }
            QScrollArea > QWidget {
                background: transparent;
                border-radius: 16px;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
                border-radius: 16px;
            }

            QScrollBar:vertical {
                width: 10px;
                background: #E8EEF6;
                border: none;
                border-radius: 5px;
                margin: 4px 2px;
            }
            QScrollBar::handle:vertical {
                background: #4589E8;
                border: none;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #1961C7;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
                border: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
            }

            QScrollBar:horizontal {
                height: 0px;
                background: transparent;
            }

        """)

    # =====================================================
    # SWITCH TAB
    # =====================================================

    def switch_tab(self, index):

        if not self.is_owner:
            return

        self.stack.setCurrentIndex(index)

        for i, btn in enumerate([self.my_tab_btn, self.emp_tab_btn]):
            btn.setProperty("selected", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

        if index == 0:
            self.refresh_my_attendance()
        else:
            self.refresh_employees_attendance()

    def on_complex_changed(self, index):

        if index < 0 or index >= len(self.complexes):
            return

        self.set_active_complex(self.complexes[index])
        self.refresh_my_attendance()

        if self.is_owner:
            self.refresh_employees_attendance()

    # =====================================================
    # TAB 1: MY ATTENDANCE
    # =====================================================

    def build_my_attendance_tab(self):

        widget = QWidget()
        widget.setObjectName("myAttendanceTab")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        today_card = QFrame()
        today_card.setObjectName("todayCard")
        today_card.setMinimumHeight(280)

        today_layout = QVBoxLayout(today_card)
        today_layout.setContentsMargins(16, 14, 16, 14)
        today_layout.setSpacing(9)

        self.today_date_label = QLabel("—")
        self.today_date_label.setObjectName("todayDate")
        self.today_date_label.setAlignment(Qt.AlignCenter)

        today_layout.addWidget(self.today_date_label)

        self.clock_label = QLabel("--:--:--")
        self.clock_label.setObjectName("todayTime")
        self.clock_label.setAlignment(Qt.AlignCenter)

        today_layout.addWidget(self.clock_label)

        self.today_status_label = QLabel("—")
        self.today_status_label.setObjectName("todayStatus")
        self.today_status_label.setAlignment(Qt.AlignCenter)
        self.today_status_label.setWordWrap(True)

        today_layout.addWidget(self.today_status_label)

        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)

        self.entry_box = self.create_time_box("ورود")
        self.exit_box = self.create_time_box("خروج")
        self.work_box = self.create_time_box("مدت کار")

        info_layout.addWidget(self.entry_box)
        info_layout.addWidget(self.exit_box)
        info_layout.addWidget(self.work_box)

        today_layout.addLayout(info_layout)

        calc_layout = QHBoxLayout()
        calc_layout.setSpacing(8)

        self.delay_box = self.create_small_box("تأخیر", "۰ دقیقه")
        self.overtime_box = self.create_small_box("اضافه‌کاری", "۰ دقیقه")
        self.remaining_box = self.create_small_box("باقی‌مانده", "—")

        calc_layout.addWidget(self.delay_box)
        calc_layout.addWidget(self.overtime_box)
        calc_layout.addWidget(self.remaining_box)

        today_layout.addLayout(calc_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.entry_button = QPushButton("ثبت ورود")
        self.entry_button.setObjectName("checkInButton")
        self.entry_button.setFixedHeight(44)
        self.entry_button.setCursor(Qt.PointingHandCursor)
        self.entry_button.clicked.connect(self.register_entry)

        self.exit_button = QPushButton("ثبت خروج")
        self.exit_button.setObjectName("checkOutButton")
        self.exit_button.setFixedHeight(44)
        self.exit_button.setCursor(Qt.PointingHandCursor)
        self.exit_button.clicked.connect(self.register_exit)

        buttons_layout.addWidget(self.entry_button)
        buttons_layout.addWidget(self.exit_button)

        today_layout.addLayout(buttons_layout)

        layout.addWidget(today_card)

        history_title = QLabel("سوابق حضور و غیاب")
        history_title.setObjectName("sectionTitle")

        layout.addWidget(history_title)

        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setFrameShape(QFrame.NoFrame)
        history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        history_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        history_content = QWidget()
        history_content.setObjectName("historyContent")

        self.my_history_layout = QVBoxLayout(history_content)
        self.my_history_layout.setContentsMargins(4, 4, 16, 4)
        self.my_history_layout.setSpacing(8)

        history_scroll.setWidget(history_content)

        layout.addWidget(history_scroll, 1)

        return widget

    # =====================================================
    # TAB 2: EMPLOYEES ATTENDANCE
    # =====================================================

    def build_employees_tab(self):

        widget = QWidget()
        widget.setObjectName("employeesAttendanceTab")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        filter_box = QFrame()
        filter_box.setObjectName("filterBox")

        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(10)

        date_label = QLabel("تاریخ:")
        date_label.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        # فیلد تاریخ شمسی — قاب واحد
        self.date_filter = PersianDateButton()

        self.date_filter.dateChanged.connect(
            self.refresh_employees_attendance
        )

        refresh_button = QPushButton("🔄  بروزرسانی")
        refresh_button.setObjectName("refreshButton")
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.clicked.connect(
            self.refresh_employees_attendance
        )

        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(refresh_button)

        layout.addWidget(filter_box)

        emp_scroll = QScrollArea()
        emp_scroll.setWidgetResizable(True)
        emp_scroll.setFrameShape(QFrame.NoFrame)
        emp_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        emp_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        emp_content = QWidget()
        emp_content.setObjectName("empContent")

        self.emp_list_layout = QVBoxLayout(emp_content)
        self.emp_list_layout.setContentsMargins(4, 4, 16, 4)
        self.emp_list_layout.setSpacing(8)

        emp_scroll.setWidget(emp_content)

        layout.addWidget(emp_scroll, 1)

        return widget

    # =====================================================
    # TIME BOX / SMALL BOX
    # =====================================================

    def create_time_box(self, title_text):

        box = QFrame()
        box.setObjectName("timeBox")
        box.setFixedHeight(72)

        box.setStyleSheet("""
            QFrame#timeBox {
                background: #F5F8FC;
                border: 1px solid #E8EEF5;
                border-radius: 36px;
            }
        """)

        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(3)

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(22)
        title.setStyleSheet("""
            QLabel {
                color: #7890A8;
                font-size: 9px;
                background: #FFFFFF;
                border: none;
                border-radius: 11px;
                padding: 0px 12px;
            }
        """)

        value = QLabel("—")
        value.setObjectName("time_value")
        value.setAlignment(Qt.AlignCenter)
        value.setFixedHeight(30)
        value.setStyleSheet("""
            QLabel {
                color: #17324D;
                font-size: 15px;
                font-weight: 700;
                background: #FFFFFF;
                border: none;
                border-radius: 15px;
                padding: 0px 12px;
            }
        """)

        layout.addWidget(title, 0, Qt.AlignCenter)
        layout.addWidget(value, 0, Qt.AlignCenter)

        return box

    def create_small_box(self, title_text, value_text):

        box = QFrame()
        box.setObjectName("smallBox")
        box.setFixedHeight(62)

        box.setStyleSheet("""
            QFrame#smallBox {
                background: #F8FAFD;
                border: 1px solid #E8EEF5;
                border-radius: 31px;
            }
        """)

        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(21)
        title.setStyleSheet("""
            QLabel {
                color: #7890A8;
                font-size: 9px;
                background: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 0px 11px;
            }
        """)

        value = QLabel(value_text)
        value.setObjectName("small_value")
        value.setAlignment(Qt.AlignCenter)
        value.setFixedHeight(26)
        value.setStyleSheet("""
            QLabel {
                color: #1961C7;
                font-size: 11px;
                font-weight: 700;
                background: #FFFFFF;
                border: none;
                border-radius: 13px;
                padding: 0px 10px;
            }
        """)

        layout.addWidget(title, 0, Qt.AlignCenter)
        layout.addWidget(value, 0, Qt.AlignCenter)

        return box

    # =====================================================
    # CLOCK
    # =====================================================

    def update_clock(self):

        now = QTime.currentTime()
        self.clock_label.setText(now.toString("HH:mm:ss"))

        if self.entry_time and not self.exit_time:
            self.update_live_calculations()

    def current_minute_time(self):

        now = QTime.currentTime()
        return QTime(now.hour(), now.minute(), 0)

    # =====================================================
    # REFRESH MY ATTENDANCE
    # =====================================================

    def refresh_my_attendance(self):

        if not self.member_id:
            return

        today = QDate.currentDate()
        self.today_date_label.setText(persian_date_long(today))

        today_str = today.toString("yyyy-MM-dd")

        record = self.db.fetch_one(
            """
            SELECT
                attendanceId,
                checkIn,
                checkOut,
                workedMinutes,
                overtimeMinutes,
                status,
                approvalStatus
            FROM attendance
            WHERE memberId = %s
              AND workDate = %s
            LIMIT 1
            """,
            (self.member_id, today_str)
        )

        self.entry_box.findChild(QLabel, "time_value").setText("—")
        self.exit_box.findChild(QLabel, "time_value").setText("—")
        self.work_box.findChild(QLabel, "time_value").setText("—")

        self.entry_time = None
        self.exit_time = None

        if not record or not record["checkIn"]:

            self.entry_button.setEnabled(True)
            self.exit_button.setEnabled(False)

            self.today_status_label.setText("امروز هنوز ورودت رو ثبت نکردی")
            self.delay_box.findChild(QLabel, "small_value").setText("۰ دقیقه")
            self.overtime_box.findChild(QLabel, "small_value").setText("۰ دقیقه")
            self.remaining_box.findChild(QLabel, "small_value").setText("—")

        elif not record["checkOut"]:

            self.entry_button.setEnabled(False)
            self.exit_button.setEnabled(True)

            ci = record["checkIn"]

            if isinstance(ci, datetime):
                self.entry_time = QTime(ci.hour, ci.minute, 0)
                ci_text = ci.strftime("%H:%M")
            else:
                ci_text = str(ci)[:5]

            self.entry_box.findChild(QLabel, "time_value").setText(ci_text)
            self.today_status_label.setText(
                f"ورودت رو زدی. ساعت ورود: {ci_text}"
            )

        else:

            self.entry_button.setEnabled(False)
            self.exit_button.setEnabled(False)

            ci = record["checkIn"]
            co = record["checkOut"]

            if isinstance(ci, datetime):
                ci_text = ci.strftime("%H:%M")
            else:
                ci_text = str(ci)[:5]

            if isinstance(co, datetime):
                co_text = co.strftime("%H:%M")
            else:
                co_text = str(co)[:5]

            self.entry_box.findChild(QLabel, "time_value").setText(ci_text)
            self.exit_box.findChild(QLabel, "time_value").setText(co_text)

            wm = record["workedMinutes"] or 0
            h = wm // 60
            m = wm % 60

            self.work_box.findChild(QLabel, "time_value").setText(
                f"{h}س {m}د"
            )

            self.today_status_label.setText("امروزت کامل ثبت شده ✅")

            self.delay_box.findChild(QLabel, "small_value").setText("—")
            self.overtime_box.findChild(QLabel, "small_value").setText("—")
            self.remaining_box.findChild(QLabel, "small_value").setText("تکمیل")

        # ==========================================
        # HISTORY
        # ==========================================

        while self.my_history_layout.count():

            item = self.my_history_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        history = self.db.fetch_all(
            """
            SELECT
                workDate,
                checkIn,
                checkOut,
                workedMinutes,
                approvalStatus
            FROM attendance
            WHERE memberId = %s
            ORDER BY workDate DESC
            LIMIT 60
            """,
            (self.member_id,)
        )

        if not history:

            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setMinimumHeight(100)

            empty_layout = QVBoxLayout(empty)
            empty_layout.setContentsMargins(20, 30, 20, 30)

            empty_text = QLabel("هنوز سابقه‌ای نداری")
            empty_text.setObjectName("emptyText")
            empty_text.setAlignment(Qt.AlignCenter)

            empty_layout.addWidget(empty_text)

            self.my_history_layout.addWidget(empty)
            self.my_history_layout.addStretch()
            return

        for row in history:
            card = self.create_history_card(row)
            self.my_history_layout.addWidget(card)

        self.my_history_layout.addStretch()

    # =====================================================
    # CREATE HISTORY CARD
    # =====================================================

    def create_history_card(self, row):

        card = QFrame()
        card.setObjectName("historyCard")
        card.setMinimumHeight(60)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        work_date = row["workDate"]

        if isinstance(work_date, date):
            qdate = QDate(
                work_date.year,
                work_date.month,
                work_date.day
            )
            date_str = jalali_string(qdate)
        else:
            date_str = str(work_date)

        date_label = QLabel(date_str)
        date_label.setObjectName("historyDate")

        layout.addWidget(date_label, 2)

        ci = row["checkIn"]
        co = row["checkOut"]

        if isinstance(ci, datetime):
            ci_text = ci.strftime("%H:%M")
        elif ci:
            ci_text = str(ci)[:5]
        else:
            ci_text = "—"

        if isinstance(co, datetime):
            co_text = co.strftime("%H:%M")
        elif co:
            co_text = str(co)[:5]
        else:
            co_text = "—"

        in_label = QLabel(f"ورود: {ci_text}")
        in_label.setObjectName("historyTime")

        out_label = QLabel(f"خروج: {co_text}")
        out_label.setObjectName("historyTime")

        layout.addWidget(in_label, 1)
        layout.addWidget(out_label, 1)

        wm = row["workedMinutes"] or 0
        h = wm // 60
        m = wm % 60

        hours_label = QLabel(f"{h} ساعت و {m} دقیقه")
        hours_label.setObjectName("historyHours")

        layout.addWidget(hours_label, 1)

        approval = row.get("approvalStatus") or "pending"

        if approval == "approved":
            badge = QLabel("تأیید شده")
            badge.setObjectName("approvedBadge")
        elif approval == "rejected":
            badge = QLabel("رد شده")
            badge.setObjectName("rejectedBadge")
        else:
            badge = QLabel("در انتظار")
            badge.setObjectName("pendingBadge")

        badge.setAlignment(Qt.AlignCenter)

        layout.addWidget(badge)

        return card

    # =====================================================
    # REGISTER ENTRY / EXIT
    # =====================================================

    def register_entry(self):

        if not self.member_id:
            return

        today = QDate.currentDate()
        today_str = today.toString("yyyy-MM-dd")

        now = datetime.now()

        attendance_id = self.db.execute(
            """
            INSERT INTO attendance (
                memberId,
                workDate,
                checkIn,
                status,
                approvalStatus
            )
            VALUES (%s, %s, %s, 'present', 'pending')
            """,
            (self.member_id, today_str, now)
        )

        if not attendance_id:
            NiceMessageBox.error(self, "خطا", "ثبت ورود انجام نشد.")
            return

        NiceMessageBox.success(
            self, "ورود ثبت شد",
            f"ساعت {now.strftime('%H:%M')} به‌عنوان ورود ثبت شد."
        )

        self.refresh_my_attendance()

    def register_exit(self):

        if not self.member_id:
            return

        today = QDate.currentDate()
        today_str = today.toString("yyyy-MM-dd")

        record = self.db.fetch_one(
            """
            SELECT attendanceId, checkIn
            FROM attendance
            WHERE memberId = %s
              AND workDate = %s
            LIMIT 1
            """,
            (self.member_id, today_str)
        )

        if not record or not record["checkIn"]:
            NiceMessageBox.warning(
                self, "خطا",
                "اول باید ورودت رو ثبت کنی."
            )
            return

        now = datetime.now()
        ci = record["checkIn"]

        if isinstance(ci, datetime):
            delta = now - ci
            worked_minutes = int(delta.total_seconds() // 60)
        else:
            worked_minutes = 0

        self.db.execute(
            """
            UPDATE attendance
            SET checkOut = %s,
                workedMinutes = %s,
                approvalStatus = 'pending'
            WHERE attendanceId = %s
            """,
            (now, worked_minutes, record["attendanceId"])
        )

        h = worked_minutes // 60
        m = worked_minutes % 60

        NiceMessageBox.success(
            self, "خروج ثبت شد",
            f"مجموع کار امروز: {h} ساعت و {m} دقیقه."
        )

        self.refresh_my_attendance()

    # =====================================================
    # LIVE CALCULATIONS
    # =====================================================

    def update_live_calculations(self):

        if not self.entry_time:
            return

        current = self.current_minute_time()
        seconds = self.entry_time.secsTo(current)
        h = seconds // 3600
        m = (seconds % 3600) // 60

        self.work_box.findChild(QLabel, "time_value").setText(
            self.format_duration(h, m)
        )

        self.calculate_delay()
        self.calculate_overtime()

    def calculate_delay(self):

        if not self.entry_time:
            return

        delay_seconds = self.work_start.secsTo(self.entry_time)

        if delay_seconds <= 0:
            text = "۰ دقیقه"
        else:
            minutes = delay_seconds // 60
            hours = minutes // 60
            minutes = minutes % 60
            if hours > 0:
                text = f"{hours} ساعت و {minutes} دقیقه"
            else:
                text = f"{minutes} دقیقه"

        self.delay_box.findChild(QLabel, "small_value").setText(text)

    def calculate_overtime(self):

        if not self.entry_time:
            return

        current_time = self.current_minute_time()
        overtime_seconds = self.work_end.secsTo(current_time)

        if overtime_seconds <= 0:
            text = "۰ دقیقه"
        else:
            minutes = overtime_seconds // 60
            hours = minutes // 60
            minutes = minutes % 60
            if hours > 0:
                text = f"{hours} ساعت و {minutes} دقیقه"
            else:
                text = f"{minutes} دقیقه"

        self.overtime_box.findChild(QLabel, "small_value").setText(text)

    def format_duration(self, hours, minutes):

        if hours == 0:
            return f"{minutes} دقیقه"
        if minutes == 0:
            return f"{hours} ساعت"
        return f"{hours} ساعت و {minutes} دقیقه"

    # =====================================================
    # REFRESH EMPLOYEES ATTENDANCE
    # =====================================================

    def refresh_employees_attendance(self):

        if not self.is_owner or not self.complex_id:
            return

        while self.emp_list_layout.count():

            item = self.emp_list_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        selected_qdate = self.date_filter.date()
        selected_str = selected_qdate.toString("yyyy-MM-dd")

        rows = self.db.fetch_all(
            """
            SELECT
                cm.memberId,
                u.name,
                u.profession,
                u.phoneNumber,
                a.attendanceId,
                a.workDate,
                a.checkIn,
                a.checkOut,
                a.workedMinutes,
                a.approvalStatus,
                a.description
            FROM complex_members cm
            INNER JOIN users u ON u.userId = cm.userId
            LEFT JOIN attendance a
                ON a.memberId = cm.memberId
                AND a.workDate = %s
            WHERE cm.complexId = %s
              AND cm.role IN ('employee', 'both')
              AND cm.isActive = '1'
            ORDER BY u.name ASC
            """,
            (selected_str, self.complex_id)
        )

        if not rows:

            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setMinimumHeight(120)

            empty_layout = QVBoxLayout(empty)
            empty_layout.setContentsMargins(20, 30, 20, 30)

            empty_text = QLabel("کارمندی توی این مجموعه نیست")
            empty_text.setObjectName("emptyText")
            empty_text.setAlignment(Qt.AlignCenter)

            empty_layout.addWidget(empty_text)

            self.emp_list_layout.addWidget(empty)
            self.emp_list_layout.addStretch()
            return

        for row in rows:
            card = self.create_employee_attendance_card(row)
            self.emp_list_layout.addWidget(card)

        self.emp_list_layout.addStretch()

    # =====================================================
    # CREATE EMPLOYEE ATTENDANCE CARD
    # =====================================================

    def create_employee_attendance_card(self, row):

        card = QFrame()
        card.setObjectName("historyCard")
        card.setMinimumHeight(76)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(12)

        name_label = QLabel(row.get("name") or "بدون نام")
        name_label.setObjectName("historyDate")
        name_label.setMinimumWidth(140)

        layout.addWidget(name_label)

        ci = row.get("checkIn")
        co = row.get("checkOut")

        if isinstance(ci, datetime):
            ci_text = ci.strftime("%H:%M")
        elif ci:
            ci_text = str(ci)[:5]
        else:
            ci_text = "—"

        if isinstance(co, datetime):
            co_text = co.strftime("%H:%M")
        elif co:
            co_text = str(co)[:5]
        else:
            co_text = "—"

        time_label = QLabel(f"{ci_text}  تا  {co_text}")
        time_label.setObjectName("historyTime")

        layout.addWidget(time_label, 1)

        wm = row.get("workedMinutes") or 0
        h = wm // 60
        m = wm % 60

        hours_label = QLabel(f"{h}س {m}د")
        hours_label.setObjectName("historyHours")

        layout.addWidget(hours_label)

        approval = row.get("approvalStatus")

        if approval == "approved":
            badge = QLabel("تأیید شده")
            badge.setObjectName("approvedBadge")
        elif approval == "rejected":
            badge = QLabel("رد شده")
            badge.setObjectName("rejectedBadge")
        elif ci:
            badge = QLabel("در انتظار")
            badge.setObjectName("pendingBadge")
        else:
            badge = QLabel("غایب")
            badge.setObjectName("rejectedBadge")

        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(24)

        layout.addWidget(badge)

        if approval == "pending" and row.get("attendanceId"):

            approve_btn = QPushButton("✓ تأیید")
            approve_btn.setObjectName("approveButton")
            approve_btn.setCursor(Qt.PointingHandCursor)
            approve_btn.clicked.connect(
                lambda checked=False, r=row: self.approve_attendance(r)
            )

            reject_btn = QPushButton("✕ رد")
            reject_btn.setObjectName("rejectButton")
            reject_btn.setCursor(Qt.PointingHandCursor)
            reject_btn.clicked.connect(
                lambda checked=False, r=row: self.reject_attendance(r)
            )

            layout.addWidget(approve_btn)
            layout.addWidget(reject_btn)

        edit_button = QPushButton("ویرایش")
        edit_button.setObjectName("editButton")
        edit_button.setCursor(Qt.PointingHandCursor)
        edit_button.clicked.connect(
            lambda checked=False, r=row: self.open_edit_dialog(r)
        )

        layout.addWidget(edit_button)

        save_button = QPushButton("💾 ثبت")
        save_button.setObjectName("saveButton")
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.clicked.connect(
            lambda checked=False, r=row: self.save_attendance_row(r)
        )

        layout.addWidget(save_button)

        return card

    # =====================================================
    # SAVE ATTENDANCE ROW
    # =====================================================

    def save_attendance_row(self, row):

        attendance_id = row.get("attendanceId")
        approval = row.get("approvalStatus")

        if not attendance_id:
            NiceMessageBox.warning(
                self, "خطا",
                "برای این کارمند در این تاریخ رکوردی وجود ندارد."
            )
            return

        if approval == "approved":
            NiceMessageBox.info(
                self, "قبلاً تأیید شده",
                f"حضور {row.get('name', 'کارمند')} قبلاً تأیید شده است."
            )
            return

        result = self.db.execute(
            """
            UPDATE attendance
            SET approvalStatus = 'approved',
                approvedBy = %s,
                approvalDate = NOW()
            WHERE attendanceId = %s
            """,
            (self.user_id, attendance_id)
        )

        if result is None:
            NiceMessageBox.error(self, "خطا", "ثبت انجام نشد.")
            return

        NiceMessageBox.success(
            self, "ثبت شد",
            f"حضور {row.get('name', 'کارمند')} با موفقیت ثبت شد."
        )

        self.refresh_employees_attendance()

    # =====================================================
    # APPROVE / REJECT
    # =====================================================

    def approve_attendance(self, row):

        attendance_id = row.get("attendanceId")

        if not attendance_id:
            return

        result = self.db.execute(
            """
            UPDATE attendance
            SET approvalStatus = 'approved',
                approvedBy = %s,
                approvalDate = NOW()
            WHERE attendanceId = %s
            """,
            (self.user_id, attendance_id)
        )

        if result is None:
            NiceMessageBox.error(self, "خطا", "تأیید انجام نشد.")
            return

        self.refresh_employees_attendance()

        NiceMessageBox.success(
            self, "تأیید شد",
            f"حضور {row.get('name', 'کارمند')} تأیید شد."
        )

    def reject_attendance(self, row):

        attendance_id = row.get("attendanceId")

        if not attendance_id:
            return

        result = self.db.execute(
            """
            UPDATE attendance
            SET approvalStatus = 'rejected',
                approvedBy = %s,
                approvalDate = NOW()
            WHERE attendanceId = %s
            """,
            (self.user_id, attendance_id)
        )

        if result is None:
            NiceMessageBox.error(self, "خطا", "رد انجام نشد.")
            return

        self.refresh_employees_attendance()

        NiceMessageBox.warning(
            self, "رد شد",
            f"حضور {row.get('name', 'کارمند')} رد شد."
        )

    # =====================================================
    # EDIT DIALOG
    # =====================================================

    def open_edit_dialog(self, row):

        dialog = QDialog(self)
        dialog.setWindowTitle("ویرایش حضور")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(420)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(12)

        name = row.get("name") or "بدون نام"

        title = QLabel(f"ویرایش حضور — {name}")
        title.setStyleSheet("""
            color: #17324D;
            font-size: 15px;
            font-weight: 700;
            background: transparent;
        """)

        layout.addWidget(title)

        in_label = QLabel("ساعت ورود")
        in_label.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        in_time = QTimeEdit()
        in_time.setDisplayFormat("HH:mm")
        in_time.setFixedHeight(42)

        ci = row.get("checkIn")

        if isinstance(ci, datetime):
            in_time.setTime(QTime(ci.hour, ci.minute))
        else:
            in_time.setTime(QTime(8, 0))

        layout.addWidget(in_label)
        layout.addWidget(in_time)

        out_label = QLabel("ساعت خروج")
        out_label.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        out_time = QTimeEdit()
        out_time.setDisplayFormat("HH:mm")
        out_time.setFixedHeight(42)

        co = row.get("checkOut")

        if isinstance(co, datetime):
            out_time.setTime(QTime(co.hour, co.minute))
        else:
            out_time.setTime(QTime(17, 0))

        layout.addWidget(out_label)
        layout.addWidget(out_time)

        desc_label = QLabel("توضیحات")
        desc_label.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        desc_input = QLineEdit()
        desc_input.setFixedHeight(42)
        desc_input.setText(row.get("description") or "")
        desc_input.setPlaceholderText("اختیاری")

        layout.addWidget(desc_label)
        layout.addWidget(desc_input)

        layout.addSpacing(8)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setFixedHeight(42)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F8FC;
                color: #526273;
                border: 1px solid #E2EAF4;
                border-radius: 14px;
                padding: 0 22px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #EAF3FF;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = QPushButton("ذخیره")
        save_btn.setFixedHeight(42)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0 26px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #4589E8;
            }
        """)

        def on_save():

            attendance_id = row.get("attendanceId")

            selected_date = self.date_filter.date()
            selected_date_str = selected_date.toString("yyyy-MM-dd")

            new_in = in_time.time()
            new_out = out_time.time()

            in_dt = datetime(
                selected_date.year(),
                selected_date.month(),
                selected_date.day(),
                new_in.hour(),
                new_in.minute()
            )

            out_dt = datetime(
                selected_date.year(),
                selected_date.month(),
                selected_date.day(),
                new_out.hour(),
                new_out.minute()
            )

            delta = out_dt - in_dt
            worked = max(0, int(delta.total_seconds() // 60))

            if attendance_id:

                self.db.execute(
                    """
                    UPDATE attendance
                    SET checkIn = %s,
                        checkOut = %s,
                        workedMinutes = %s,
                        description = %s
                    WHERE attendanceId = %s
                    """,
                    (
                        in_dt,
                        out_dt,
                        worked,
                        desc_input.text().strip() or None,
                        attendance_id
                    )
                )

            else:

                self.db.execute(
                    """
                    INSERT INTO attendance (
                        memberId,
                        workDate,
                        checkIn,
                        checkOut,
                        workedMinutes,
                        status,
                        description,
                        approvalStatus
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        'present', %s, 'approved'
                    )
                    """,
                    (
                        row["memberId"],
                        selected_date_str,
                        in_dt,
                        out_dt,
                        worked,
                        desc_input.text().strip() or None
                    )
                )

            dialog.accept()
            self.refresh_employees_attendance()

            NiceMessageBox.success(
                self, "ذخیره شد",
                "تغییرات با موفقیت ذخیره شد."
            )

        save_btn.clicked.connect(on_save)

        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)

        layout.addLayout(buttons)

        dialog.setStyleSheet("""
            QDialog {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }
            QTimeEdit, QLineEdit {
                background-color: white;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                padding: 0 14px;
                color: #17324D;
                font-size: 13px;
            }
            QTimeEdit:focus, QLineEdit:focus {
                border: 2px solid #4589E8;
            }
            QTimeEdit::up-button,
            QTimeEdit::down-button {
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }
        """)

        dialog.exec()