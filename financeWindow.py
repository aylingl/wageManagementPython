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
    QScrollBar,
    QBoxLayout,
    QStackedWidget,
    QComboBox,
    QTimeEdit,
    QDialog
)

from PySide6.QtCore import (
    Qt, QTimer, QTime, QPoint, QDate, Signal, QRectF
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QRegion,
    QPainterPath
)

from database import Database
from signals import signals

# =========================================================
# ROUND SCROLL BAR
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

        handle_height = int(groove_height * page_step / total_range)
        handle_height = max(42, handle_height)
        handle_height = min(handle_height, groove_height)

        available_space = groove_height - handle_height

        if maximum == minimum:
            handle_y = groove_top
        else:
            value_ratio = (self.value() - minimum) / (maximum - minimum)
            handle_y = groove_top + available_space * value_ratio

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

        return (jy2 == jy and jm2 == 12 and jd2 == 30)

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
# PERSIAN MONTH POPUP
# =========================================================

class PersianMonthPopup(QWidget):

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
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.setLayoutDirection(Qt.RightToLeft)

        self._radius = 18
        self._margin = 6

        self.setFixedSize(300, 300)

        self.build_ui()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        r = self._radius
        m = self._margin

        rect = self.rect().adjusted(m, m, -m, -m)

        for i in range(6, 0, -1):

            shadow_color = QColor(0, 0, 0, 4 + (6 - i) * 2)

            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)

            painter.drawRoundedRect(
                rect.adjusted(-i, -i + 2, i, i + 2),
                r + i,
                r + i
            )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawRoundedRect(rect, r, r)

        painter.setPen(QColor("#E2EAF4"))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, r, r)

        painter.end()

    def resizeEvent(self, event):

        super().resizeEvent(event)

        path = QPainterPath()
        path.addRoundedRect(
            QRectF(self.rect()),
            self._radius + self._margin,
            self._radius + self._margin
        )

        polygon = path.toFillPolygon().toPolygon()
        region = QRegion(polygon)

        self.setMask(region)

    def build_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self._margin + 14,
            self._margin + 14,
            self._margin + 14,
            self._margin + 14
        )
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

            QPushButton#calNavBtn:pressed {
                background-color: #C8DDF5;
            }

            QPushButton#monthBtn {
                background-color: #F7F9FC;
                color: #17324D;
                border: 1px solid #DCE6F2;
                border-radius: 12px;
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
        self.setFixedHeight(44)
        self.setMinimumWidth(230)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 14, 0)
        layout.setSpacing(8)

        icon = QLabel("📅")
        icon.setObjectName("dateIconLabel")
        icon.setFixedSize(32, 32)
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
        self.my_name = "من"

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

        signals.employee_added.connect(self.on_employee_changed)
        signals.employee_removed.connect(self.on_employee_changed)
        signals.employee_updated.connect(self.on_employee_changed)

    def on_employee_changed(self, complex_id):
        if complex_id != self.complex_id:
            return

        try:
            current = self.stack.currentIndex()
            self.switch_tab(current)
        except Exception as e:
            print("FINANCE REFRESH ERROR:", e)

    def load_user_data(self):

        try:
            user = self.db.fetch_one(
                """
                SELECT userId, name
                FROM users
                WHERE phoneNumber = %s
                LIMIT 1
                """,
                (self.phone_number,)
            )

            if not user:
                return

            self.user_id = user["userId"]
            self.my_name = user.get("name") or "من"

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

    def make_rounded_scroll(self, content_widget):

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

        vbar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(vbar)

        scroll.setWidget(content_widget)

        return scroll

    def make_container_box(self, content_widget):

        box = QFrame()
        box.setObjectName("contentBox")
        box.setAttribute(Qt.WA_StyledBackground, True)

        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(18, 18, 18, 18)
        box_layout.setSpacing(8)

        box_layout.addWidget(content_widget)

        return box

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

        self.setStyleSheet("""

            QWidget#financeWindow {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
                color: #25364A;
            }

            QWidget#financeWindow QLabel {
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

            QFrame#contentBox {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
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
                font-size: 14px;
                font-weight: 700;
                background: transparent;
                padding: 3px 0px;
                min-height: 22px;
            }

            QLabel#empInfo {
                color: #607D96;
                font-size: 10px;
                background: transparent;
                padding: 1px 0px;
                min-height: 16px;
            }

            QLabel#moneyLabel {
                color: #8290A1;
                font-size: 11px;
                font-weight: 600;
                background: transparent;
                min-height: 18px;
            }

            QLabel#moneyValue {
                color: #17324D;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                min-height: 18px;
            }

            QLabel#moneyValueGreen {
                color: #16A34A;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                min-height: 18px;
            }

            QLabel#moneyValueRed {
                color: #D93025;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                min-height: 18px;
            }

            QLabel#moneyValueBlue {
                color: #1961C7;
                font-size: 14px;
                font-weight: 800;
                background: transparent;
                min-height: 20px;
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

            QPushButton#payBtn {
                background-color: #DCFCE7;
                color: #16A34A;
                border: none;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
                min-height: 30px;
            }

            QPushButton#payBtn:hover {
                background-color: #BBF7D0;
            }

            QPushButton#detailBtn {
                background-color: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
                min-height: 30px;
            }

            QPushButton#detailBtn:hover {
                background-color: #D8E9FF;
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
            "کل حقوق این ماه", "0", "statBox"
        )

        self.dash_paid_box = self.create_stat_box(
            "پرداخت‌شده", "0", "statBoxGreen"
        )

        self.dash_remain_box = self.create_stat_box(
            "مانده", "0", "statBoxRed"
        )

        self.dash_emp_box = self.create_stat_box(
            "تعداد کارمندان", "0", "statBox"
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

        content = QWidget()

        self.salaries_layout = QVBoxLayout(content)
        self.salaries_layout.setContentsMargins(4, 4, 12, 4)
        self.salaries_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)
        container = self.make_container_box(scroll)

        layout.addWidget(container, 1)

        return widget

    def on_salary_month_changed(self, year, month):
        self.selected_year = year
        self.selected_month = month
        self.refresh_salaries()

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
        self.bonuses_layout.setContentsMargins(4, 4, 12, 4)
        self.bonuses_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)
        container = self.make_container_box(scroll)

        layout.addWidget(container, 1)

        return widget

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
        self.deductions_layout.setContentsMargins(4, 4, 12, 4)
        self.deductions_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)
        container = self.make_container_box(scroll)

        layout.addWidget(container, 1)

        return widget

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
        self.history_layout.setContentsMargins(4, 4, 12, 4)
        self.history_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)
        container = self.make_container_box(scroll)

        layout.addWidget(container, 1)

        return widget

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
        top_layout.setSpacing(12)

        month_lbl = QLabel("ماه:")
        month_lbl.setStyleSheet("""
            color: #526273;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)

        self.emp_month_btn = PersianMonthButton()
        self.emp_month_btn.monthChanged.connect(
            self.on_emp_month_changed
        )

        top_layout.addWidget(month_lbl)
        top_layout.addWidget(self.emp_month_btn)
        top_layout.addStretch()

        layout.addWidget(top_box)

        content = QWidget()

        self.emp_history_layout = QVBoxLayout(content)
        self.emp_history_layout.setContentsMargins(4, 4, 12, 4)
        self.emp_history_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(content)
        container = self.make_container_box(scroll)

        layout.addWidget(container, 1)

        return widget

    def on_emp_month_changed(self, year, month):
        self.selected_year = year
        self.selected_month = month
        self.refresh_employee_history()

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
                u.phoneNumber,
                ep.jobTitle,
                ep.salaryType,
                ep.baseSalary,
                ep.workDays,
                ep.workHours,
                ep.employmentType,
                ep.allowOvertime,
                s.salaryId,
                s.baseSalary AS calcBase,
                s.overtimeAmount,
                s.bonusAmount,
                s.deductionAmount,
                s.loanAmount,
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
        card.setMinimumHeight(210)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(24)

        # ═══════════════ ستون راست ═══════════════
        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.setContentsMargins(0, 0, 0, 0)

        name_label = QLabel(row.get("name") or "کارمند")
        name_label.setObjectName("empName")
        name_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        name_label.setMinimumHeight(24)

        phone = row.get("phoneNumber") or "-"
        phone_label = QLabel(phone)
        phone_label.setObjectName("empInfo")
        phone_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        phone_label.setMinimumHeight(18)

        job = row.get("jobTitle") or "بدون شغل"

        salary_type_map = {
            "monthly": "ماهانه",
            "daily": "روزانه",
            "hourly": "ساعتی"
        }
        st = salary_type_map.get(row.get("salaryType"), "-")

        employment_map = {
            "fullTime": "تمام‌وقت",
            "partTime": "پاره‌وقت"
        }
        emp_type = employment_map.get(row.get("employmentType"), "-")

        job_label = QLabel(f"{job}   •   حقوق {st}   •   {emp_type}")
        job_label.setObjectName("empInfo")
        job_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        job_label.setMinimumHeight(18)

        right_col.addWidget(name_label)
        right_col.addWidget(phone_label)
        right_col.addWidget(job_label)

        div1 = QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet("background-color: #EEF3FA; border: none;")
        right_col.addSpacing(4)
        right_col.addWidget(div1)
        right_col.addSpacing(4)

        # ─── حقوق پایه (سمت راست) ───
        base_salary = float(row.get("baseSalary") or 0)

        base_row = QLabel(f"حقوق پایه:  {format_money(base_salary)} تومان")
        base_row.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        base_row.setMinimumHeight(24)
        base_row.setStyleSheet("""
            color: #17324D;
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            padding: 3px 0px;
        """)

        right_col.addWidget(base_row)

        # ─── خلاصه‌ی این ماه ───
        summary_title = QLabel("📊  خلاصه‌ی این ماه")
        summary_title.setStyleSheet("""
            color: #4589E8;
            font-size: 10px;
            font-weight: 700;
            background: transparent;
            padding: 3px 0px;
        """)
        summary_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        summary_title.setMinimumHeight(20)

        right_col.addWidget(summary_title)

        overtime = float(row.get("overtimeAmount") or 0)
        bonus = float(row.get("bonusAmount") or 0)
        deduction = float(row.get("deductionAmount") or 0)
        loan = float(row.get("loanAmount") or 0)

        def add_mini_row(label_text, value_text, kind="normal"):

            rw = QWidget()
            rw.setStyleSheet("background: transparent;")
            rw.setMinimumHeight(22)

            rl = QHBoxLayout(rw)
            rl.setContentsMargins(14, 2, 0, 2)
            rl.setSpacing(6)

            lb = QLabel(label_text)
            lb.setObjectName("moneyLabel")

            vl = QLabel(value_text)

            if kind == "green":
                vl.setObjectName("moneyValueGreen")
            elif kind == "red":
                vl.setObjectName("moneyValueRed")
            else:
                vl.setObjectName("moneyValue")

            vl.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)

            rl.addWidget(lb)
            rl.addWidget(vl, 1)

            right_col.addWidget(rw)

        has_any = False

        if overtime > 0:
            add_mini_row("اضافه‌کاری:", f"+ {format_money(overtime)}", "green")
            has_any = True

        if bonus > 0:
            add_mini_row("پاداش:", f"+ {format_money(bonus)}", "green")
            has_any = True

        if deduction > 0:
            add_mini_row("کسورات:", f"- {format_money(deduction)}", "red")
            has_any = True

        if loan > 0:
            add_mini_row("وام:", f"- {format_money(loan)}", "red")
            has_any = True

        if not has_any:
            no_extra = QLabel("—  هیچ مورد اضافه یا کسر ثبت نشده")
            no_extra.setObjectName("empInfo")
            no_extra.setContentsMargins(14, 0, 0, 0)
            no_extra.setMinimumHeight(18)
            right_col.addWidget(no_extra)

        right_col.addStretch()

        layout.addLayout(right_col, 3)

        # ═══════════════ ستون چپ ═══════════════
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setAlignment(Qt.AlignTop)

        # ─── حقوق نهایی ───
        final = float(row.get("finalAmount") or 0)

        final_title = QLabel("حقوق نهایی")
        final_title.setObjectName("statTitle")
        final_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        final_title.setMinimumHeight(18)

        final_value = QLabel(format_money(final) + " تومان")
        final_value.setObjectName("moneyValueBlue")
        final_value.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        final_value.setMinimumHeight(24)

        left_col.addWidget(final_title)
        left_col.addWidget(final_value)

        left_col.addSpacing(4)

        # ─── چک پرداخت ───
        status = row.get("status") or "draft"
        paid_date = row.get("paidDate")
        salary_id_for_check = row.get("salaryId")

        has_payment = False

        if salary_id_for_check:
            payment_check = self.db.fetch_one(
                """
                SELECT COUNT(*) AS cnt
                FROM payments
                WHERE salaryId = %s
                  AND paymentType = 'salary'
                """,
                (salary_id_for_check,)
            )

            has_payment = bool(payment_check and payment_check.get("cnt", 0) > 0)

        is_paid = (
            status == "paid"
            or paid_date is not None
            or has_payment
        )

        if is_paid:
            badge = QLabel("✅ پرداخت‌شده")
            badge.setObjectName("badgePaid")
        elif status == "calculated":
            badge = QLabel("⏳ در انتظار پرداخت")
            badge.setObjectName("badgePending")
        else:
            badge = QLabel("📝 پیش‌نویس")
            badge.setObjectName("badgeDraft")

        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(30)

        left_col.addWidget(badge)

        # ─── دکمه پرداخت ───
        if not is_paid and row.get("salaryId") and status in ("draft", "calculated"):

            pay_btn = QPushButton("💳  پرداخت")
            pay_btn.setObjectName("payBtn")
            pay_btn.setFixedHeight(30)
            pay_btn.setCursor(Qt.PointingHandCursor)
            pay_btn.clicked.connect(
                lambda checked=False, r=row: self.pay_salary(r)
            )

            left_col.addWidget(pay_btn)

        # ─── دکمه جزئیات ───
        detail_btn = QPushButton("📋  جزئیات")
        detail_btn.setObjectName("detailBtn")
        detail_btn.setFixedHeight(30)
        detail_btn.setCursor(Qt.PointingHandCursor)
        detail_btn.clicked.connect(
            lambda checked=False, r=row: self.open_details_dialog(r)
        )

        left_col.addWidget(detail_btn)

        left_col.addStretch()

        layout.addLayout(left_col, 2)

        return card

    def open_details_dialog(self, row):

        member_id = row.get("memberId")
        name = row.get("name") or "کارمند"

        if not member_id:
            return

        year = self.selected_year
        month = self.selected_month

        profile = self.db.fetch_one(
            """
            SELECT jobTitle, employmentType, salaryType,
                   baseSalary, workDays, workHours,
                   workStartTime, workEndTime, allowOvertime
            FROM employee_profiles
            WHERE memberId = %s
            LIMIT 1
            """,
            (member_id,)
        )

        if not profile:
            NiceMessageBox.error(self, "خطا", "اطلاعات پروفایل پیدا نشد.")
            return

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

        days_present = int(att["days"] or 0) if att else 0
        minutes_worked = int(att["minutes"] or 0) if att else 0
        overtime_min = int(att["overtime"] or 0) if att else 0

        salary = self.db.fetch_one(
            """
            SELECT
                baseSalary, overtimeAmount, bonusAmount,
                deductionAmount, loanAmount, finalAmount,
                status, paidDate
            FROM salaries
            WHERE memberId = %s
              AND salaryYear = %s
              AND salaryMonth = %s
            LIMIT 1
            """,
            (member_id, year, month)
        )

        dialog = QDialog(self)
        dialog.setWindowTitle(f"جزئیات محاسبه — {name}")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(650)
        dialog.setModal(True)

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        vbar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(vbar)

        content = QWidget()
        content.setObjectName("detailsContent")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        header_frame = QFrame()
        header_frame.setObjectName("detailsHeader")
        header_frame.setStyleSheet("""
            QFrame#detailsHeader {
                background-color: #F7F9FC;
                border: 1px solid #E2EAF4;
                border-radius: 18px;
            }
        """)

        h_layout = QVBoxLayout(header_frame)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.setSpacing(6)

        h_name = QLabel(name)
        h_name.setStyleSheet("""
            color: #17324D;
            font-size: 17px;
            font-weight: 800;
            background: transparent;
        """)

        h_sub = QLabel(
            f"📅  {MONTH_NAMES[month - 1]} {year}   •   📋  جزئیات محاسبه‌ی حقوق"
        )
        h_sub.setStyleSheet("""
            color: #4589E8;
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        """)

        h_layout.addWidget(h_name)
        h_layout.addWidget(h_sub)

        layout.addWidget(header_frame)

        section1 = self.create_modern_section("👤", "اطلاعات پروفایل")

        job = profile.get("jobTitle") or "بدون شغل"
        emp_map = {"fullTime": "تمام‌وقت", "partTime": "پاره‌وقت"}
        emp_type = emp_map.get(profile.get("employmentType"), "-")
        st_map = {"monthly": "ماهانه", "daily": "روزانه", "hourly": "ساعتی"}
        st_type = st_map.get(profile.get("salaryType"), "-")

        base = float(profile.get("baseSalary") or 0)
        wd = float(profile.get("workDays") or 26)
        wh = float(profile.get("workHours") or 8)

        allow_ot = str(profile.get("allowOvertime") or "1") == "1"
        ot_status = "✅ دارد" if allow_ot else "❌ ندارد"

        section1["layout"].addWidget(self.create_modern_row("شغل", job))
        section1["layout"].addWidget(self.create_modern_row("نوع همکاری", emp_type))
        section1["layout"].addWidget(self.create_modern_row("نوع حقوق", st_type))
        section1["layout"].addWidget(self.create_modern_row("حقوق پایه", format_money(base) + " تومان"))
        section1["layout"].addWidget(self.create_modern_row("روز × ساعت کاری", f"{int(wd)} روز × {int(wh)} ساعت"))
        section1["layout"].addWidget(self.create_modern_row("اجازه اضافه‌کاری", ot_status))

        layout.addWidget(section1["frame"])

        section2 = self.create_modern_section("🕒", "حضور و غیاب ماه")

        section2["layout"].addWidget(self.create_modern_row("روزهای حاضر", f"{days_present} روز"))

        total_hours = minutes_worked // 60
        total_min = minutes_worked % 60
        section2["layout"].addWidget(self.create_modern_row("مجموع ساعت کار", f"{total_hours} ساعت و {total_min} دقیقه"))

        ot_h = overtime_min // 60
        ot_m = overtime_min % 60
        section2["layout"].addWidget(self.create_modern_row("اضافه‌کاری ماه", f"{ot_h} ساعت و {ot_m} دقیقه"))

        layout.addWidget(section2["frame"])

        if salary:

            section3 = self.create_modern_section("🧮", "نحوه‌ی محاسبه")

            calc_base = float(salary.get("baseSalary") or 0)
            overtime_amt = float(salary.get("overtimeAmount") or 0)
            bonus_amt = float(salary.get("bonusAmount") or 0)
            deduction_amt = float(salary.get("deductionAmount") or 0)
            loan_amt = float(salary.get("loanAmount") or 0)
            final_amt = float(salary.get("finalAmount") or 0)

            emp_ratio = 1.0
            if profile.get("employmentType") == "partTime":
                emp_ratio = 0.5

            ratio_text = f"{days_present} ÷ {int(wd)}"

            if wd > 0:
                ratio = days_present / wd
            else:
                ratio = 0

            if profile.get("salaryType") == "monthly":
                formula_base = f"{format_money(base)} × ({ratio_text}) = {format_money(base * ratio)}"
            elif profile.get("salaryType") == "daily":
                formula_base = f"{format_money(base)} × {days_present} = {format_money(base * days_present)}"
            elif profile.get("salaryType") == "hourly":
                formula_base = f"{format_money(base)} × ({minutes_worked} ÷ 60) = {format_money(base * (minutes_worked / 60))}"
            else:
                formula_base = "—"

            section3["layout"].addWidget(self.create_modern_row("فرمول پایه", formula_base))

            if emp_ratio == 0.5:
                section3["layout"].addWidget(self.create_modern_row("ضریب پاره‌وقت", "× 0.5"))

            section3["layout"].addWidget(self.create_modern_row("پایه محاسبه‌شده", format_money(calc_base) + " تومان"))

            layout.addWidget(section3["frame"])

            section4 = self.create_modern_section("💰", "جزئیات حقوق")

            section4["layout"].addWidget(self.create_modern_row("حقوق پایه‌ی محاسبه‌شده", "+ " + format_money(calc_base), "normal"))

            if overtime_amt > 0:
                section4["layout"].addWidget(self.create_modern_row("اضافه‌کاری", "+ " + format_money(overtime_amt), "green"))

            if bonus_amt > 0:
                section4["layout"].addWidget(self.create_modern_row("پاداش", "+ " + format_money(bonus_amt), "green"))

            if deduction_amt > 0:
                section4["layout"].addWidget(self.create_modern_row("کسورات", "- " + format_money(deduction_amt), "red"))

            if loan_amt > 0:
                section4["layout"].addWidget(self.create_modern_row("وام", "- " + format_money(loan_amt), "red"))

            divider = QFrame()
            divider.setFixedHeight(1)
            divider.setStyleSheet("background-color: #EEF3FA; border: none;")
            section4["layout"].addWidget(divider)

            final_row = QFrame()
            final_row.setStyleSheet("""
                QFrame {
                    background-color: #EAF3FF;
                    border: none;
                    border-radius: 14px;
                }
            """)

            fr_layout = QHBoxLayout(final_row)
            fr_layout.setContentsMargins(16, 12, 16, 12)
            fr_layout.setSpacing(8)

            fr_lbl = QLabel("حقوق نهایی")
            fr_lbl.setStyleSheet("""
                color: #1961C7;
                font-size: 13px;
                font-weight: 800;
                background: transparent;
            """)

            fr_val = QLabel(format_money(final_amt) + " تومان")
            fr_val.setStyleSheet("""
                color: #1961C7;
                font-size: 15px;
                font-weight: 800;
                background: transparent;
            """)
            fr_val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            fr_layout.addWidget(fr_lbl)
            fr_layout.addStretch()
            fr_layout.addWidget(fr_val)

            section4["layout"].addWidget(final_row)

            status_val = salary.get("status") or "draft"
            paid_date_val = salary.get("paidDate")

            if status_val == "paid" or paid_date_val:
                status_text = "✅ پرداخت‌شده"
                status_color = "#16A34A"
                status_bg = "#EAF6EE"
            elif status_val == "calculated":
                status_text = "⏳ در انتظار پرداخت"
                status_color = "#B87900"
                status_bg = "#FFF4DD"
            else:
                status_text = "📝 پیش‌نویس"
                status_color = "#526273"
                status_bg = "#EEF2F6"

            status_row = QFrame()
            status_row.setStyleSheet(f"""
                QFrame {{
                    background-color: {status_bg};
                    border: none;
                    border-radius: 14px;
                }}
            """)

            sr_layout = QHBoxLayout(status_row)
            sr_layout.setContentsMargins(16, 10, 16, 10)

            sr_lbl = QLabel("وضعیت:")
            sr_lbl.setStyleSheet(f"""
                color: {status_color};
                font-size: 12px;
                font-weight: 700;
                background: transparent;
            """)

            sr_val = QLabel(status_text)
            sr_val.setStyleSheet(f"""
                color: {status_color};
                font-size: 13px;
                font-weight: 800;
                background: transparent;
            """)
            sr_val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            sr_layout.addWidget(sr_lbl)
            sr_layout.addStretch()
            sr_layout.addWidget(sr_val)

            section4["layout"].addSpacing(6)
            section4["layout"].addWidget(status_row)

            layout.addWidget(section4["frame"])

        else:

            no_salary = QLabel("⚠️  هنوز برای این ماه محاسبه‌ای انجام نشده")
            no_salary.setStyleSheet("""
                color: #B87900;
                background-color: #FFF4DD;
                border: 1px solid #FDE68A;
                border-radius: 16px;
                padding: 18px 20px;
                font-size: 13px;
                font-weight: 700;
            """)
            no_salary.setWordWrap(True)
            no_salary.setAlignment(Qt.AlignCenter)

            layout.addWidget(no_salary)

        layout.addStretch()

        scroll.setWidget(content)

        main_layout.addWidget(scroll)

        bottom = QFrame()
        bottom.setStyleSheet("""
            background-color: #FFFFFF;
            border-top: 1px solid #E2EAF4;
        """)

        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(24, 14, 24, 14)

        close_btn = QPushButton("بستن")
        close_btn.setFixedHeight(42)
        close_btn.setMinimumWidth(140)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #4589E8;
            }
        """)
        close_btn.clicked.connect(dialog.accept)

        bottom_layout.addStretch()
        bottom_layout.addWidget(close_btn)
        bottom_layout.addStretch()

        main_layout.addWidget(bottom)

        dialog.setStyleSheet("""
            QDialog {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }
        """)

        dialog.exec()

    def create_modern_section(self, icon, title_text):

        frame = QFrame()
        frame.setObjectName("modernSection")
        frame.setStyleSheet("""
            QFrame#modernSection {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("""
            QLabel {
                background-color: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
            }
        """)

        title = QLabel(title_text)
        title.setStyleSheet("""
            color: #17324D;
            font-size: 14px;
            font-weight: 800;
            background: transparent;
        """)

        title_row.addWidget(icon_lbl)
        title_row.addWidget(title)
        title_row.addStretch()

        layout.addLayout(title_row)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #EEF3FA; border: none;")
        layout.addWidget(divider)

        return {"frame": frame, "layout": layout}

    def create_modern_row(self, label_text, value_text, kind="normal"):

        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent;")
        row_widget.setMinimumHeight(26)

        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 4, 0, 4)
        row_layout.setSpacing(12)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("""
            color: #8290A1;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        """)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignTop | Qt.AlignVCenter)

        val = QLabel(value_text)

        if kind == "green":
            val.setStyleSheet("""
                color: #16A34A;
                font-size: 13px;
                font-weight: 700;
                background: transparent;
            """)
        elif kind == "red":
            val.setStyleSheet("""
                color: #D93025;
                font-size: 13px;
                font-weight: 700;
                background: transparent;
            """)
        elif kind == "blue":
            val.setStyleSheet("""
                color: #1961C7;
                font-size: 14px;
                font-weight: 800;
                background: transparent;
            """)
        else:
            val.setStyleSheet("""
                color: #17324D;
                font-size: 13px;
                font-weight: 700;
                background: transparent;
            """)

        val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        val.setWordWrap(True)
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)

        row_layout.addWidget(lbl, 1)
        row_layout.addWidget(val, 2)

        return row_widget

    def pay_salary(self, row):

        salary_id = row.get("salaryId")
        member_id = row.get("memberId")

        if not salary_id:
            return

        final_amount = float(row.get("finalAmount") or 0)

        result = self.db.execute(
            """
            UPDATE salaries
            SET status = 'paid',
                paidDate = NOW(),
                paidBy = %s
            WHERE salaryId = %s
            """,
            (self.user_id, salary_id)
        )

        if result is None:
            NiceMessageBox.error(
                self, "خطا",
                "ثبت پرداخت در دیتابیس انجام نشد."
            )
            return

        existing_payment = self.db.fetch_one(
            """
            SELECT paymentId
            FROM payments
            WHERE salaryId = %s
              AND paymentType = 'salary'
            LIMIT 1
            """,
            (salary_id,)
        )

        if not existing_payment:

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
                ep.workHours,
                ep.employmentType,
                ep.allowOvertime
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
                m.get("employmentType") or "fullTime",
                m.get("allowOvertime") or "1",
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
        employment_type,
        allow_overtime,
        year,
        month
    ):

        base_salary = float(base_salary or 0)
        work_days = float(work_days or 26)
        work_hours = float(work_hours or 8)

        if employment_type == "partTime":
            emp_ratio = 0.5
        else:
            emp_ratio = 1.0

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

        calc_base = calc_base * emp_ratio
        overtime_amount = overtime_amount * emp_ratio

        if str(allow_overtime) != "1":
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
            SELECT salaryId, status
            FROM salaries
            WHERE memberId = %s
              AND salaryYear = %s
              AND salaryMonth = %s
            LIMIT 1
            """,
            (member_id, year, month)
        )

        if existing:

            current_status = existing.get("status") or "draft"

            if current_status == "paid":
                new_status = "paid"
            else:
                new_status = "calculated"

            self.db.execute(
                """
                UPDATE salaries
                SET baseSalary = %s,
                    overtimeAmount = %s,
                    bonusAmount = %s,
                    deductionAmount = %s,
                    loanAmount = %s,
                    finalAmount = %s,
                    status = %s
                WHERE salaryId = %s
                """,
                (
                    calc_base,
                    overtime_amount,
                    bonus_amount,
                    deduction_amount,
                    loan_amount,
                    final,
                    new_status,
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

        name = QLabel(row.get("name") or "کارمند")
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
            emp_combo.addItem(m["name"] or "کارمند", m["memberId"])

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

        name = QLabel(row.get("name") or "کارمند")
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
            emp_combo.addItem(m["name"] or "کارمند", m["memberId"])

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

        name = QLabel(row.get("name") or "کارمند")
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

    def refresh_employee_history(self):

        while self.emp_history_layout.count():
            item = self.emp_history_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        my_name = self.my_name

        profile = self.db.fetch_one(
            """
            SELECT jobTitle, salaryType, baseSalary, workDays, workHours,
                   employmentType, allowOvertime
            FROM employee_profiles
            WHERE memberId = %s
            LIMIT 1
            """,
            (self.member_id,)
        )

        current_salary = self.db.fetch_one(
            """
            SELECT
                salaryId,
                baseSalary,
                overtimeAmount,
                bonusAmount,
                deductionAmount,
                loanAmount,
                finalAmount,
                status,
                paidDate
            FROM salaries
            WHERE memberId = %s
              AND salaryYear = %s
              AND salaryMonth = %s
            LIMIT 1
            """,
            (self.member_id, self.selected_year, self.selected_month)
        )

        has_payment = False

        if current_salary and current_salary.get("salaryId"):

            payment_check = self.db.fetch_one(
                """
                SELECT COUNT(*) AS cnt
                FROM payments
                WHERE salaryId = %s
                  AND paymentType = 'salary'
                """,
                (current_salary["salaryId"],)
            )

            has_payment = bool(
                payment_check and payment_check.get("cnt", 0) > 0
            )

        gy, gm, gd = jalali_to_gregorian(self.selected_year, self.selected_month, 1)
        first_day = date(gy, gm, gd)

        if self.selected_month <= 6:
            last_day_num = 31
        elif self.selected_month <= 11:
            last_day_num = 30
        elif is_jalali_leap(self.selected_year):
            last_day_num = 30
        else:
            last_day_num = 29

        gy2, gm2, gd2 = jalali_to_gregorian(self.selected_year, self.selected_month, last_day_num)
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
            (self.member_id, first_day, last_day)
        )

        days_present = int(att["days"] or 0) if att else 0
        minutes_worked = int(att["minutes"] or 0) if att else 0
        overtime_min = int(att["overtime"] or 0) if att else 0

        summary_card = QFrame()
        summary_card.setObjectName("boxSub")
        summary_card.setAttribute(Qt.WA_StyledBackground, True)

        s_layout = QVBoxLayout(summary_card)
        s_layout.setContentsMargins(22, 18, 22, 18)
        s_layout.setSpacing(10)

        s_title = QLabel(
            f"📊  خلاصه‌ی حقوق {MONTH_NAMES[self.selected_month - 1]} {self.selected_year}"
        )
        s_title.setStyleSheet("""
            color: #17324D;
            font-size: 15px;
            font-weight: 800;
            background: transparent;
        """)
        s_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        s_layout.addWidget(s_title)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: #EEF3FA; border: none;")
        s_layout.addWidget(div)

        def add_row(label_text, value_text, kind="normal"):

            rw = QWidget()
            rw.setStyleSheet("background: transparent;")
            rw.setMinimumHeight(22)

            rl = QHBoxLayout(rw)
            rl.setContentsMargins(0, 2, 0, 2)
            rl.setSpacing(8)

            lb = QLabel(label_text)
            lb.setObjectName("moneyLabel")
            lb.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

            vl = QLabel(value_text)

            if kind == "green":
                vl.setObjectName("moneyValueGreen")
            elif kind == "red":
                vl.setObjectName("moneyValueRed")
            elif kind == "blue":
                vl.setObjectName("moneyValueBlue")
            else:
                vl.setObjectName("moneyValue")

            vl.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)

            rl.addWidget(lb)
            rl.addWidget(vl, 1)

            s_layout.addWidget(rw)

        if current_salary:

            calc_base = float(current_salary.get("baseSalary") or 0)
            overtime = float(current_salary.get("overtimeAmount") or 0)
            bonus = float(current_salary.get("bonusAmount") or 0)
            deduction = float(current_salary.get("deductionAmount") or 0)
            loan = float(current_salary.get("loanAmount") or 0)
            final = float(current_salary.get("finalAmount") or 0)

            if calc_base > 0:
                add_row("حقوق پایه:", format_money(calc_base))

            if overtime > 0:
                ot_h = overtime_min // 60
                ot_m = overtime_min % 60
                add_row(
                    f"اضافه‌کاری ({ot_h}س {ot_m}د):",
                    f"+ {format_money(overtime)}",
                    "green"
                )

            if bonus > 0:
                add_row("پاداش:", f"+ {format_money(bonus)}", "green")

            if deduction > 0:
                add_row("کسورات:", f"- {format_money(deduction)}", "red")

            if loan > 0:
                add_row("وام:", f"- {format_money(loan)}", "red")

            div2 = QFrame()
            div2.setFixedHeight(1)
            div2.setStyleSheet("background-color: #EEF3FA; border: none;")
            s_layout.addWidget(div2)

            add_row("حقوق نهایی:", format_money(final), "blue")

            status = current_salary.get("status") or "draft"
            paid_date = current_salary.get("paidDate")

            is_paid = (
                status == "paid"
                or paid_date is not None
                or has_payment
            )

            if is_paid:
                status_text = "✅ پرداخت‌شده"
                status_color = "#16A34A"
                status_bg = "#EAF6EE"
            elif status == "calculated":
                status_text = "⏳ در انتظار پرداخت"
                status_color = "#B87900"
                status_bg = "#FFF4DD"
            else:
                status_text = "📝 پیش‌نویس"
                status_color = "#526273"
                status_bg = "#EEF2F6"

            status_lbl = QLabel(status_text)
            status_lbl.setAlignment(Qt.AlignCenter)
            status_lbl.setFixedHeight(32)
            status_lbl.setStyleSheet(f"""
                QLabel {{
                    color: {status_color};
                    background-color: {status_bg};
                    border: none;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 700;
                    padding: 0 16px;
                }}
            """)

            s_layout.addSpacing(4)
            s_layout.addWidget(status_lbl)

        else:

            no_calc = QLabel(
                "ℹ️  هنوز برای این ماه محاسبه‌ای انجام نشده\n"
                "منتظر بمانید تا مالک حقوق این ماه را محاسبه کند"
            )
            no_calc.setAlignment(Qt.AlignCenter)
            no_calc.setWordWrap(True)
            no_calc.setStyleSheet("""
                color: #8290A1;
                background-color: #F7F9FC;
                border: 1px dashed #DCE6F2;
                border-radius: 14px;
                padding: 20px 16px;
                font-size: 12px;
                font-weight: 600;
            """)

            s_layout.addWidget(no_calc)

        s_layout.addSpacing(6)

        att_title = QLabel("🕒  حضور و غیاب این ماه")
        att_title.setStyleSheet("""
            color: #17324D;
            font-size: 13px;
            font-weight: 700;
            background: transparent;
        """)
        att_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        s_layout.addWidget(att_title)

        add_row("روزهای حاضر:", f"{days_present} روز")

        total_h = minutes_worked // 60
        total_m = minutes_worked % 60

        add_row("مجموع ساعت کار:", f"{total_h}س {total_m}د")

        ot_h = overtime_min // 60
        ot_m = overtime_min % 60

        if overtime_min > 0:
            add_row("اضافه‌کاری:", f"{ot_h}س {ot_m}د", "green")
        else:
            add_row("اضافه‌کاری:", "ندارد")

        if current_salary or profile:

            detail_btn = QPushButton("📋  مشاهده‌ی جزئیات کامل محاسبه")
            detail_btn.setObjectName("detailBtn")
            detail_btn.setFixedHeight(40)
            detail_btn.setCursor(Qt.PointingHandCursor)
            detail_btn.clicked.connect(
                lambda checked=False, m=self.member_id, n=my_name:
                self.open_details_dialog({
                    "memberId": m,
                    "name": n
                })
            )

            s_layout.addSpacing(6)
            s_layout.addWidget(detail_btn)

        self.emp_history_layout.addWidget(summary_card)

        history_title = QLabel("💳  تاریخچه پرداخت‌ها")
        history_title.setObjectName("sectionTitle")
        history_title.setStyleSheet("""
            color: #17324D;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
            padding: 8px 4px 0px 4px;
        """)

        self.emp_history_layout.addWidget(history_title)

        rows = self.db.fetch_all(
            """
            SELECT
                p.paymentId,
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
            empty.setMinimumHeight(100)

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

            row["name"] = my_name

            card = self.create_history_card(row)
            self.emp_history_layout.addWidget(card)

        self.emp_history_layout.addStretch()