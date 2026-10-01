import os
from datetime import datetime, date
from calendar import monthrange

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLineEdit,
    QTextEdit,
    QScrollArea,
    QScrollBar,
    QBoxLayout,
    QStackedWidget,
    QComboBox,
    QDialog
)

from PySide6.QtCore import Qt, QTimer, QDate, Signal, QPoint
from PySide6.QtGui import QPainter, QColor

from database import Database

# =========================================================
# ROUND SCROLL BAR — کاملاً گرد
# =========================================================

class RoundScrollBar(QScrollBar):

    def __init__(self, orientation=Qt.Vertical, parent=None):
        super().__init__(orientation, parent)

        self.setFixedWidth(12)

        self.setStyleSheet("""
            QScrollBar {
                background: transparent;
                border: none;
                margin: 0px;
            }
        """)

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track_width = 6

        track_x = (self.width() - track_width) / 2

        track_top = 6
        track_bottom = self.height() - 6

        track_height = track_bottom - track_top

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#EEF3FA"))

        painter.drawRoundedRect(
            int(track_x),
            int(track_top),
            track_width,
            int(track_height),
            track_width / 2,
            track_width / 2
        )

        minimum = self.minimum()
        maximum = self.maximum()
        page_step = self.pageStep()

        if maximum <= minimum:
            return

        groove_top = 6
        groove_bottom = self.height() - 6
        groove_height = groove_bottom - groove_top

        total_range = maximum - minimum + page_step

        handle_height = int(
            groove_height * page_step / total_range
        )

        handle_height = max(42, handle_height)
        handle_height = min(handle_height, groove_height)

        available_space = groove_height - handle_height

        if maximum == minimum:
            handle_y = groove_top
        else:
            value_ratio = (
                self.value() - minimum
            ) / (maximum - minimum)

            handle_y = (
                groove_top + available_space * value_ratio
            )

        handle_width = 8
        handle_x = (self.width() - handle_width) / 2

        painter.setBrush(QColor("#4589E8"))

        painter.drawRoundedRect(
            int(handle_x),
            int(handle_y),
            handle_width,
            int(handle_height),
            handle_width / 2,
            handle_width / 2
        )

# =========================================================
# JALALI HELPERS
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

def format_money(amount):

    try:
        return f"{amount:,.0f}"
    except Exception:
        return "0"

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
# PERSIAN MONTH PICKER POPUP
# =========================================================

class PersianMonthPopup(QFrame):

    monthSelected = Signal(int, int)

    def __init__(self, parent=None, current_year=None, current_month=None):

        super().__init__(parent)

        today = QDate.currentDate()
        jy, jm, jd = gregorian_to_jalali(
            today.year(), today.month(), today.day()
        )

        if current_year is None:
            current_year = jy
        if current_month is None:
            current_month = jm

        self.view_year = current_year
        self.selected_year = current_year
        self.selected_month = current_month

        self.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedSize(290, 290)

        self.build_ui()

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
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(6)

        prev_btn = QPushButton(">")
        prev_btn.setObjectName("calNavBtn")
        prev_btn.setFixedSize(30, 30)
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.clicked.connect(self.go_prev_year)

        self.year_label = QLabel()
        self.year_label.setObjectName("calMonthLabel")
        self.year_label.setAlignment(Qt.AlignCenter)

        next_btn = QPushButton("<")
        next_btn.setObjectName("calNavBtn")
        next_btn.setFixedSize(30, 30)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.clicked.connect(self.go_next_year)

        header.addWidget(prev_btn)
        header.addWidget(self.year_label, 1)
        header.addWidget(next_btn)

        layout.addLayout(header)

        grid = QGridLayout()
        grid.setSpacing(6)

        for idx, month_name in enumerate(MONTH_NAMES):

            r = idx // 3
            c = idx % 3

            btn = QPushButton(month_name)
            btn.setObjectName("monthBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(50)

            if idx + 1 == self.selected_month and self.view_year == self.selected_year:
                btn.setProperty("selected", "true")
            else:
                btn.setProperty("selected", "false")

            btn.clicked.connect(
                lambda checked=False, m=idx + 1: self.pick_month(m)
            )

            grid.addWidget(btn, r, c)

        layout.addLayout(grid, 1)

        self.setStyleSheet("""

            QLabel#calMonthLabel {
                color: #17324D;
                font-size: 14px;
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

            QPushButton#monthBtn {
                background-color: #F7F9FC;
                color: #17324D;
                border: 1px solid #DCE6F2;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#monthBtn:hover {
                background-color: #EAF3FF;
                color: #1961C7;
                border: 1px solid #C9DDF5;
            }

            QPushButton#monthBtn[selected="true"] {
                background-color: #1961C7;
                color: white;
                border: 1px solid #1961C7;
            }

        """)

        self.refresh_year_label()

    def refresh_year_label(self):
        self.year_label.setText(str(self.view_year))

    def go_prev_year(self):
        self.view_year -= 1
        self.refresh_year_label()

    def go_next_year(self):
        self.view_year += 1
        self.refresh_year_label()

    def pick_month(self, month):

        self.selected_year = self.view_year
        self.selected_month = month

        self.monthSelected.emit(
            self.selected_year,
            self.selected_month
        )

        self.close()

# =========================================================
# PERSIAN MONTH BUTTON
# =========================================================

class PersianMonthButton(QFrame):

    monthChanged = Signal(int, int)

    def __init__(self, parent=None):

        super().__init__(parent)

        today = QDate.currentDate()
        jy, jm, jd = gregorian_to_jalali(
            today.year(), today.month(), today.day()
        )

        self.year = jy
        self.month = jm

        self.setObjectName("persianDateFrame")
        self.setFixedHeight(42)
        self.setMinimumWidth(220)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 14, 0)
        layout.setSpacing(8)

        icon = QLabel("📅")
        icon.setObjectName("dateIconLabel")
        icon.setFixedSize(30, 30)
        icon.setAlignment(Qt.AlignCenter)

        self.month_btn = QPushButton()
        self.month_btn.setObjectName("persianDateButton")
        self.month_btn.setCursor(Qt.PointingHandCursor)

        layout.addWidget(icon)
        layout.addWidget(self.month_btn, 1)

        self._refresh_text()

        self.mousePressEvent = self._frame_clicked
        self.month_btn.clicked.connect(self._open_popup)

    def _frame_clicked(self, event):
        self._open_popup()
        event.accept()

    def _refresh_text(self):
        self.month_btn.setText(
            f"{MONTH_NAMES[self.month - 1]} {self.year}"
        )

    def _open_popup(self):

        self._popup = PersianMonthPopup(
            self,
            self.year,
            self.month
        )

        self._popup.monthSelected.connect(
            self._on_month_selected
        )

        global_pos = self.mapToGlobal(
            QPoint(0, self.height() + 4)
        )

        self._popup.move(global_pos)
        self._popup.show()

    def _on_month_selected(self, year, month):

        if year == self.year and month == self.month:
            return

        self.year = year
        self.month = month
        self._refresh_text()
        self.monthChanged.emit(year, month)

# =========================================================
# FINANCE WINDOW
# =========================================================

class FinanceWindow(QWidget):

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

        today = QDate.currentDate()
        jy, jm, jd = gregorian_to_jalali(
            today.year(), today.month(), today.day()
        )
        self.selected_year = jy
        self.selected_month = jm

        self.setWindowTitle("امور مالی")
        self.resize(1050, 720)
        self.setMinimumSize(700, 550)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("financeWindow")

        self.load_user_data()
        self.setup_ui()

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
                    cm.role
                FROM complexes c
                INNER JOIN complex_members cm
                    ON cm.complexId = c.complexId
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
            print("FINANCE LOAD USER DATA ERROR:", e)

    def set_active_complex(self, complex_row):

        self.complex_id = complex_row["complexId"]
        self.member_id = complex_row["memberId"]
        self.role = complex_row["role"]

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 15, 22, 15)
        main_layout.setSpacing(10)

        # HEADER
        header = QHBoxLayout()
        header.setSpacing(8)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(7)

        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(1)

        title = QLabel("امور مالی")
        title.setStyleSheet("""
            font-size: 21px;
            font-weight: 700;
            color: #17324D;
        """)

        subtitle = QLabel("مدیریت حقوق، پاداش، کسورات و پرداخت‌ها")
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

        # TABS
        self.is_owner = self.role in ("owner", "both")

        if self.is_owner:

            tabs = QHBoxLayout()
            tabs.setSpacing(6)

            self.tab_btns = []

            tab_names = [
                "خلاصه",
                "حقوق ماهانه",
                "پاداش",
                "کسورات",
                "تاریخچه"
            ]

            for i, name in enumerate(tab_names):

                btn = QPushButton(name)
                btn.setObjectName("tabButton")
                btn.setFixedHeight(40)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(
                    lambda checked=False, idx=i: self.switch_tab(idx)
                )

                tabs.addWidget(btn)
                self.tab_btns.append(btn)

            tabs.addStretch()

            main_layout.addLayout(tabs)

            self.stack = QStackedWidget()
            self.stack.addWidget(self.build_dashboard_tab())
            self.stack.addWidget(self.build_salaries_tab())
            self.stack.addWidget(self.build_bonuses_tab())
            self.stack.addWidget(self.build_deductions_tab())
            self.stack.addWidget(self.build_history_tab())

            main_layout.addWidget(self.stack, 1)

            self.switch_tab(0)

        else:

            self.stack = QStackedWidget()
            self.stack.addWidget(self.build_employee_history_tab())

            main_layout.addWidget(self.stack, 1)

            self.refresh_employee_history()

        # STYLE
        self.setStyleSheet("""

            QWidget#financeWindow {
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
                padding: 0 22px;
                font-size: 12px;
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

            QFrame#box {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QFrame#boxSub {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 22px;
            }

            QFrame#boxSub:hover {
                border-color: #C9DDF5;
                background-color: #FAFCFF;
            }

            QLabel#sectionTitle {
                color: #17324D;
                font-size: 14px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#statTitle {
                color: #8290A1;
                font-size: 11px;
                font-weight: 600;
                background: transparent;
            }

            QLabel#statValue {
                color: #1961C7;
                font-size: 18px;
                font-weight: 800;
                background: transparent;
            }

            QLabel#statValueGreen {
                color: #16A34A;
                font-size: 18px;
                font-weight: 800;
                background: transparent;
            }

            QLabel#statValueRed {
                color: #D93025;
                font-size: 18px;
                font-weight: 800;
                background: transparent;
            }

            QFrame#statBox {
                background-color: #F7F9FC;
                border: 1px solid #E8EEF5;
                border-radius: 20px;
            }

            QFrame#statBoxGreen {
                background-color: #EAF6EE;
                border: 1px solid #D1E9DB;
                border-radius: 20px;
            }

            QFrame#statBoxRed {
                background-color: #FDEBEC;
                border: 1px solid #F5D0D3;
                border-radius: 20px;
            }

            QLabel#empName {
                color: #17324D;
                font-size: 13px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#empInfo {
                color: #607D96;
                font-size: 10px;
                background: transparent;
            }

            QLabel#moneyLabel {
                color: #8290A1;
                font-size: 11px;
                font-weight: 600;
                background: transparent;
            }

            QLabel#moneyValue {
                color: #17324D;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#moneyValueGreen {
                color: #16A34A;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#moneyValueRed {
                color: #D93025;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#moneyValueBlue {
                color: #1961C7;
                font-size: 14px;
                font-weight: 800;
                background: transparent;
            }

            QLabel#badgePending {
                color: #B87900;
                background-color: #FFF4DD;
                border: none;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: 700;
            }

            QLabel#badgePaid {
                color: #21844A;
                background-color: #EAF6EE;
                border: none;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: 700;
            }

            QLabel#badgeDraft {
                color: #526273;
                background-color: #EEF2F6;
                border: none;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: 700;
            }

            QPushButton#actionBtn {
                background-color: #F1F6FD;
                color: #1961C7;
                border: none;
                border-radius: 14px;
                padding: 8px 18px;
                font-size: 11px;
                font-weight: 700;
            }

            QPushButton#actionBtn:hover {
                background-color: #D8E9FF;
            }

            QPushButton#payBtn {
                background-color: #DCFCE7;
                color: #16A34A;
                border: none;
                border-radius: 12px;
                padding: 4px 14px;
                font-size: 11px;
                font-weight: 700;
                min-height: 24px;
            }

            QPushButton#payBtn:hover {
                background-color: #BBF7D0;
            }

            QPushButton#primaryBtn {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: 700;
            }

            QPushButton#primaryBtn:hover {
                background-color: #4589E8;
            }

            QPushButton#primaryBtn:pressed {
                background-color: #1453AA;
            }

            QPushButton#secondaryBtn {
                background-color: #EAF3FF;
                color: #1961C7;
                border: 1px solid #C9DDF5;
                border-radius: 14px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: 700;
            }

            QPushButton#secondaryBtn:hover {
                background-color: #D8E9FF;
            }

            QLabel#dateIconLabel {
                background-color: #EAF3FF;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
            }

            QFrame#persianDateFrame {
                background-color: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
            }

            QFrame#persianDateFrame:hover {
                background-color: #FFFFFF;
                border: 1px solid #C9DDF5;
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

            QFrame#emptyCard {
                background-color: white;
                border: 1px dashed #DCE6F2;
                border-radius: 22px;
            }

            QLabel#emptyText {
                color: #8290A1;
                font-size: 12px;
                background: transparent;
            }

            /* ==========================================
               SCROLL — کاملاً گرد
               ========================================== */

            QScrollArea#financeScroll {
                background: transparent;
                border: none;
                border-radius: 28px;
            }

            QScrollArea#financeScroll > QWidget {
                background: transparent;
                border-radius: 28px;
            }

            QScrollArea#financeScroll > QWidget > QWidget {
                background: transparent;
                border-radius: 28px;
            }

            QScrollArea#financeScroll::viewport {
                background: transparent;
                border: none;
                border-radius: 28px;
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

            QLineEdit#formInput,
            QTextEdit#formInput {
                background-color: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                padding: 0 16px;
                color: #17324D;
                font-size: 13px;
            }

            QLineEdit#formInput {
                min-height: 42px;
            }

            QLineEdit#formInput:focus,
            QTextEdit#formInput:focus {
                background: #FFFFFF;
                border: 2px solid #4589E8;
            }

        """)

    # =====================================================
    # HELPER — ساخت اسکرول گرد
    # =====================================================    def make_rounded_scroll(self, content_widget):

        scroll = QScrollArea()
        scroll.setObjectName("financeScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea#financeScroll {
                background: transparent;
                border: none;
                border-radius: 28px;
            }
            QScrollArea#financeScroll::viewport {
                background: transparent;
                border: none;
                border-radius: 28px;
            }
        """)

        # نوار اسکرول گرد سفارشی
        vbar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(vbar)

        scroll.setWidget(content_widget)

        return scroll

    # =====================================================
    # TAB SWITCH
    # =====================================================

    def switch_tab(self, index):

        self.stack.setCurrentIndex(index)

        for i, btn in enumerate(self.tab_btns):
            btn.setProperty("selected", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

        if index == 0:
            self.refresh_dashboard()
        elif index == 1:
            self.refresh_salaries()
        elif index == 2:
            self.refresh_bonuses()
        elif index == 3:
            self.refresh_deductions()
        elif index == 4:
            self.refresh_history()

    def on_complex_changed(self, index):

        if index < 0 or index >= len(self.complexes):
            return

        self.set_active_complex(self.complexes[index])

        if self.is_owner:
            self.switch_tab(self.stack.currentIndex())
        else:
            self.refresh_employee_history()

    # =====================================================
    # TAB 1: DASHBOARD
    # =====================================================

    def build_dashboard_tab(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        month_box = QFrame()
        month_box.setObjectName("box")
        month_box.setAttribute(Qt.WA_StyledBackground, True)

        mb_layout = QHBoxLayout(month_box)
        mb_layout.setContentsMargins(20, 14, 20, 14)
        mb_layout.setSpacing(12)

        month_lbl = QLabel("ماه:")
        month_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        self.dashboard_month_btn = PersianMonthButton()
        self.dashboard_month_btn.monthChanged.connect(
            self.on_dashboard_month_changed
        )

        mb_layout.addWidget(month_lbl)
        mb_layout.addWidget(self.dashboard_month_btn)
        mb_layout.addStretch()

        layout.addWidget(month_box)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        self.dash_total_box = self.create_stat_box(
            "کل حقوق این ماه",
            "0",
            "statBox"
        )

        self.dash_paid_box = self.create_stat_box(
            "پرداخت‌شده",
            "0",
            "statBoxGreen"
        )

        self.dash_remain_box = self.create_stat_box(
            "مانده",
            "0",
            "statBoxRed"
        )

        self.dash_emp_box = self.create_stat_box(
            "تعداد کارمندان",
            "0",
            "statBox"
        )

        stats_row.addWidget(self.dash_total_box)
        stats_row.addWidget(self.dash_paid_box)
        stats_row.addWidget(self.dash_remain_box)
        stats_row.addWidget(self.dash_emp_box)

        layout.addLayout(stats_row)

        layout.addStretch()

        return widget

    def create_stat_box(self, title, value, box_name):

        box = QFrame()
        box.setObjectName(box_name)
        box.setAttribute(Qt.WA_StyledBackground, True)
        box.setMinimumHeight(100)

        layout = QVBoxLayout(box)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        value_label = QLabel(value)

        if box_name == "statBoxGreen":
            value_label.setObjectName("statValueGreen")
        elif box_name == "statBoxRed":
            value_label.setObjectName("statValueRed")
        else:
            value_label.setObjectName("statValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return box

    def on_dashboard_month_changed(self, year, month):

        self.selected_year = year
        self.selected_month = month
        self.refresh_dashboard()

    # =====================================================
    # TAB 2: SALARIES
    # =====================================================

    def build_salaries_tab(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        top_box = QFrame()
        top_box.setObjectName("box")
        top_box.setAttribute(Qt.WA_StyledBackground, True)

        top_layout = QHBoxLayout(top_box)
        top_layout.setContentsMargins(20, 14, 20, 14)
        top_layout.setSpacing(12)

        month_lbl = QLabel("ماه:")
        month_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        self.salary_month_btn = PersianMonthButton()
        self.salary_month_btn.monthChanged.connect(
            self.on_salary_month_changed
        )

        calc_btn = QPushButton("🧮  محاسبه حقوق این ماه")
        calc_btn.setObjectName("primaryBtn")
        calc_btn.setCursor(Qt.PointingHandCursor)
        calc_btn.clicked.connect(self.calculate_all_salaries)

        top_layout.addWidget(month_lbl)
        top_layout.addWidget(self.salary_month_btn)
        top_layout.addStretch()
        top_layout.addWidget(calc_btn)

        layout.addWidget(top_box)

        # لیست — با اسکرول گرد
        content = QWidget()

        self.salaries_layout = QVBoxLayout(content)
        self.salaries_layout.setContentsMargins(4, 4, 16, 4)
        self.salaries_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)

        layout.addWidget(scroll, 1)

        return widget

    def on_salary_month_changed(self, year, month):

        self.selected_year = year
        self.selected_month = month
        self.refresh_salaries()

    # =====================================================
    # TAB 3: BONUSES
    # =====================================================

    def build_bonuses_tab(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        top_box = QFrame()
        top_box.setObjectName("box")
        top_box.setAttribute(Qt.WA_StyledBackground, True)

        top_layout = QHBoxLayout(top_box)
        top_layout.setContentsMargins(20, 14, 20, 14)
        top_layout.setSpacing(12)

        title = QLabel("پاداش‌ها")
        title.setObjectName("sectionTitle")

        add_btn = QPushButton("+  افزودن پاداش")
        add_btn.setObjectName("primaryBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_bonus_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(add_btn)

        layout.addWidget(top_box)

        content = QWidget()

        self.bonuses_layout = QVBoxLayout(content)
        self.bonuses_layout.setContentsMargins(4, 4, 16, 4)
        self.bonuses_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)

        layout.addWidget(scroll, 1)

        return widget

    # =====================================================
    # TAB 4: DEDUCTIONS
    # =====================================================

    def build_deductions_tab(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        top_box = QFrame()
        top_box.setObjectName("box")
        top_box.setAttribute(Qt.WA_StyledBackground, True)

        top_layout = QHBoxLayout(top_box)
        top_layout.setContentsMargins(20, 14, 20, 14)
        top_layout.setSpacing(12)

        title = QLabel("کسورات")
        title.setObjectName("sectionTitle")

        add_btn = QPushButton("+  افزودن کسر")
        add_btn.setObjectName("primaryBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_deduction_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(add_btn)

        layout.addWidget(top_box)

        content = QWidget()

        self.deductions_layout = QVBoxLayout(content)
        self.deductions_layout.setContentsMargins(4, 4, 16, 4)
        self.deductions_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)

        layout.addWidget(scroll, 1)

        return widget

    # =====================================================
    # TAB 5: HISTORY
    # =====================================================

    def build_history_tab(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        top_box = QFrame()
        top_box.setObjectName("box")
        top_box.setAttribute(Qt.WA_StyledBackground, True)

        top_layout = QHBoxLayout(top_box)
        top_layout.setContentsMargins(20, 14, 20, 14)
        top_layout.setSpacing(12)

        title = QLabel("تاریخچه پرداخت‌ها")
        title.setObjectName("sectionTitle")

        top_layout.addWidget(title)
        top_layout.addStretch()

        layout.addWidget(top_box)

        content = QWidget()

        self.history_layout = QVBoxLayout(content)
        self.history_layout.setContentsMargins(4, 4, 16, 4)
        self.history_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)

        layout.addWidget(scroll, 1)

        return widget

    # =====================================================
    # EMPLOYEE HISTORY TAB
    # =====================================================

    def build_employee_history_tab(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        top_box = QFrame()
        top_box.setObjectName("box")
        top_box.setAttribute(Qt.WA_StyledBackground, True)

        top_layout = QHBoxLayout(top_box)
        top_layout.setContentsMargins(20, 14, 20, 14)

        title = QLabel("پرداخت‌های من")
        title.setObjectName("sectionTitle")

        top_layout.addWidget(title)
        top_layout.addStretch()

        layout.addWidget(top_box)

        content = QWidget()

        self.emp_history_layout = QVBoxLayout(content)
        self.emp_history_layout.setContentsMargins(4, 4, 16, 4)
        self.emp_history_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)

        layout.addWidget(scroll, 1)

        return widget

    # =====================================================
    # REFRESH: DASHBOARD
    # =====================================================

    def refresh_dashboard(self):

        if not self.is_owner or not self.complex_id:
            return

        year = self.selected_year
        month = self.selected_month

        result = self.db.fetch_one(
            """
            SELECT
                COUNT(*) AS cnt,
                COALESCE(SUM(finalAmount), 0) AS total,
                COALESCE(SUM(CASE WHEN status='paid' THEN finalAmount ELSE 0 END), 0) AS paid
            FROM salaries s
            INNER JOIN complex_members cm ON cm.memberId = s.memberId
            WHERE cm.complexId = %s
              AND s.salaryYear = %s
              AND s.salaryMonth = %s
            """,
            (self.complex_id, year, month)
        )

        total = float(result["total"] or 0) if result else 0
        paid = float(result["paid"] or 0) if result else 0
        remain = total - paid

        emp_result = self.db.fetch_one(
            """
            SELECT COUNT(*) AS cnt
            FROM complex_members
            WHERE complexId = %s
              AND role IN ('employee', 'both')
              AND isActive = '1'
            """,
            (self.complex_id,)
        )

        emp_count = emp_result["cnt"] if emp_result else 0

        self.dash_total_box.findChild(QLabel, "statValue").setText(
            format_money(total)
        )
        self.dash_paid_box.findChild(QLabel, "statValueGreen").setText(
            format_money(paid)
        )
        self.dash_remain_box.findChild(QLabel, "statValueRed").setText(
            format_money(remain)
        )
        self.dash_emp_box.findChild(QLabel, "statValue").setText(
            str(emp_count)
        )

    # =====================================================
    # REFRESH: SALARIES
    # =====================================================

    def refresh_salaries(self):

        if not self.is_owner or not self.complex_id:
            return

        while self.salaries_layout.count():
            item = self.salaries_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        year = self.selected_year
        month = self.selected_month

        rows = self.db.fetch_all(
            """
            SELECT
                cm.memberId,
                u.name,
                u.profession,
                ep.jobTitle,
                ep.salaryType,
                ep.baseSalary,
                s.salaryId,
                s.baseSalary AS calcBase,
                s.overtimeAmount,
                s.bonusAmount,
                s.deductionAmount,
                s.loanAmount,
                s.insuranceAmount,
                s.taxAmount,
                s.advanceAmount,
                s.finalAmount,
                s.status,
                s.paidDate
            FROM complex_members cm
            INNER JOIN users u ON u.userId = cm.userId
            LEFT JOIN employee_profiles ep ON ep.memberId = cm.memberId
            LEFT JOIN salaries s
                ON s.memberId = cm.memberId
                AND s.salaryYear = %s
                AND s.salaryMonth = %s
            WHERE cm.complexId = %s
              AND cm.role IN ('employee', 'both')
              AND cm.isActive = '1'
            ORDER BY u.name ASC
            """,
            (year, month, self.complex_id)
        )

        if not rows:

            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setMinimumHeight(120)

            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)

            t = QLabel("کارمندی توی این مجموعه نیست")
            t.setObjectName("emptyText")
            t.setAlignment(Qt.AlignCenter)

            el.addWidget(t)

            self.salaries_layout.addWidget(empty)
            self.salaries_layout.addStretch()
            return

        for row in rows:
            card = self.create_salary_card(row)
            self.salaries_layout.addWidget(card)

        self.salaries_layout.addStretch()

    def create_salary_card(self, row):

        card = QFrame()
        card.setObjectName("boxSub")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(130)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # سمت راست
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setContentsMargins(0, 0, 0, 0)

        name = QLabel(row.get("name") or "بدون نام")
        name.setObjectName("empName")
        name.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        job = row.get("jobTitle") or "بدون شغل"

        salary_type_map = {
            "monthly": "ماهانه",
            "daily": "روزانه",
            "hourly": "ساعتی"
        }

        st = salary_type_map.get(row.get("salaryType"), "-")

        info = QLabel(f"{job}")
        info.setObjectName("empInfo")
        info.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        type_lbl = QLabel(f"حقوق {st}")
        type_lbl.setObjectName("empInfo")
        type_lbl.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        right_layout.addWidget(name)
        right_layout.addWidget(info)
        right_layout.addWidget(type_lbl)
        right_layout.addStretch()

        layout.addLayout(right_layout, 1)

        # وسط
        calc_base = float(row.get("calcBase") or 0)
        overtime = float(row.get("overtimeAmount") or 0)
        bonus = float(row.get("bonusAmount") or 0)
        deduction = float(row.get("deductionAmount") or 0)
        loan = float(row.get("loanAmount") or 0)

        amounts_widget = QWidget()
        amounts_widget.setStyleSheet("background: transparent;")

        amounts_layout = QVBoxLayout(amounts_widget)
        amounts_layout.setContentsMargins(0, 0, 0, 0)
        amounts_layout.setSpacing(4)

        def add_row(label_text, value_text, value_kind="normal"):

            row_widget = QWidget()
            row_widget.setStyleSheet("background: transparent;")

            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)

            lbl = QLabel(label_text)
            lbl.setObjectName("moneyLabel")
            lbl.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

            val = QLabel(value_text)

            if value_kind == "green":
                val.setObjectName("moneyValueGreen")
            elif value_kind == "red":
                val.setObjectName("moneyValueRed")
            else:
                val.setObjectName("moneyValue")

            val.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)

            row_layout.addWidget(lbl)
            row_layout.addWidget(val, 1)

            amounts_layout.addWidget(row_widget)

        if calc_base > 0:
            add_row("پایه محاسبه‌شده:", format_money(calc_base))

        if overtime > 0:
            add_row("اضافه‌کار:", f"+ {format_money(overtime)}", "green")

        if bonus > 0:
            add_row("پاداش:", f"+ {format_money(bonus)}", "green")

        if deduction > 0:
            add_row("کسورات:", f"- {format_money(deduction)}", "red")

        if loan > 0:
            add_row("وام:", f"- {format_money(loan)}", "red")

        amounts_layout.addStretch()

        layout.addWidget(amounts_widget, 2)

        # چپ
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignVCenter)

        final_title = QLabel("حقوق نهایی")
        final_title.setObjectName("statTitle")
        final_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        final = float(row.get("finalAmount") or 0)

        final_value = QLabel(format_money(final))
        final_value.setObjectName("moneyValueBlue")
        final_value.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        left_layout.addWidget(final_title)
        left_layout.addWidget(final_value)

        status_row = QHBoxLayout()
        status_row.setSpacing(8)

        status = row.get("status") or "draft"

        if status == "paid":
            badge = QLabel("پرداخت‌شده")
            badge.setObjectName("badgePaid")
        elif status == "calculated":
            badge = QLabel("محاسبه‌شده")
            badge.setObjectName("badgePending")
        else:
            badge = QLabel("پیش‌نویس")
            badge.setObjectName("badgeDraft")

        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(28)
        badge.setMinimumWidth(90)

        status_row.addWidget(badge)

        if status in ("draft", "calculated") and row.get("salaryId"):

            pay_btn = QPushButton("پرداخت")
            pay_btn.setObjectName("payBtn")
            pay_btn.setFixedHeight(28)
            pay_btn.setMinimumWidth(90)
            pay_btn.setCursor(Qt.PointingHandCursor)
            pay_btn.clicked.connect(
                lambda checked=False, r=row: self.pay_salary(r)
            )

            status_row.addWidget(pay_btn)

        left_layout.addLayout(status_row)

        layout.addLayout(left_layout, 1)

        return card

    def pay_salary(self, row):

        salary_id = row.get("salaryId")
        member_id = row.get("memberId")

        if not salary_id:
            return

        final_amount = float(row.get("finalAmount") or 0)

        self.db.execute(
            """
            UPDATE salaries
            SET status = 'paid',
                paidDate = NOW(),
                paidBy = %s
            WHERE salaryId = %s
            """,
            (self.user_id, salary_id)
        )

        self.db.execute(
            """
            INSERT INTO payments
            (
                memberId,
                complexId,
                salaryId,
                amount,
                paymentType,
                paymentDate,
                paidBy,
                description
            )
            VALUES
            (
                %s, %s, %s,
                %s,
                'salary',
                NOW(),
                %s,
                %s
            )
            """,
            (
                member_id,
                self.complex_id,
                salary_id,
                final_amount,
                self.user_id,
                f"پرداخت حقوق {MONTH_NAMES[self.selected_month - 1]} {self.selected_year}"
            )
        )

        NiceMessageBox.success(
            self, "پرداخت شد",
            f"حقوق {row.get('name')} پرداخت شد."
        )

        self.refresh_salaries()

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate_all_salaries(self):

        if not self.complex_id:
            return

        year = self.selected_year
        month = self.selected_month

        members = self.db.fetch_all(
            """
            SELECT
                cm.memberId,
                ep.baseSalary,
                ep.salaryType,
                ep.workDays,
                ep.workHours
            FROM complex_members cm
            LEFT JOIN employee_profiles ep ON ep.memberId = cm.memberId
            WHERE cm.complexId = %s
              AND cm.role IN ('employee', 'both')
              AND cm.isActive = '1'
            """,
            (self.complex_id,)
        )

        if not members:
            NiceMessageBox.warning(
                self, "خطا",
                "کارمندی برای محاسبه وجود ندارد."
            )
            return

        for m in members:

            self.calculate_one_salary(
                m["memberId"],
                m.get("baseSalary") or 0,
                m.get("salaryType") or "monthly",
                m.get("workDays") or 26,
                m.get("workHours") or 8,
                year,
                month
            )

        self.refresh_salaries()

        NiceMessageBox.success(
            self, "محاسبه شد",
            "حقوق همه‌ی کارمندان برای این ماه محاسبه شد."
        )

    def calculate_one_salary(
        self,
        member_id,
        base_salary,
        salary_type,
        work_days,
        work_hours,
        year,
        month
    ):

        base_salary = float(base_salary or 0)
        work_days = float(work_days or 26)
        work_hours = float(work_hours or 8)

        gy, gm, gd = jalali_to_gregorian(year, month, 1)
        first_day = date(gy, gm, gd)

        if month <= 6:
            last_day_num = 31
        elif month <= 11:
            last_day_num = 30
        elif is_jalali_leap(year):
            last_day_num = 30
        else:
            last_day_num = 29

        gy2, gm2, gd2 = jalali_to_gregorian(year, month, last_day_num)
        last_day = date(gy2, gm2, gd2)

        att = self.db.fetch_one(
            """
            SELECT
                COUNT(DISTINCT workDate) AS days,
                COALESCE(SUM(workedMinutes), 0) AS minutes,
                COALESCE(SUM(overtimeMinutes), 0) AS overtime
            FROM attendance
            WHERE memberId = %s
              AND workDate BETWEEN %s AND %s
              AND approvalStatus = 'approved'
            """,
            (member_id, first_day, last_day)
        )

        days_present = float(att["days"] or 0) if att else 0
        minutes_worked = float(att["minutes"] or 0) if att else 0
        overtime_min = float(att["overtime"] or 0) if att else 0

        if salary_type == "monthly":

            ratio = days_present / work_days if work_days else 0
            calc_base = base_salary * ratio

            hourly_rate = (
                base_salary / work_days / work_hours
                if (work_days and work_hours) else 0
            )
            overtime_amount = hourly_rate * (overtime_min / 60) * 1.4

        elif salary_type == "daily":

            calc_base = base_salary * days_present
            hourly_rate = base_salary / work_hours if work_hours else 0
            overtime_amount = hourly_rate * (overtime_min / 60) * 1.4

        elif salary_type == "hourly":

            calc_base = base_salary * (minutes_worked / 60)
            overtime_amount = base_salary * (overtime_min / 60) * 1.4

        else:
            calc_base = 0
            overtime_amount = 0

        bonus_row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM bonuses
            WHERE memberId = %s
              AND YEAR(bonusDate) = %s
              AND MONTH(bonusDate) = %s
              AND status = 'approved'
            """,
            (member_id, gy, gm)
        )
        bonus_amount = float(bonus_row["total"] or 0) if bonus_row else 0

        ded_row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM deductions
            WHERE memberId = %s
              AND YEAR(deductionDate) = %s
              AND MONTH(deductionDate) = %s
              AND status = 'approved'
            """,
            (member_id, gy, gm)
        )
        deduction_amount = float(ded_row["total"] or 0) if ded_row else 0

        loan_row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(li.amount), 0) AS total
            FROM loan_installments li
            INNER JOIN loans l ON l.loanId = li.loanId
            WHERE l.memberId = %s
              AND YEAR(li.dueDate) = %s
              AND MONTH(li.dueDate) = %s
              AND li.status = 'pending'
            """,
            (member_id, gy, gm)
        )
        loan_amount = float(loan_row["total"] or 0) if loan_row else 0

        final = (
            calc_base
            + overtime_amount
            + bonus_amount
            - deduction_amount
            - loan_amount
        )

        if final < 0:
            final = 0

        existing = self.db.fetch_one(
            """
            SELECT salaryId
            FROM salaries
            WHERE memberId = %s
              AND salaryYear = %s
              AND salaryMonth = %s
            LIMIT 1
            """,
            (member_id, year, month)
        )

        if existing:

            self.db.execute(
                """
                UPDATE salaries
                SET baseSalary = %s,
                    overtimeAmount = %s,
                    bonusAmount = %s,
                    deductionAmount = %s,
                    loanAmount = %s,
                    finalAmount = %s,
                    status = 'calculated'
                WHERE salaryId = %s
                """,
                (
                    calc_base,
                    overtime_amount,
                    bonus_amount,
                    deduction_amount,
                    loan_amount,
                    final,
                    existing["salaryId"]
                )
            )

        else:

            self.db.execute(
                """
                INSERT INTO salaries
                (
                    memberId,
                    salaryYear,
                    salaryMonth,
                    baseSalary,
                    overtimeAmount,
                    bonusAmount,
                    deductionAmount,
                    loanAmount,
                    finalAmount,
                    status,
                    createdDate
                )
                VALUES
                (
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    'calculated',
                    NOW()
                )
                """,
                (
                    member_id,
                    year,
                    month,
                    calc_base,
                    overtime_amount,
                    bonus_amount,
                    deduction_amount,
                    loan_amount,
                    final
                )
            )

    # =====================================================
    # REFRESH: BONUSES
    # =====================================================

    def refresh_bonuses(self):

        if not self.is_owner or not self.complex_id:
            return

        while self.bonuses_layout.count():
            item = self.bonuses_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        rows = self.db.fetch_all(
            """
            SELECT
                b.bonusId,
                b.amount,
                b.title,
                b.description,
                b.bonusDate,
                b.status,
                u.name
            FROM bonuses b
            INNER JOIN complex_members cm ON cm.memberId = b.memberId
            INNER JOIN users u ON u.userId = cm.userId
            WHERE cm.complexId = %s
            ORDER BY b.bonusDate DESC, b.bonusId DESC
            LIMIT 100
            """,
            (self.complex_id,)
        )

        if not rows:

            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setMinimumHeight(120)

            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)

            t = QLabel("هنوز پاداشی ثبت نشده")
            t.setObjectName("emptyText")
            t.setAlignment(Qt.AlignCenter)

            el.addWidget(t)

            self.bonuses_layout.addWidget(empty)
            self.bonuses_layout.addStretch()
            return

        for row in rows:
            card = self.create_bonus_card(row)
            self.bonuses_layout.addWidget(card)

        self.bonuses_layout.addStretch()

    def create_bonus_card(self, row):

        card = QFrame()
        card.setObjectName("boxSub")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(70)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(12)

        name = QLabel(row.get("name") or "بدون نام")
        name.setObjectName("empName")
        name.setMinimumWidth(140)
        name.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        title = QLabel(row.get("title") or "پاداش")
        title.setObjectName("moneyValue")
        title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        bd = row.get("bonusDate")

        if isinstance(bd, date):
            qd = QDate(bd.year, bd.month, bd.day)
            date_str = jalali_string(qd)
        else:
            date_str = str(bd)

        date_lbl = QLabel(date_str)
        date_lbl.setObjectName("empInfo")

        amount = QLabel(f"+{format_money(row.get('amount') or 0)}")
        amount.setObjectName("moneyValueGreen")

        layout.addWidget(name)
        layout.addWidget(title, 1)
        layout.addWidget(date_lbl)
        layout.addWidget(amount)

        return card

    def open_add_bonus_dialog(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("افزودن پاداش")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(420)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        title = QLabel("افزودن پاداش")
        title.setStyleSheet("""
            color: #17324D;
            font-size: 15px;
            font-weight: 700;
            background: transparent;
        """)

        layout.addWidget(title)

        emp_lbl = QLabel("کارمند")
        emp_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        emp_combo = QComboBox()
        emp_combo.setFixedHeight(42)
        emp_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #DCE6F2;
                border-radius: 12px;
                padding: 0 12px;
                padding-left: 30px;
                color: #17324D;
                font-size: 12px;
            }
            QComboBox::drop-down {
                width: 26px;
                border: none;
            }
        """)

        members = self.db.fetch_all(
            """
            SELECT cm.memberId, u.name
            FROM complex_members cm
            INNER JOIN users u ON u.userId = cm.userId
            WHERE cm.complexId = %s
              AND cm.role IN ('employee', 'both')
              AND cm.isActive = '1'
            ORDER BY u.name ASC
            """,
            (self.complex_id,)
        )

        for m in members or []:
            emp_combo.addItem(m["name"] or "بدون نام", m["memberId"])

        layout.addWidget(emp_lbl)
        layout.addWidget(emp_combo)

        t_lbl = QLabel("عنوان پاداش")
        t_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        title_input = QLineEdit()
        title_input.setObjectName("formInput")
        title_input.setPlaceholderText("مثلاً پاداش عملکرد")

        layout.addWidget(t_lbl)
        layout.addWidget(title_input)

        a_lbl = QLabel("مبلغ (تومان)")
        a_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        amount_input = QLineEdit()
        amount_input.setObjectName("formInput")
        amount_input.setPlaceholderText("مثلاً 500000")
        amount_input.setLayoutDirection(Qt.LeftToRight)

        layout.addWidget(a_lbl)
        layout.addWidget(amount_input)

        d_lbl = QLabel("توضیحات (اختیاری)")
        d_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        desc_input = QLineEdit()
        desc_input.setObjectName("formInput")

        layout.addWidget(d_lbl)
        layout.addWidget(desc_input)

        layout.addSpacing(8)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = QPushButton("ذخیره")
        save_btn.setObjectName("primaryBtn")
        save_btn.setCursor(Qt.PointingHandCursor)

        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)

        layout.addLayout(btns)

        def on_save():

            if emp_combo.count() == 0:
                NiceMessageBox.warning(dialog, "خطا", "کارمندی وجود ندارد.")
                return

            member_id = emp_combo.currentData()
            title_text = title_input.text().strip()
            amount_text = amount_input.text().strip()
            desc_text = desc_input.text().strip()

            if not title_text:
                NiceMessageBox.warning(dialog, "خطا", "لطفاً عنوان پاداش را وارد کنید.")
                return

            if not amount_text:
                NiceMessageBox.warning(dialog, "خطا", "لطفاً مبلغ را وارد کنید.")
                return

            try:
                amount = float(amount_text.replace(",", "").replace("٬", ""))
            except ValueError:
                NiceMessageBox.warning(dialog, "خطا", "مبلغ نامعتبر است.")
                return

            today = date.today()

            self.db.execute(
                """
                INSERT INTO bonuses
                (
                    memberId,
                    amount,
                    title,
                    description,
                    bonusDate,
                    createdBy,
                    status,
                    approvedBy
                )
                VALUES
                (
                    %s, %s, %s, %s,
                    %s, %s,
                    'approved', %s
                )
                """,
                (
                    member_id,
                    amount,
                    title_text,
                    desc_text or None,
                    today,
                    self.user_id,
                    self.user_id
                )
            )

            dialog.accept()
            self.refresh_bonuses()

            NiceMessageBox.success(self, "ذخیره شد", "پاداش با موفقیت ثبت شد.")

        save_btn.clicked.connect(on_save)

        dialog.exec()

    # =====================================================
    # REFRESH: DEDUCTIONS
    # =====================================================

    def refresh_deductions(self):

        if not self.is_owner or not self.complex_id:
            return

        while self.deductions_layout.count():
            item = self.deductions_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        rows = self.db.fetch_all(
            """
            SELECT
                d.deductionId,
                d.amount,
                d.title,
                d.description,
                d.deductionDate,
                d.status,
                u.name
            FROM deductions d
            INNER JOIN complex_members cm ON cm.memberId = d.memberId
            INNER JOIN users u ON u.userId = cm.userId
            WHERE cm.complexId = %s
            ORDER BY d.deductionDate DESC, d.deductionId DESC
            LIMIT 100
            """,
            (self.complex_id,)
        )

        if not rows:

            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setMinimumHeight(120)

            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)

            t = QLabel("هنوز کسری ثبت نشده")
            t.setObjectName("emptyText")
            t.setAlignment(Qt.AlignCenter)

            el.addWidget(t)

            self.deductions_layout.addWidget(empty)
            self.deductions_layout.addStretch()
            return

        for row in rows:
            card = self.create_deduction_card(row)
            self.deductions_layout.addWidget(card)

        self.deductions_layout.addStretch()

    def create_deduction_card(self, row):

        card = QFrame()
        card.setObjectName("boxSub")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(70)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(12)

        name = QLabel(row.get("name") or "بدون نام")
        name.setObjectName("empName")
        name.setMinimumWidth(140)
        name.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        title = QLabel(row.get("title") or "کسر")
        title.setObjectName("moneyValue")
        title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        dd = row.get("deductionDate")

        if isinstance(dd, date):
            qd = QDate(dd.year, dd.month, dd.day)
            date_str = jalali_string(qd)
        else:
            date_str = str(dd)

        date_lbl = QLabel(date_str)
        date_lbl.setObjectName("empInfo")

        amount = QLabel(f"-{format_money(row.get('amount') or 0)}")
        amount.setObjectName("moneyValueRed")

        layout.addWidget(name)
        layout.addWidget(title, 1)
        layout.addWidget(date_lbl)
        layout.addWidget(amount)

        return card

    def open_add_deduction_dialog(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("افزودن کسر")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(420)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        title = QLabel("افزودن کسر")
        title.setStyleSheet("""
            color: #17324D;
            font-size: 15px;
            font-weight: 700;
            background: transparent;
        """)

        layout.addWidget(title)

        emp_lbl = QLabel("کارمند")
        emp_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        emp_combo = QComboBox()
        emp_combo.setFixedHeight(42)
        emp_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #DCE6F2;
                border-radius: 12px;
                padding: 0 12px;
                padding-left: 30px;
                color: #17324D;
                font-size: 12px;
            }
            QComboBox::drop-down {
                width: 26px;
                border: none;
            }
        """)

        members = self.db.fetch_all(
            """
            SELECT cm.memberId, u.name
            FROM complex_members cm
            INNER JOIN users u ON u.userId = cm.userId
            WHERE cm.complexId = %s
              AND cm.role IN ('employee', 'both')
              AND cm.isActive = '1'
            ORDER BY u.name ASC
            """,
            (self.complex_id,)
        )

        for m in members or []:
            emp_combo.addItem(m["name"] or "بدون نام", m["memberId"])

        layout.addWidget(emp_lbl)
        layout.addWidget(emp_combo)

        t_lbl = QLabel("عنوان کسر")
        t_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        title_input = QLineEdit()
        title_input.setObjectName("formInput")
        title_input.setPlaceholderText("مثلاً جریمه تأخیر")

        layout.addWidget(t_lbl)
        layout.addWidget(title_input)

        a_lbl = QLabel("مبلغ (تومان)")
        a_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        amount_input = QLineEdit()
        amount_input.setObjectName("formInput")
        amount_input.setPlaceholderText("مثلاً 200000")
        amount_input.setLayoutDirection(Qt.LeftToRight)

        layout.addWidget(a_lbl)
        layout.addWidget(amount_input)

        d_lbl = QLabel("توضیحات (اختیاری)")
        d_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        desc_input = QLineEdit()
        desc_input.setObjectName("formInput")

        layout.addWidget(d_lbl)
        layout.addWidget(desc_input)

        layout.addSpacing(8)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = QPushButton("ذخیره")
        save_btn.setObjectName("primaryBtn")
        save_btn.setCursor(Qt.PointingHandCursor)

        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)

        layout.addLayout(btns)

        def on_save():

            if emp_combo.count() == 0:
                NiceMessageBox.warning(dialog, "خطا", "کارمندی وجود ندارد.")
                return

            member_id = emp_combo.currentData()
            title_text = title_input.text().strip()
            amount_text = amount_input.text().strip()
            desc_text = desc_input.text().strip()

            if not title_text:
                NiceMessageBox.warning(dialog, "خطا", "لطفاً عنوان کسر را وارد کنید.")
                return

            if not amount_text:
                NiceMessageBox.warning(dialog, "خطا", "لطفاً مبلغ را وارد کنید.")
                return

            try:
                amount = float(amount_text.replace(",", "").replace("٬", ""))
            except ValueError:
                NiceMessageBox.warning(dialog, "خطا", "مبلغ نامعتبر است.")
                return

            today = date.today()

            self.db.execute(
                """
                INSERT INTO deductions
                (
                    memberId,
                    amount,
                    title,
                    description,
                    deductionDate,
                    createdBy,
                    status,
                    approvedBy
                )
                VALUES
                (
                    %s, %s, %s, %s,
                    %s, %s,
                    'approved', %s
                )
                """,
                (
                    member_id,
                    amount,
                    title_text,
                    desc_text or None,
                    today,
                    self.user_id,
                    self.user_id
                )
            )

            dialog.accept()
            self.refresh_deductions()

            NiceMessageBox.success(self, "ذخیره شد", "کسر با موفقیت ثبت شد.")

        save_btn.clicked.connect(on_save)

        dialog.exec()

    # =====================================================
    # REFRESH: HISTORY
    # =====================================================

    def refresh_history(self):

        if not self.is_owner or not self.complex_id:
            return

        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        rows = self.db.fetch_all(
            """
            SELECT
                p.paymentId,
                p.amount,
                p.paymentType,
                p.paymentDate,
                p.description,
                u.name
            FROM payments p
            INNER JOIN complex_members cm ON cm.memberId = p.memberId
            INNER JOIN users u ON u.userId = cm.userId
            WHERE cm.complexId = %s
            ORDER BY p.paymentDate DESC, p.paymentId DESC
            LIMIT 100
            """,
            (self.complex_id,)
        )

        if not rows:

            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setMinimumHeight(120)

            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)

            t = QLabel("هنوز پرداختی ثبت نشده")
            t.setObjectName("emptyText")
            t.setAlignment(Qt.AlignCenter)

            el.addWidget(t)

            self.history_layout.addWidget(empty)
            self.history_layout.addStretch()
            return

        for row in rows:
            card = self.create_history_card(row)
            self.history_layout.addWidget(card)

        self.history_layout.addStretch()

    def create_history_card(self, row):

        card = QFrame()
        card.setObjectName("boxSub")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(70)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(12)

        name = QLabel(row.get("name") or "بدون نام")
        name.setObjectName("empName")
        name.setMinimumWidth(140)
        name.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        ptype_map = {
            "salary": "حقوق",
            "job": "کارمزدی",
            "bonus": "پاداش",
            "advance": "علی‌الحساب",
            "other": "سایر"
        }

        ptype = ptype_map.get(row.get("paymentType"), "پرداخت")

        type_lbl = QLabel(ptype)
        type_lbl.setObjectName("moneyValue")
        type_lbl.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        pd = row.get("paymentDate")

        if isinstance(pd, datetime):
            qd = QDate(pd.year, pd.month, pd.day)
            date_str = jalali_string(qd) + " " + pd.strftime("%H:%M")
        elif isinstance(pd, date):
            qd = QDate(pd.year, pd.month, pd.day)
            date_str = jalali_string(qd)
        else:
            date_str = str(pd)

        date_lbl = QLabel(date_str)
        date_lbl.setObjectName("empInfo")

        amount = QLabel(f"{format_money(row.get('amount') or 0)}")
        amount.setObjectName("moneyValueBlue")

        layout.addWidget(name)
        layout.addWidget(type_lbl, 1)
        layout.addWidget(date_lbl)
        layout.addWidget(amount)

        return card

    # =====================================================
    # EMPLOYEE HISTORY
    # =====================================================

    def refresh_employee_history(self):

        while self.emp_history_layout.count():
            item = self.emp_history_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        rows = self.db.fetch_all(
            """
            SELECT
                p.amount,
                p.paymentType,
                p.paymentDate,
                p.description
            FROM payments p
            WHERE p.memberId = %s
            ORDER BY p.paymentDate DESC, p.paymentId DESC
            LIMIT 100
            """,
            (self.member_id,)
        )

        if not rows:

            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setMinimumHeight(120)

            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)

            t = QLabel("هنوز پرداختی برای شما ثبت نشده")
            t.setObjectName("emptyText")
            t.setAlignment(Qt.AlignCenter)

            el.addWidget(t)

            self.emp_history_layout.addWidget(empty)
            self.emp_history_layout.addStretch()
            return

        for row in rows:
            card = self.create_history_card(row)
            self.emp_history_layout.addWidget(card)

        self.emp_history_layout.addStretch()