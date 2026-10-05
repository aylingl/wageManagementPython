import os
from datetime import datetime, date

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QLineEdit, QScrollArea, QScrollBar,
    QBoxLayout, QStackedWidget, QComboBox, QTimeEdit, QDialog,
    QListWidget, QListWidgetItem, QGraphicsDropShadowEffect
)

from PySide6.QtCore import (
    Qt, QTimer, QTime, QPoint, QDate, Signal, QRectF, QSize
)
from PySide6.QtGui import QPainter, QColor, QRegion, QPainterPath

from database import Database
from signals import signals
from theme import theme_manager
from i18n import tr, set_language, get_language

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
        c = theme_manager.colors()

        track_width = 6
        track_x = (self.width() - track_width) / 2
        track_top = 6
        track_bottom = self.height() - 6
        track_height = track_bottom - track_top

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(c["bg_input"]))
        painter.drawRoundedRect(
            int(track_x), int(track_top),
            track_width, int(track_height),
            track_width / 2, track_width / 2
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
        painter.setBrush(QColor(c["accent"]))
        painter.drawRoundedRect(
            int(handle_x), int(handle_y),
            handle_width, int(handle_height),
            handle_width / 2, handle_width / 2
        )

# =========================================================
# ROUNDED COMBO BOX
# =========================================================

class RoundedComboBox(QComboBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._popup = None
        self._list = None

    def showPopup(self):
        if self._popup is not None:
            self.hidePopup()
            return

        self._popup = QFrame(None)
        self._popup.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self._popup.setAttribute(Qt.WA_TranslucentBackground, True)

        outer = QVBoxLayout(self._popup)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("comboCard")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)

        outer.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self._list = QListWidget()
        self._list.setFrameShape(QFrame.NoFrame)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._list.setFocusPolicy(Qt.NoFocus)

        c = theme_manager.colors()

        self._list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
                padding: 6px;
                color: {c['text_main']};
                font-family: "Vazirmatn";
                font-size: 13px;
            }}
            QListWidget::item {{
                background: transparent;
                color: {c['text_main']};
                border-radius: 10px;
                padding: 10px 16px;
                margin: 2px 4px;
                min-height: 20px;
            }}
            QListWidget::item:hover {{
                background-color: {c['bg_hover']};
                color: {c['accent']};
            }}
            QListWidget::item:selected {{
                background-color: {c['accent']};
                color: white;
            }}
            QScrollBar:vertical {{
                width: 8px;
                background: transparent;
                border: none;
                margin: 6px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {c['accent']};
                border-radius: 4px;
                min-height: 24px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

        for i in range(self.count()):
            item = QListWidgetItem(self.itemText(i))
            item.setData(Qt.UserRole, i)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setSizeHint(QSize(0, 42))
            self._list.addItem(item)
            if i == self.currentIndex():
                self._list.setCurrentItem(item)

        self._list.itemClicked.connect(self._on_item_clicked)
        card_layout.addWidget(self._list)

        self._popup.setStyleSheet(f"""
            QFrame#comboCard {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 18px;
            }}
        """)

        count = max(self.count(), 1)
        content_h = count * 42 + 32
        popup_w = max(self.width(), 160)
        popup_h = min(content_h, 220)

        self._popup.setFixedWidth(popup_w)
        self._popup.setFixedHeight(popup_h)

        pos = self.mapToGlobal(QPoint(0, self.height() + 4))
        self._popup.move(pos)
        self._popup.show()

    def hidePopup(self):
        if self._popup is not None:
            self._popup.close()
            self._popup.deleteLater()
            self._popup = None
            self._list = None

    def _on_item_clicked(self, item):
        idx = item.data(Qt.UserRole)
        if idx is not None:
            self.setCurrentIndex(idx)
        self.hidePopup()

# =========================================================
# JALALI HELPERS
# =========================================================

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (355666 + (365 * gy) + ((gy2 + 3) // 4)
            - ((gy2 + 99) // 100) + ((gy2 + 399) // 400)
            + gd + g_d_m[gm - 1])
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
    days = (-355668 + (365 * jy) + ((jy // 33) * 8)
            + (((jy % 33) + 3) // 4) + jd
            + ((jm - 1) * 31 if jm < 7 else ((jm - 7) * 30) + 186))
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
    sal_a = [0, 31, 29 if is_leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
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

def jalali_month_days(jy, jm):
    if jm <= 6:
        return 31
    if jm <= 11:
        return 30
    if is_jalali_leap(jy):
        return 30
    return 29

WEEKDAY_NAMES = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یک‌شنبه"]
WEEKDAY_SHORT = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
MONTH_NAMES = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]

def jalali_string(qdate):
    jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
    return f"{jy:04d}/{jm:02d}/{jd:02d}"

def persian_date_long(qdate):
    jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
    weekday = WEEKDAY_NAMES[qdate.dayOfWeek() - 1]
    return f"{weekday} {jd} {MONTH_NAMES[jm - 1]} {jy}"

# =========================================================
# PERSIAN CALENDAR POPUP
# =========================================================

class PersianCalendarPopup(QWidget):

    dateSelected = Signal(QDate)

    def __init__(self, parent=None, current_qdate=None):
        super().__init__(parent)

        if current_qdate is None:
            current_qdate = QDate.currentDate()

        self.selected_qdate = current_qdate
        jy, jm, jd = gregorian_to_jalali(
            current_qdate.year(), current_qdate.month(), current_qdate.day()
        )
        self.view_year = jy
        self.view_month = jm
        self.selected_jy = jy
        self.selected_jm = jm
        self.selected_jd = jd

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.setLayoutDirection(Qt.RightToLeft)

        self._radius = 18
        self._margin = 6
        self.setFixedSize(300, 350)

        self.build_ui()
        self.refresh_grid()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = theme_manager.colors()

        r = self._radius
        m = self._margin
        rect = self.rect().adjusted(m, m, -m, -m)

        for i in range(6, 0, -1):
            shadow_color = QColor(0, 0, 0, 4 + (6 - i) * 2)
            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)
            painter.drawRoundedRect(rect.adjusted(-i, -i + 2, i, i + 2), r + i, r + i)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(c["bg_card"]))
        painter.drawRoundedRect(rect, r, r)

        painter.setPen(QColor(c["border"]))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, r, r)
        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._radius + self._margin, self._radius + self._margin)
        polygon = path.toFillPolygon().toPolygon()
        self.setMask(QRegion(polygon))

    def build_ui(self):
        c = theme_manager.colors()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(self._margin + 14, self._margin + 14, self._margin + 14, self._margin + 14)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(6)

        prev_btn = QPushButton(">")
        prev_btn.setObjectName("calNavBtn")
        prev_btn.setFixedSize(30, 30)
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.clicked.connect(self.go_prev_month)

        self.month_label = QLabel()
        self.month_label.setObjectName("calMonthLabel")
        self.month_label.setAlignment(Qt.AlignCenter)

        next_btn = QPushButton("<")
        next_btn.setObjectName("calNavBtn")
        next_btn.setFixedSize(30, 30)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.clicked.connect(self.go_next_month)

        header.addWidget(prev_btn)
        header.addWidget(self.month_label, 1)
        header.addWidget(next_btn)
        layout.addLayout(header)

        wd_layout = QHBoxLayout()
        wd_layout.setSpacing(2)
        for name in WEEKDAY_SHORT:
            lbl = QLabel(name)
            lbl.setObjectName("calWeekday")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(24)
            wd_layout.addWidget(lbl, 1)
        layout.addLayout(wd_layout)

        self.days_layout = QGridLayout()
        self.days_layout.setSpacing(2)
        for col in range(7):
            self.days_layout.setColumnStretch(col, 1)
        layout.addLayout(self.days_layout, 1)

        self.setStyleSheet(f"""
            QLabel#calMonthLabel {{
                color: {c['text_main']};
                font-size: 13px;
                font-weight: 700;
                background: transparent;
            }}
            QPushButton#calNavBtn {{
                background-color: {c['accent_light']};
                color: {c['accent']};
                border: 1px solid {c['border_hover']};
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
                padding: 0px;
            }}
            QPushButton#calNavBtn:hover {{
                background-color: {c['bg_hover']};
            }}
            QLabel#calWeekday {{
                color: {c['text_dim']};
                font-size: 10px;
                font-weight: 700;
                background: transparent;
            }}
            QPushButton#calDayBtn {{
                background-color: transparent;
                color: {c['text_main']};
                border: none;
                border-radius: 8px;
                font-size: 11px;
                font-weight: 600;
                min-height: 28px;
            }}
            QPushButton#calDayBtn:hover {{
                background-color: {c['bg_hover']};
                color: {c['accent']};
            }}
            QPushButton#calDayBtn[today="true"] {{
                border: 2px solid {c['accent']};
                color: {c['accent']};
            }}
            QPushButton#calDayBtn[selected="true"] {{
                background-color: {c['accent']};
                color: white;
                border: none;
            }}
        """)

    def refresh_grid(self):
        while self.days_layout.count():
            item = self.days_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.month_label.setText(f"{MONTH_NAMES[self.view_month - 1]} {self.view_year}")

        days_in_month = jalali_month_days(self.view_year, self.view_month)
        gy, gm, gd = jalali_to_gregorian(self.view_year, self.view_month, 1)
        first_qdate = QDate(gy, gm, gd)
        persian_weekday = (first_qdate.dayOfWeek() + 1) % 7

        today_qdate = QDate.currentDate()
        tjy, tjm, tjd = gregorian_to_jalali(
            today_qdate.year(), today_qdate.month(), today_qdate.day()
        )

        row = 0
        col = persian_weekday

        for day in range(1, days_in_month + 1):
            btn = QPushButton(str(day))
            btn.setObjectName("calDayBtn")
            btn.setCursor(Qt.PointingHandCursor)

            is_today = (self.view_year == tjy and self.view_month == tjm and day == tjd)
            is_selected = (
                self.view_year == self.selected_jy
                and self.view_month == self.selected_jm
                and day == self.selected_jd
            )

            btn.setProperty("today", "true" if is_today else "false")
            btn.setProperty("selected", "true" if is_selected else "false")
            btn.clicked.connect(lambda checked=False, d=day: self.pick_day(d))

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
        gy, gm, gd = jalali_to_gregorian(self.selected_jy, self.selected_jm, self.selected_jd)
        self.selected_qdate = QDate(gy, gm, gd)
        self.dateSelected.emit(self.selected_qdate)
        self.close()

# =========================================================
# PERSIAN DATE BUTTON
# =========================================================

class PersianDateButton(QFrame):

    dateChanged = Signal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._qdate = QDate.currentDate()

        self.setObjectName("persianDateFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(42)
        self.setMinimumWidth(220)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 14, 0)
        layout.setSpacing(8)

        self.icon_label = QLabel("📅")
        self.icon_label.setObjectName("dateIconLabel")
        self.icon_label.setFixedSize(30, 30)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.date_btn = QPushButton()
        self.date_btn.setObjectName("persianDateButton")
        self.date_btn.setCursor(Qt.PointingHandCursor)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.date_btn, 1)

        self._refresh_text()
        self.mousePressEvent = self._frame_clicked
        self.date_btn.clicked.connect(self._open_dialog)

    def _frame_clicked(self, event):
        self._open_dialog()
        event.accept()

    def _refresh_text(self):
        jy, jm, jd = gregorian_to_jalali(
            self._qdate.year(), self._qdate.month(), self._qdate.day()
        )
        self.date_btn.setText(f"{jy:04d} / {jm:02d} / {jd:02d}")

    def date(self):
        return self._qdate

    def setDate(self, qdate):
        self._qdate = qdate
        self._refresh_text()

    def _open_dialog(self):
        self._popup = PersianCalendarPopup(self, self._qdate)
        self._popup.dateSelected.connect(self._on_date_selected)
        global_pos = self.mapToGlobal(QPoint(0, self.height() + 4))
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

        c = theme_manager.colors()

        if kind == "success":
            icon_char, color, bg = "✓", "#16A34A", "#DCFCE7"
        elif kind == "error":
            icon_char, color, bg = "✕", "#D93025", "#FFE5E8"
        elif kind == "warning":
            icon_char, color, bg = "!", "#D93025", "#FFE5E8"
        else:
            icon_char, color, bg = "i", "#1961C7", "#DBEAFE"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['bg_card']};"
            f"border-radius: 22px;"
            f"border: 1px solid {c['border']};"
        )
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)

        icon_label = QLabel(icon_char)
        icon_label.setFixedSize(56, 56)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(
            f"background-color: {bg};color: {color};"
            f"border-radius: 28px;font-size: 26px;font-weight: 700;"
        )

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()
        layout.addLayout(icon_row)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            f"color: {c['text_main']};font-size: 16px;"
            f"font-weight: 700;background: transparent;border: none;"
        )
        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(
            f"color: {c['text_dim']};font-size: 12px;"
            f"background: transparent;border: none;"
        )
        layout.addWidget(text_label)
        layout.addStretch()

        btn = QPushButton(tr("ok"))
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(120)
        btn.setStyleSheet(
            f"background-color: {color};color: white;"
            f"border: none;border-radius: 12px;font-size: 12px;"
            f"font-weight: 600;padding: 0px 24px;"
        )
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

        self.setWindowTitle(tr("attendance_title"))
        self.resize(1000, 700)
        self.setMinimumSize(600, 500)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("attendanceWindow")

        self.load_user_data()
        self.setup_ui()

        signals.employee_added.connect(self.on_employee_changed)
        signals.employee_removed.connect(self.on_employee_changed)
        signals.employee_updated.connect(self.on_employee_changed)

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    # =====================================================
    # THEME / LANGUAGE
    # =====================================================

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()
        self.refresh_my_attendance()
        if self.is_owner:
            self.refresh_employees_attendance()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("attendance_title"))
        QTimer.singleShot(0, self._rebuild)

    def _rebuild(self):
        old = self.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
        self.setup_ui()

    def on_employee_changed(self, complex_id):
        if complex_id != self.complex_id:
            return
        if self.is_owner:
            try:
                self.refresh_employees_attendance()
            except Exception as e:
                print("REFRESH EMP ATTENDANCE ERROR:", e)

    # =====================================================
    # LOAD USER
    # =====================================================

    def load_user_data(self):
        try:
            user = self.db.fetch_one(
                "SELECT userId FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if not user:
                return

            self.user_id = user["userId"]

            rows = self.db.fetch_all(
                """
                SELECT c.complexId, c.name, cm.memberId, cm.role,
                       ep.workStartTime, ep.workEndTime
                FROM complexes c
                INNER JOIN complex_members cm ON cm.complexId = c.complexId
                LEFT JOIN employee_profiles ep ON ep.memberId = cm.memberId
                WHERE cm.userId = %s AND cm.isActive = '1' AND c.isActive = '1'
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
                    self.work_start = QTime(st.seconds // 3600, (st.seconds % 3600) // 60, 0)
            except Exception:
                pass
        if et:
            try:
                if isinstance(et, str):
                    parts = et.split(":")
                    self.work_end = QTime(int(parts[0]), int(parts[1]), 0)
                else:
                    self.work_end = QTime(et.seconds // 3600, (et.seconds % 3600) // 60, 0)
            except Exception:
                pass

    def make_rounded_scroll(self, content_widget):
        scroll = QScrollArea()
        scroll.setObjectName("attendanceScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        vbar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(vbar)

        scroll.setWidget(content_widget)
        return scroll

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 15, 22, 15)
        main_layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(10)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(1)

        title = QLabel(tr("attendance_title"))
        title.setObjectName("attTitle")

        subtitle = QLabel(tr("attendance_subtitle"))
        subtitle.setObjectName("attSubtitle")

        title_text_layout.addWidget(title)
        title_text_layout.addWidget(subtitle)

        back_button = QPushButton("›")
        back_button.setObjectName("attBackBtn")
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.close)

        title_layout.setDirection(QBoxLayout.LeftToRight)
        title_layout.addWidget(back_button)
        title_layout.addLayout(title_text_layout)

        header.addLayout(title_layout)
        header.addStretch()

        if len(self.complexes) > 1:
            self.complex_combo = RoundedComboBox()
            self.complex_combo.setObjectName("attComplexCombo")
            self.complex_combo.setFixedHeight(42)
            self.complex_combo.setMinimumWidth(200)
            self.complex_combo.setAttribute(Qt.WA_StyledBackground, True)
            self.complex_combo.setCursor(Qt.PointingHandCursor)
            for c in self.complexes:
                self.complex_combo.addItem(c["name"], c["complexId"])
            for i, c in enumerate(self.complexes):
                if c["complexId"] == self.complex_id:
                    self.complex_combo.setCurrentIndex(i)
                    break
            self.complex_combo.currentIndexChanged.connect(self.on_complex_changed)
            header.addWidget(self.complex_combo)

        main_layout.addLayout(header)

        self.is_owner = self.role in ("owner", "both")

        if self.is_owner:
            tabs = QHBoxLayout()
            tabs.setSpacing(6)

            self.my_tab_btn = QPushButton(tr("my_attendance"))
            self.my_tab_btn.setObjectName("tabButton")
            self.my_tab_btn.setFixedHeight(40)
            self.my_tab_btn.setCursor(Qt.PointingHandCursor)
            self.my_tab_btn.setAttribute(Qt.WA_StyledBackground, True)
            self.my_tab_btn.clicked.connect(lambda: self.switch_tab(0))

            self.emp_tab_btn = QPushButton(tr("employees_attendance"))
            self.emp_tab_btn.setObjectName("tabButton")
            self.emp_tab_btn.setFixedHeight(40)
            self.emp_tab_btn.setCursor(Qt.PointingHandCursor)
            self.emp_tab_btn.setAttribute(Qt.WA_StyledBackground, True)
            self.emp_tab_btn.clicked.connect(lambda: self.switch_tab(1))

            tabs.addWidget(self.my_tab_btn)
            tabs.addWidget(self.emp_tab_btn)
            tabs.addStretch()

            main_layout.addLayout(tabs)

            self.stack = QStackedWidget()
            self.stack.addWidget(self.build_my_attendance_tab())
            self.stack.addWidget(self.build_employees_tab())

            main_layout.addWidget(self.stack, 1)

            self.refresh_my_attendance()
            self.switch_tab(0)
        else:
            self.stack = QStackedWidget()
            self.stack.addWidget(self.build_my_attendance_tab())
            main_layout.addWidget(self.stack, 1)

        self.apply_stylesheet()

    # =====================================================
    # STYLESHEET
    # =====================================================

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""
            QWidget#attendanceWindow {{
                background-color: {c['bg_main']};
                font-family: "Vazirmatn";
                color: {c['text_main']};
            }}
            QWidget#attendanceWindow QLabel {{ background: transparent; }}

            QLabel#attTitle {{
                font-size: 21px;
                font-weight: 700;
                color: {c['text_main']};
                background: transparent;
            }}
            QLabel#attSubtitle {{
                font-size: 10px;
                color: {c['text_dim']};
                background: transparent;
            }}

            QPushButton#attBackBtn {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 21px;
                color: {c['accent']};
                font-size: 22px;
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton#attBackBtn:hover {{
                background-color: {c['bg_hover']};
                border-color: {c['border_hover']};
            }}

            QComboBox#attComplexCombo {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 21px;
                padding: 0 18px;
                color: {c['text_main']};
                font-size: 12px;
                font-weight: 600;
            }}
            QComboBox#attComplexCombo:hover {{
                border-color: {c['accent']};
                background-color: {c['bg_hover']};
            }}
            QComboBox#attComplexCombo::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border: none;
                background: transparent;
            }}
            QComboBox#attComplexCombo::down-arrow {{
                image: none;
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {c['accent']};
                margin-right: 10px;
            }}

            QPushButton#tabButton {{
                background-color: {c['bg_card']};
                color: {c['text_dim']};
                border: 1px solid {c['border']};
                border-radius: 20px;
                padding: 0 24px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton#tabButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton#tabButton[selected="true"] {{
                background-color: {c['accent']};
                color: white;
                border: 1px solid {c['accent']};
            }}

            QFrame#todayCard {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 24px;
            }}

            QLabel#todayTime {{
                color: {c['accent']};
                font-size: 48px;
                font-weight: 800;
                background: transparent;
            }}
            QLabel#todayDate {{
                color: {c['text_main']};
                font-size: 15px;
                font-weight: 700;
                background: transparent;
            }}
            QLabel#todayStatus {{
                color: {c['text_dim']};
                font-size: 12px;
                background: transparent;
            }}

            QPushButton#checkInButton {{
                background-color: #16A34A;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 0 40px;
                font-size: 13px;
                font-weight: 700;
                min-height: 44px;
            }}
            QPushButton#checkInButton:hover {{ background-color: #15803D; }}
            QPushButton#checkInButton:disabled {{ background-color: #B8C9DD; }}

            QPushButton#checkOutButton {{
                background-color: #D93025;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 0 40px;
                font-size: 13px;
                font-weight: 700;
                min-height: 44px;
            }}
            QPushButton#checkOutButton:hover {{ background-color: #B71C1C; }}
            QPushButton#checkOutButton:disabled {{ background-color: #B8C9DD; }}

            QPushButton#addOvertimeButton {{
                background-color: {c['accent_light']};
                color: {c['accent']};
                border: 1px solid {c['accent']};
                border-radius: 22px;
                padding: 0 24px;
                font-size: 13px;
                font-weight: 700;
                min-height: 44px;
            }}
            QPushButton#addOvertimeButton:hover {{ background-color: {c['bg_hover']}; }}

            QLabel#sectionTitle {{
                color: {c['text_main']};
                font-size: 15px;
                font-weight: 700;
                background: transparent;
            }}

            QFrame#historyCard {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 20px;
            }}
            QFrame#historyCard:hover {{
                border-color: {c['border_hover']};
                background-color: {c['bg_hover']};
            }}

            QLabel#historyDate {{
                color: {c['text_main']};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }}
            QLabel#historyTime {{
                color: {c['text_dim']};
                font-size: 11px;
                background: transparent;
            }}
            QLabel#historyHours {{
                color: {c['accent']};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }}
            QLabel#historyOvertime {{
                color: {c['accent']};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }}

            QLabel#approvedBadge {{
                color: #21844A;
                background-color: {c['success_bg']};
                border: none;
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: 700;
            }}
            QLabel#pendingBadge {{
                color: {c['accent']};
                background-color: {c['accent_light']};
                border: none;
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: 700;
            }}
            QLabel#rejectedBadge {{
                color: #E63946;
                background-color: #FFE5E8;
                border: none;
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: 700;
            }}

            QFrame#filterBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 20px;
            }}

            QFrame#persianDateFrame {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 21px;
            }}
            QFrame#persianDateFrame:hover {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border_hover']};
            }}

            QLabel#dateIconLabel {{
                background-color: {c['accent_light']};
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
            }}

            QPushButton#persianDateButton {{
                background-color: transparent;
                border: none;
                padding: 0 4px;
                color: {c['text_main']};
                font-size: 12px;
                font-weight: 700;
                text-align: center;
            }}

            QPushButton#refreshButton {{
                background-color: {c['accent_light']};
                color: {c['accent']};
                border: 1px solid {c['border_hover']};
                border-radius: 21px;
                padding: 0 20px;
                font-size: 12px;
                font-weight: 600;
                min-height: 42px;
            }}
            QPushButton#refreshButton:hover {{ background-color: {c['bg_hover']}; }}

            QPushButton#editButton {{
                background-color: {c['accent_light']};
                color: {c['accent']};
                border: none;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 600;
                min-height: 28px;
            }}
            QPushButton#editButton:hover {{ background-color: {c['bg_hover']}; }}

            QPushButton#approveButton {{
                background-color: {c['success_bg']};
                color: {c['success']};
                border: none;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
                min-height: 28px;
            }}
            QPushButton#approveButton:hover {{ background-color: {c['bg_hover']}; }}

            QPushButton#rejectButton {{
                background-color: #FFE5E8;
                color: #D93025;
                border: none;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
                min-height: 28px;
            }}
            QPushButton#rejectButton:hover {{ background-color: {c['bg_hover']}; }}

            QPushButton#saveButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 6px 16px;
                font-size: 11px;
                font-weight: 700;
                min-height: 28px;
            }}
            QPushButton#saveButton:hover {{ background-color: {c['accent_hover']}; }}

            QFrame#emptyCard {{
                background-color: {c['bg_card']};
                border: 1px dashed {c['border']};
                border-radius: 20px;
            }}
            QLabel#emptyText {{
                color: {c['text_dim']};
                font-size: 12px;
                background: transparent;
            }}

            QScrollArea {{
                background: transparent;
                border: none;
                border-radius: 16px;
            }}
            QScrollArea > QWidget {{
                background: transparent;
                border-radius: 16px;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
                border-radius: 16px;
            }}
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
    # BUILD MY ATTENDANCE TAB
    # =====================================================

    def build_my_attendance_tab(self):
        widget = QWidget()
        widget.setObjectName("myAttendanceTab")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        today_card = QFrame()
        today_card.setObjectName("todayCard")
        today_card.setAttribute(Qt.WA_StyledBackground, True)
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

        self.entry_box, self.entry_value = self.create_time_box(tr("entry"))
        self.exit_box, self.exit_value = self.create_time_box(tr("exit"))
        self.work_box, self.work_value = self.create_time_box(tr("worked_time"))

        info_layout.addWidget(self.entry_box)
        info_layout.addWidget(self.exit_box)
        info_layout.addWidget(self.work_box)
        today_layout.addLayout(info_layout)

        calc_layout = QHBoxLayout()
        calc_layout.setSpacing(8)

        self.delay_box, self.delay_value = self.create_small_box(tr("delay"), "0")
        self.overtime_box, self.overtime_value = self.create_small_box("اضافه کاری", "0")
        self.remaining_box, self.remaining_value = self.create_small_box(tr("remaining"), "—")

        calc_layout.addWidget(self.delay_box)
        calc_layout.addWidget(self.overtime_box)
        calc_layout.addWidget(self.remaining_box)
        today_layout.addLayout(calc_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.entry_button = QPushButton(tr("check_in"))
        self.entry_button.setObjectName("checkInButton")
        self.entry_button.setFixedHeight(44)
        self.entry_button.setCursor(Qt.PointingHandCursor)
        self.entry_button.clicked.connect(self.register_entry)

        self.exit_button = QPushButton(tr("check_out"))
        self.exit_button.setObjectName("checkOutButton")
        self.exit_button.setFixedHeight(44)
        self.exit_button.setCursor(Qt.PointingHandCursor)
        self.exit_button.clicked.connect(self.register_exit)

        buttons_layout.addWidget(self.entry_button)
        buttons_layout.addWidget(self.exit_button)
        today_layout.addLayout(buttons_layout)

        layout.addWidget(today_card)

        add_ot_row = QHBoxLayout()
        add_ot_row.setSpacing(8)

        self.add_ot_btn = QPushButton(tr("add_overtime"))
        self.add_ot_btn.setObjectName("addOvertimeButton")
        self.add_ot_btn.setFixedHeight(44)
        self.add_ot_btn.setCursor(Qt.PointingHandCursor)
        self.add_ot_btn.clicked.connect(self.open_add_overtime_dialog)

        add_ot_row.addWidget(self.add_ot_btn)
        add_ot_row.addStretch()
        layout.addLayout(add_ot_row)

        self.history_title = QLabel(tr("history_title"))
        self.history_title.setObjectName("sectionTitle")
        layout.addWidget(self.history_title)

        history_content = QWidget()
        self.my_history_layout = QVBoxLayout(history_content)
        self.my_history_layout.setContentsMargins(4, 4, 12, 4)
        self.my_history_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(history_content)
        layout.addWidget(scroll, 1)

        return widget

    # =====================================================
    # BUILD EMPLOYEES TAB
    # =====================================================

    def build_employees_tab(self):
        widget = QWidget()
        widget.setObjectName("employeesAttendanceTab")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        filter_box = QFrame()
        filter_box.setObjectName("filterBox")
        filter_box.setAttribute(Qt.WA_StyledBackground, True)

        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(10)

        self.date_label_filter = QLabel(tr("date_filter"))
        self.date_label_filter.setStyleSheet(
            f"color: {theme_manager.colors()['text_dim']};"
            f"font-size: 12px; font-weight: 600; background: transparent;"
        )

        self.date_filter = PersianDateButton()
        self.date_filter.dateChanged.connect(self.refresh_employees_attendance)

        self.refresh_button = QPushButton(tr("refresh"))
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.on_refresh_clicked)

        filter_layout.addWidget(self.date_label_filter)
        filter_layout.addWidget(self.date_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(self.refresh_button)

        layout.addWidget(filter_box)

        emp_content = QWidget()
        self.emp_list_layout = QVBoxLayout(emp_content)
        self.emp_list_layout.setContentsMargins(4, 4, 12, 4)
        self.emp_list_layout.setSpacing(8)

        scroll = self.make_rounded_scroll(emp_content)
        layout.addWidget(scroll, 1)

        return widget

    def on_refresh_clicked(self):
        self.refresh_employees_attendance()
        NiceMessageBox.success(self, "بروزرسانی", "بروزرسانی با موفقیت انجام شد.")

    # =====================================================
    # TIME BOXES
    # =====================================================

    def create_time_box(self, title_text):
        c = theme_manager.colors()

        box = QFrame()
        box.setObjectName("timeBox")
        box.setAttribute(Qt.WA_StyledBackground, True)
        box.setFixedHeight(72)
        box.setStyleSheet(f"""
            QFrame#timeBox {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 36px;
            }}
        """)

        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(3)

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(22)
        title.setStyleSheet(
            f"color: {c['text_dim']};font-size: 9px;background-color: {c['bg_card']};"
            f"border: none;border-radius: 11px;padding: 0px 12px;"
        )

        value = QLabel("—")
        value.setAlignment(Qt.AlignCenter)
        value.setFixedHeight(30)
        value.setStyleSheet(
            f"color: {c['text_main']};font-size: 15px;font-weight: 700;"
            f"background-color: {c['bg_card']};border: none;"
            f"border-radius: 15px;padding: 0px 12px;"
        )

        layout.addWidget(title, 0, Qt.AlignCenter)
        layout.addWidget(value, 0, Qt.AlignCenter)

        return box, value

    def create_small_box(self, title_text, value_text):
        c = theme_manager.colors()

        box = QFrame()
        box.setObjectName("smallBox")
        box.setAttribute(Qt.WA_StyledBackground, True)
        box.setFixedHeight(62)
        box.setStyleSheet(f"""
            QFrame#smallBox {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 31px;
            }}
        """)

        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(21)
        title.setStyleSheet(
            f"color: {c['text_dim']};font-size: 9px;"
            f"background-color: {c['bg_card']};border: none;"
            f"border-radius: 10px;padding: 0px 11px;"
        )

        value = QLabel(value_text)
        value.setAlignment(Qt.AlignCenter)
        value.setFixedHeight(26)
        value.setStyleSheet(
            f"color: {c['accent']};font-size: 11px;font-weight: 700;"
            f"background-color: {c['bg_card']};border: none;"
            f"border-radius: 13px;padding: 0px 10px;"
        )

        layout.addWidget(title, 0, Qt.AlignCenter)
        layout.addWidget(value, 0, Qt.AlignCenter)

        return box, value

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
            SELECT attendanceId, checkIn, checkOut, workedMinutes,
                   overtimeMinutes, status, approvalStatus
            FROM attendance
            WHERE memberId = %s AND workDate = %s
            ORDER BY attendanceId DESC LIMIT 1
            """,
            (self.member_id, today_str)
        )

        self.entry_value.setText("—")
        self.exit_value.setText("—")
        self.work_value.setText("—")

        self.entry_time = None
        self.exit_time = None

        if not record or not record["checkIn"]:
            self.entry_button.setEnabled(True)
            self.exit_button.setEnabled(False)
            self.today_status_label.setText(tr("no_check_in_yet"))
            self.delay_value.setText("0")
            self.overtime_value.setText("0")
            self.remaining_value.setText("—")

        elif not record["checkOut"]:
            self.entry_button.setEnabled(False)
            self.exit_button.setEnabled(True)

            ci = record["checkIn"]
            if isinstance(ci, datetime):
                self.entry_time = QTime(ci.hour, ci.minute, 0)
                ci_text = ci.strftime("%H:%M")
            else:
                ci_text = str(ci)[:5]

            self.entry_value.setText(ci_text)
            self.today_status_label.setText(tr("checked_in_at", time=ci_text))

        else:
            self.entry_button.setEnabled(False)
            self.exit_button.setEnabled(False)

            ci = record["checkIn"]
            co = record["checkOut"]
            ci_text = ci.strftime("%H:%M") if isinstance(ci, datetime) else str(ci)[:5]
            co_text = co.strftime("%H:%M") if isinstance(co, datetime) else str(co)[:5]

            self.entry_value.setText(ci_text)
            self.exit_value.setText(co_text)

            wm = record["workedMinutes"] or 0
            h, m = wm // 60, wm % 60
            self.work_value.setText(f"{h}{tr('hour_short')} {m}{tr('min_short')}")
            self.today_status_label.setText(tr("day_complete"))
            self.delay_value.setText("—")
            self.overtime_value.setText("—")
            self.remaining_value.setText("✓")

        while self.my_history_layout.count():
            item = self.my_history_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        history = self.db.fetch_all(
            """
            SELECT workDate, checkIn, checkOut, workedMinutes,
                   overtimeMinutes, approvalStatus
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
            empty.setAttribute(Qt.WA_StyledBackground, True)
            empty.setMinimumHeight(100)
            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)
            t = QLabel(tr("no_history"))
            t.setObjectName("emptyText")
            t.setAlignment(Qt.AlignCenter)
            el.addWidget(t)
            self.my_history_layout.addWidget(empty)
            self.my_history_layout.addStretch()
            return

        for row in history:
            card = self.create_history_card(row, is_owner=self.is_owner)
            self.my_history_layout.addWidget(card)

        self.my_history_layout.addStretch()

    # =====================================================
    # HISTORY CARD
    # =====================================================

    def create_history_card(self, row, is_owner=False):
        card = QFrame()
        card.setObjectName("historyCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(60)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        work_date = row["workDate"]
        if isinstance(work_date, date):
            qdate = QDate(work_date.year, work_date.month, work_date.day)
            date_str = jalali_string(qdate)
        else:
            date_str = str(work_date)

        date_label = QLabel(date_str)
        date_label.setObjectName("historyDate")
        layout.addWidget(date_label, 2)

        ci = row["checkIn"]
        co = row["checkOut"]
        ci_text = ci.strftime("%H:%M") if isinstance(ci, datetime) else (str(ci)[:5] if ci else "—")
        co_text = co.strftime("%H:%M") if isinstance(co, datetime) else (str(co)[:5] if co else "—")

        in_label = QLabel(f"{tr('entry')}: {ci_text}")
        in_label.setObjectName("historyTime")
        out_label = QLabel(f"{tr('exit')}: {co_text}")
        out_label.setObjectName("historyTime")

        layout.addWidget(in_label, 1)
        layout.addWidget(out_label, 1)

        wm = row["workedMinutes"] or 0
        h, m = wm // 60, wm % 60
        hours_label = QLabel(f"{h}{tr('hour_short')} {m}{tr('min_short')}")
        hours_label.setObjectName("historyHours")
        layout.addWidget(hours_label, 1)

        ot = row.get("overtimeMinutes") or 0
        if ot > 0:
            ot_h, ot_m = ot // 60, ot % 60
            ot_label = QLabel(f"اضافه کاری: {ot_h}{tr('hour_short')} {ot_m}{tr('min_short')}")
            ot_label.setObjectName("historyOvertime")
            layout.addWidget(ot_label, 1)

        approval = row.get("approvalStatus") or "pending"

        if is_owner and approval == "pending":
            badge = QLabel(tr("approved"))
            badge.setObjectName("approvedBadge")
        elif approval == "approved":
            badge = QLabel(tr("approved"))
            badge.setObjectName("approvedBadge")
        elif approval == "rejected":
            badge = QLabel(tr("rejected"))
            badge.setObjectName("rejectedBadge")
        else:
            badge = QLabel(tr("pending"))
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

        record = self.db.fetch_one(
            """
            SELECT attendanceId, checkIn
            FROM attendance
            WHERE memberId = %s AND workDate = %s
            ORDER BY attendanceId DESC LIMIT 1
            """,
            (self.member_id, today_str)
        )

        if record and record.get("checkIn"):
            self.refresh_my_attendance()
            return

        now = datetime.now()
        status = 'approved' if self.is_owner else 'pending'

        if record:
            self.db.execute(
                """
                UPDATE attendance
                SET checkIn = %s, status = 'present', approvalStatus = %s
                WHERE attendanceId = %s
                """,
                (now, status, record["attendanceId"])
            )
        else:
            self.db.execute(
                """
                INSERT INTO attendance (memberId, workDate, checkIn, status, approvalStatus)
                VALUES (%s, %s, %s, 'present', %s)
                """,
                (self.member_id, today_str, now, status)
            )

        NiceMessageBox.success(
            self, tr("check_in_success"),
            tr("checked_in_at", time=now.strftime('%H:%M'))
        )
        self.refresh_my_attendance()
        signals.data_changed.emit("attendance")

    def register_exit(self):
        if not self.member_id:
            return

        today = QDate.currentDate()
        today_str = today.toString("yyyy-MM-dd")

        record = self.db.fetch_one(
            """
            SELECT attendanceId, checkIn, checkOut
            FROM attendance
            WHERE memberId = %s AND workDate = %s
            ORDER BY attendanceId DESC LIMIT 1
            """,
            (self.member_id, today_str)
        )

        if not record or not record.get("checkIn"):
            NiceMessageBox.error(self, tr("error"), tr("not_checked_in_msg"))
            return

        if record.get("checkOut"):
            self.refresh_my_attendance()
            return

        now = datetime.now()
        ci = record["checkIn"]

        worked_minutes = 0
        if isinstance(ci, datetime):
            delta = now - ci
            worked_minutes = max(0, int(delta.total_seconds() // 60))

        status = 'approved' if self.is_owner else 'pending'

        self.db.execute(
            """
            UPDATE attendance
            SET checkOut = %s, workedMinutes = %s, approvalStatus = %s
            WHERE attendanceId = %s
            """,
            (now, worked_minutes, status, record["attendanceId"])
        )

        h, m = worked_minutes // 60, worked_minutes % 60

        NiceMessageBox.success(
            self, tr("check_out_success"),
            tr("check_out_msg", h=h, m=m)
        )
        self.refresh_my_attendance()
        signals.data_changed.emit("attendance")

    # =====================================================
    # ADD OVERTIME DIALOG
    # =====================================================

    def open_add_overtime_dialog(self):
        if not self.member_id:
            return

        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("add_overtime_title"))
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(450)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(10)

        title = QLabel(tr("add_overtime_title"))
        title.setStyleSheet(f"color: {c['text_main']}; font-size: 16px; font-weight: 700; background: transparent;")
        layout.addWidget(title)

        subtitle = QLabel(tr("add_overtime_sub"))
        subtitle.setStyleSheet(f"color: {c['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(subtitle)
        layout.addSpacing(6)

        date_lbl = QLabel(tr("date"))
        date_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        date_picker = PersianDateButton()

        layout.addWidget(date_lbl)
        layout.addWidget(date_picker)
        layout.addSpacing(6)

        time_lbl = QLabel(tr("duration"))
        time_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(time_lbl)

        time_row = QHBoxLayout()
        time_row.setSpacing(8)

        h_col = QVBoxLayout()
        h_lbl = QLabel(tr("hours"))
        h_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 10px; background: transparent;")
        h_input = QLineEdit()
        h_input.setFixedHeight(44)
        h_input.setPlaceholderText("0")
        h_input.setLayoutDirection(Qt.LeftToRight)
        h_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
                padding: 0 16px;
                color: {c['text_main']};
                font-size: 14px;
                font-weight: 700;
            }}
            QLineEdit:focus {{
                background: {c['bg_card']};
                border: 2px solid {c['accent']};
            }}
        """)
        h_col.addWidget(h_lbl)
        h_col.addWidget(h_input)

        m_col = QVBoxLayout()
        m_lbl = QLabel(tr("minutes"))
        m_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 10px; background: transparent;")
        m_input = QLineEdit()
        m_input.setFixedHeight(44)
        m_input.setPlaceholderText("0")
        m_input.setLayoutDirection(Qt.LeftToRight)
        m_input.setStyleSheet(h_input.styleSheet())
        m_col.addWidget(m_lbl)
        m_col.addWidget(m_input)

        time_row.addLayout(h_col, 1)
        time_row.addLayout(m_col, 1)
        layout.addLayout(time_row)
        layout.addSpacing(6)

        desc_lbl = QLabel(tr("description_optional"))
        desc_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        desc_input = QLineEdit()
        desc_input.setFixedHeight(44)
        desc_input.setPlaceholderText(tr("description_ph"))
        desc_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
                padding: 0 16px;
                color: {c['text_main']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                background: {c['bg_card']};
                border: 2px solid {c['accent']};
            }}
        """)

        layout.addWidget(desc_lbl)
        layout.addWidget(desc_input)
        layout.addSpacing(10)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        cancel_btn = QPushButton(tr("cancel"))
        cancel_btn.setFixedHeight(46)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_input']};
                color: {c['text_dim']};
                border: 1px solid {c['border']};
                border-radius: 23px;
                padding: 0 26px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
        """)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = QPushButton(tr("save"))
        save_btn.setFixedHeight(46)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 23px;
                padding: 0 30px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {c['accent_hover']}; }}
        """)

        def on_save():
            h_text = h_input.text().strip()
            m_text = m_input.text().strip()
            desc_text = desc_input.text().strip()

            try:
                hours = int(h_text) if h_text else 0
            except ValueError:
                NiceMessageBox.error(dialog, tr("error"), tr("invalid_hours"))
                return
            try:
                mins = int(m_text) if m_text else 0
            except ValueError:
                NiceMessageBox.error(dialog, tr("error"), tr("invalid_minutes"))
                return

            if hours < 0 or mins < 0:
                NiceMessageBox.error(dialog, tr("error"), tr("negative_not_allowed"))
                return
            if mins >= 60:
                NiceMessageBox.error(dialog, tr("error"), tr("minutes_under_60"))
                return

            total_minutes = hours * 60 + mins
            if total_minutes <= 0:
                NiceMessageBox.error(dialog, tr("error"), tr("enter_overtime"))
                return

            selected_qdate = date_picker.date()
            selected_date_str = selected_qdate.toString("yyyy-MM-dd")

            existing = self.db.fetch_one(
                """
                SELECT attendanceId, overtimeMinutes
                FROM attendance
                WHERE memberId = %s AND workDate = %s
                ORDER BY attendanceId DESC LIMIT 1
                """,
                (self.member_id, selected_date_str)
            )

            if existing:
                new_ot = int(existing.get("overtimeMinutes") or 0) + total_minutes
                self.db.execute(
                    """
                    UPDATE attendance
                    SET overtimeMinutes = %s, description = %s
                    WHERE attendanceId = %s
                    """,
                    (new_ot, desc_text or None, existing["attendanceId"])
                )
            else:
                self.db.execute(
                    """
                    INSERT INTO attendance
                    (memberId, workDate, overtimeMinutes, status, description, approvalStatus)
                    VALUES (%s, %s, %s, 'present', %s, 'pending')
                    """,
                    (self.member_id, selected_date_str, total_minutes, desc_text or None)
                )

            dialog.accept()
            NiceMessageBox.success(
                self, tr("overtime_added"),
                tr("overtime_added_msg", h=hours, m=mins)
            )
            self.refresh_my_attendance()

        save_btn.clicked.connect(on_save)
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

        dialog.setStyleSheet(f"QDialog {{ background-color: {c['bg_main']}; font-family: 'Vazirmatn'; }}")
        dialog.exec()

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
        self.work_value.setText(f"{h}{tr('hour_short')} {m}{tr('min_short')}")
        self.calculate_delay()
        self.calculate_overtime()

    def calculate_delay(self):
        if not self.entry_time:
            return
        delay_seconds = self.work_start.secsTo(self.entry_time)
        if delay_seconds <= 0:
            text = "0"
        else:
            minutes = delay_seconds // 60
            h, m = minutes // 60, minutes % 60
            text = f"{h}{tr('hour_short')} {m}{tr('min_short')}" if h > 0 else f"{m}{tr('min_short')}"
        self.delay_value.setText(text)

    def calculate_overtime(self):
        if not self.entry_time:
            return
        current_time = self.current_minute_time()
        ot_seconds = self.work_end.secsTo(current_time)
        if ot_seconds <= 0:
            text = "0"
        else:
            minutes = ot_seconds // 60
            h, m = minutes // 60, minutes % 60
            text = f"{h}{tr('hour_short')} {m}{tr('min_short')}" if h > 0 else f"{m}{tr('min_short')}"
        self.overtime_value.setText(text)

    # =====================================================
    # EMPLOYEES ATTENDANCE
    # =====================================================

    def refresh_employees_attendance(self):
        if not self.is_owner or not self.complex_id:
            return

        while self.emp_list_layout.count():
            item = self.emp_list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        selected_qdate = self.date_filter.date()
        selected_str = selected_qdate.toString("yyyy-MM-dd")

        rows = self.db.fetch_all(
            """
            SELECT cm.memberId, u.name, u.phoneNumber, a.attendanceId,
                   a.workDate, a.checkIn, a.checkOut, a.workedMinutes,
                   a.overtimeMinutes, a.approvalStatus, a.description
            FROM complex_members cm
            INNER JOIN users u ON u.userId = cm.userId
            LEFT JOIN attendance a ON a.memberId = cm.memberId AND a.workDate = %s
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
            empty.setAttribute(Qt.WA_StyledBackground, True)
            empty.setMinimumHeight(120)
            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)
            t = QLabel(tr("no_employees"))
            t.setObjectName("emptyText")
            t.setAlignment(Qt.AlignCenter)
            el.addWidget(t)
            self.emp_list_layout.addWidget(empty)
            self.emp_list_layout.addStretch()
            return

        for row in rows:
            card = self.create_employee_attendance_card(row)
            self.emp_list_layout.addWidget(card)

        self.emp_list_layout.addStretch()

    def create_employee_attendance_card(self, row):
        c = theme_manager.colors()

        card = QFrame()
        card.setObjectName("historyCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(96)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(18, 14, 18, 14)
        outer.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        name_text = row.get("name") or "—"
        initial = name_text.strip()[0] if name_text.strip() else "?"
        avatar = QLabel(initial)
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"background-color: {c['accent_light']}; color: {c['accent']}; border: none; border-radius: 19px; font-size: 15px; font-weight: 800;")
        top_row.addWidget(avatar)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        name_label = QLabel(name_text)
        name_label.setStyleSheet(f"color: {c['text_main']}; font-size: 13px; font-weight: 700; background: transparent;")
        phone = row.get("phoneNumber") or ""
        phone_label = QLabel(phone)
        phone_label.setStyleSheet(f"color: {c['text_dim']}; font-size: 10px; background: transparent;")
        info_col.addWidget(name_label)
        info_col.addWidget(phone_label)
        top_row.addLayout(info_col, 2)

        ci = row.get("checkIn")
        co = row.get("checkOut")
        ci_text = ci.strftime("%H:%M") if isinstance(ci, datetime) else (str(ci)[:5] if ci else "—")
        co_text = co.strftime("%H:%M") if isinstance(co, datetime) else (str(co)[:5] if co else "—")

        time_box = QFrame()
        time_box.setStyleSheet(f"background-color: {c['bg_input']}; border: none; border-radius: 14px;")
        tb_layout = QHBoxLayout(time_box)
        tb_layout.setContentsMargins(10, 4, 10, 4)
        tb_layout.setSpacing(6)

        in_lbl = QLabel(f"ورود: {ci_text}")
        in_lbl.setStyleSheet(f"color: {c['text_main']}; font-size: 11px; font-weight: 700; background: transparent;")
        sep = QLabel("|")
        sep.setStyleSheet(f"color: {c['border']}; font-size: 12px; background: transparent;")
        out_lbl = QLabel(f"خروج: {co_text}")
        out_lbl.setStyleSheet(f"color: {c['text_main']}; font-size: 11px; font-weight: 700; background: transparent;")

        tb_layout.addWidget(in_lbl)
        tb_layout.addWidget(sep)
        tb_layout.addWidget(out_lbl)
        top_row.addWidget(time_box, 2)

        outer.addLayout(top_row)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        wm = row.get("workedMinutes") or 0
        h, m = wm // 60, wm % 60

        worked_lbl = QLabel(f"ساعت کار: {h}{tr('hour_short')} {m}{tr('min_short')}")
        worked_lbl.setStyleSheet(f"color: {c['accent']}; font-size: 11px; font-weight: 700; background-color: {c['accent_light']}; border: none; border-radius: 10px; padding: 4px 10px;")
        bottom_row.addWidget(worked_lbl)

        ot = row.get("overtimeMinutes") or 0
        if ot > 0:
            ot_h, ot_m = ot // 60, ot % 60
            ot_label = QLabel(f"اضافه کاری: {ot_h}{tr('hour_short')} {ot_m}{tr('min_short')}")
            ot_label.setStyleSheet(f"color: {c['accent']}; font-size: 11px; font-weight: 700; background-color: {c['accent_light']}; border: none; border-radius: 10px; padding: 4px 10px;")
            bottom_row.addWidget(ot_label)

        bottom_row.addStretch()

        approval = row.get("approvalStatus")
        has_checkin = bool(row.get("checkIn"))
        has_checkout = bool(row.get("checkOut"))

        if approval == "approved":
            badge = QLabel(tr("approved"))
            badge.setObjectName("approvedBadge")
        elif approval == "rejected":
            badge = QLabel(tr("rejected"))
            badge.setObjectName("rejectedBadge")
        elif has_checkin:
            badge = QLabel(tr("pending"))
            badge.setObjectName("pendingBadge")
        else:
            badge = QLabel(tr("absent"))
            badge.setObjectName("rejectedBadge")

        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(24)
        bottom_row.addWidget(badge)

        selected_date = self.date_filter.date()
        is_today = (selected_date == QDate.currentDate())

        if is_today:
            if not has_checkin:
                in_btn = QPushButton("ثبت ورود")
                in_btn.setObjectName("approveButton")
                in_btn.setCursor(Qt.PointingHandCursor)
                in_btn.clicked.connect(lambda checked=False, r=row: self.owner_register_entry(r))
                bottom_row.addWidget(in_btn)
            elif has_checkin and not has_checkout:
                out_btn = QPushButton("ثبت خروج")
                out_btn.setObjectName("rejectButton")
                out_btn.setCursor(Qt.PointingHandCursor)
                out_btn.clicked.connect(lambda checked=False, r=row: self.owner_register_exit(r))
                bottom_row.addWidget(out_btn)

        if approval == "pending" and row.get("attendanceId"):
            approve_btn = QPushButton(tr("approve"))
            approve_btn.setObjectName("approveButton")
            approve_btn.setCursor(Qt.PointingHandCursor)
            approve_btn.clicked.connect(lambda checked=False, r=row: self.approve_attendance(r))
            bottom_row.addWidget(approve_btn)

            reject_btn = QPushButton(tr("reject"))
            reject_btn.setObjectName("rejectButton")
            reject_btn.setCursor(Qt.PointingHandCursor)
            reject_btn.clicked.connect(lambda checked=False, r=row: self.reject_attendance(r))
            bottom_row.addWidget(reject_btn)

        edit_button = QPushButton(tr("edit"))
        edit_button.setObjectName("editButton")
        edit_button.setCursor(Qt.PointingHandCursor)
        edit_button.clicked.connect(lambda checked=False, r=row: self.open_edit_dialog(r))
        bottom_row.addWidget(edit_button)

        save_button = QPushButton(tr("save_btn"))
        save_button.setObjectName("saveButton")
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.clicked.connect(lambda checked=False, r=row: self.save_attendance_row(r))
        bottom_row.addWidget(save_button)

        outer.addLayout(bottom_row)

        return card

    def owner_register_entry(self, row):
        member_id = row.get("memberId")
        if not member_id:
            return

        if self.date_filter.date() != QDate.currentDate():
            NiceMessageBox.error(self, "خطا", "فقط برای امروز می‌توانید ورود ثبت کنید.")
            return

        today = QDate.currentDate()
        today_str = today.toString("yyyy-MM-dd")
        now = datetime.now()
        entry_dt = datetime(
            today.year(), today.month(), today.day(),
            now.hour, now.minute, now.second
        )

        attendance_id = row.get("attendanceId")
        if attendance_id:
            self.db.execute(
                """
                UPDATE attendance
                SET checkIn = %s, status = 'present',
                    approvalStatus = 'approved', approvedBy = %s, approvalDate = NOW()
                WHERE attendanceId = %s
                """,
                (entry_dt, self.user_id, attendance_id)
            )
        else:
            self.db.execute(
                """
                INSERT INTO attendance
                (memberId, workDate, checkIn, status, approvalStatus, approvedBy, approvalDate)
                VALUES (%s, %s, %s, 'present', 'approved', %s, NOW())
                """,
                (member_id, today_str, entry_dt, self.user_id)
            )

        NiceMessageBox.success(self, "ثبت ورود", f"ورود برای {row.get('name') or ''} در ساعت {entry_dt.strftime('%H:%M')} ثبت شد.")
        self.refresh_employees_attendance()
        signals.data_changed.emit("attendance")

    def owner_register_exit(self, row):
        member_id = row.get("memberId")
        attendance_id = row.get("attendanceId")
        if not member_id or not attendance_id:
            return

        if self.date_filter.date() != QDate.currentDate():
            NiceMessageBox.error(self, "خطا", "فقط برای امروز می‌توانید خروج ثبت کنید.")
            return

        today = QDate.currentDate()
        now = datetime.now()
        exit_dt = datetime(
            today.year(), today.month(), today.day(),
            now.hour, now.minute, now.second
        )

        ci = row.get("checkIn")
        worked_minutes = 0
        if isinstance(ci, datetime):
            delta = exit_dt - ci
            worked_minutes = max(0, int(delta.total_seconds() // 60))

        self.db.execute(
            """
            UPDATE attendance
            SET checkOut = %s, workedMinutes = %s,
                approvalStatus = 'approved', approvedBy = %s, approvalDate = NOW()
            WHERE attendanceId = %s
            """,
            (exit_dt, worked_minutes, self.user_id, attendance_id)
        )

        h, m = worked_minutes // 60, worked_minutes % 60
        NiceMessageBox.success(self, "ثبت خروج", f"خروج برای {row.get('name') or ''} در ساعت {exit_dt.strftime('%H:%M')} ثبت شد ({h} ساعت و {m} دقیقه کار).")
        self.refresh_employees_attendance()
        signals.data_changed.emit("attendance")

    def save_attendance_row(self, row):
        attendance_id = row.get("attendanceId")
        approval = row.get("approvalStatus")

        if not attendance_id:
            NiceMessageBox.error(self, tr("error"), tr("no_record"))
            return

        if approval == "approved":
            NiceMessageBox.info(self, tr("already_approved"),
                                tr("already_approved_msg", name=row.get('name', '')))
            return

        result = self.db.execute(
            """
            UPDATE attendance
            SET approvalStatus = 'approved', approvedBy = %s, approvalDate = NOW()
            WHERE attendanceId = %s
            """,
            (self.user_id, attendance_id)
        )

        if result is None:
            NiceMessageBox.error(self, tr("error"), tr("approve_failed"))
            return

        NiceMessageBox.success(self, tr("attendance_saved"),
                               tr("attendance_saved_msg", name=row.get('name', '')))
        self.refresh_employees_attendance()
        signals.data_changed.emit("attendance")

    def approve_attendance(self, row):
        attendance_id = row.get("attendanceId")
        if not attendance_id:
            return

        result = self.db.execute(
            """
            UPDATE attendance
            SET approvalStatus = 'approved', approvedBy = %s, approvalDate = NOW()
            WHERE attendanceId = %s
            """,
            (self.user_id, attendance_id)
        )

        if result is None:
            NiceMessageBox.error(self, tr("error"), tr("approve_failed"))
            return

        self.refresh_employees_attendance()
        signals.data_changed.emit("attendance")
        NiceMessageBox.success(self, tr("approved_msg"),
                               tr("already_approved_msg", name=row.get('name', '')))

    def reject_attendance(self, row):
        attendance_id = row.get("attendanceId")
        if not attendance_id:
            return

        result = self.db.execute(
            """
            UPDATE attendance
            SET approvalStatus = 'rejected', approvedBy = %s, approvalDate = NOW()
            WHERE attendanceId = %s
            """,
            (self.user_id, attendance_id)
        )

        if result is None:
            NiceMessageBox.error(self, tr("error"), tr("reject_failed"))
            return

        self.refresh_employees_attendance()
        signals.data_changed.emit("attendance")

        NiceMessageBox.warning(self, tr("rejected_msg"), tr("rejected_msg"))

    # =====================================================
    # EDIT DIALOG (RESIZABLE)
    # =====================================================

    def open_edit_dialog(self, row):
        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("edit_attendance"))
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        # ═══ قابل تغییر اندازه + باریک ═══
        dialog.setMinimumSize(420, 460)
        dialog.resize(480, 620)

        # ═══ لایه اصلی ═══
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ═══ اسکرول گرد ═══
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QScrollArea::viewport { background: transparent; }")
        vbar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(vbar)

        # ═══ محتوا ═══
        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_main']};")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(12)

        name = row.get("name") or "—"
        title = QLabel(f"{tr('edit_attendance')} — {name}")
        title.setStyleSheet(f"color: {c['text_main']}; font-size: 15px; font-weight: 700; background: transparent;")
        layout.addWidget(title)

        inp_style = f"""
            QTimeEdit, QLineEdit {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
                padding: 0 16px;
                color: {c['text_main']};
                font-size: 13px;
                min-height: 44px;
            }}
            QTimeEdit:focus, QLineEdit:focus {{
                background: {c['bg_card']};
                border: 2px solid {c['accent']};
            }}
            QTimeEdit::up-button, QTimeEdit::down-button {{
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }}
        """

        in_label = QLabel(tr("check_in_time"))
        in_label.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        in_time = QTimeEdit()
        in_time.setDisplayFormat("HH:mm")
        in_time.setFixedHeight(44)
        in_time.setStyleSheet(inp_style)

        ci = row.get("checkIn")
        in_time.setTime(QTime(ci.hour, ci.minute) if isinstance(ci, datetime) else QTime.currentTime())

        layout.addWidget(in_label)
        layout.addWidget(in_time)

        out_label = QLabel(tr("check_out_time"))
        out_label.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        out_time = QTimeEdit()
        out_time.setDisplayFormat("HH:mm")
        out_time.setFixedHeight(44)
        out_time.setStyleSheet(inp_style)

        co = row.get("checkOut")
        out_time.setTime(QTime(co.hour, co.minute) if isinstance(co, datetime) else QTime(17, 0))

        layout.addWidget(out_label)
        layout.addWidget(out_time)

        ot_lbl = QLabel("اضافه کاری (ساعت:دقیقه)")
        ot_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(ot_lbl)

        ot_time = QTimeEdit()
        ot_time.setDisplayFormat("HH:mm")
        ot_time.setFixedHeight(44)
        ot_time.setStyleSheet(inp_style)

        current_ot = int(row.get("overtimeMinutes") or 0)
        ot_h = current_ot // 60
        ot_m = current_ot % 60
        ot_time.setTime(QTime(ot_h if ot_h < 24 else 23, ot_m, 0))

        layout.addWidget(ot_time)

        desc_label = QLabel(tr("description_optional"))
        desc_label.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        desc_input = QLineEdit()
        desc_input.setFixedHeight(44)
        desc_input.setText(row.get("description") or "")
        desc_input.setStyleSheet(inp_style)

        layout.addWidget(desc_label)
        layout.addWidget(desc_input)

        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        # ═══ دکمه‌های ثابت پایین ═══
        bottom = QFrame()
        bottom.setAttribute(Qt.WA_StyledBackground, True)
        bottom.setStyleSheet(f"background-color: {c['bg_card']}; border-top: 1px solid {c['border']};")
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(28, 14, 28, 14)
        bottom_layout.setSpacing(10)

        cancel_btn = QPushButton(tr("cancel"))
        cancel_btn.setFixedHeight(46)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_input']};
                color: {c['text_dim']};
                border: 1px solid {c['border']};
                border-radius: 23px;
                padding: 0 26px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
        """)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = QPushButton(tr("save"))
        save_btn.setFixedHeight(46)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 23px;
                padding: 0 30px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {c['accent_hover']}; }}
        """)

        def on_save():
            attendance_id = row.get("attendanceId")
            selected_date = self.date_filter.date()
            selected_date_str = selected_date.toString("yyyy-MM-dd")

            new_in = in_time.time()
            new_out = out_time.time()

            in_dt = datetime(selected_date.year(), selected_date.month(), selected_date.day(),
                             new_in.hour(), new_in.minute())
            out_dt = datetime(selected_date.year(), selected_date.month(), selected_date.day(),
                              new_out.hour(), new_out.minute())

            delta = out_dt - in_dt
            worked = max(0, int(delta.total_seconds() // 60))

            ot_val = ot_time.time()
            total_ot = ot_val.hour() * 60 + ot_val.minute()

            if attendance_id:
                self.db.execute(
                    """
                    UPDATE attendance
                    SET checkIn = %s, checkOut = %s, workedMinutes = %s,
                        overtimeMinutes = %s, description = %s
                    WHERE attendanceId = %s
                    """,
                    (in_dt, out_dt, worked, total_ot,
                     desc_input.text().strip() or None, attendance_id)
                )
            else:
                self.db.execute(
                    """
                    INSERT INTO attendance
                    (memberId, workDate, checkIn, checkOut, workedMinutes,
                     overtimeMinutes, status, description, approvalStatus)
                    VALUES (%s, %s, %s, %s, %s, %s, 'present', %s, 'approved')
                    """,
                    (row["memberId"], selected_date_str, in_dt, out_dt, worked,
                     total_ot, desc_input.text().strip() or None)
                )

            dialog.accept()
            self.refresh_employees_attendance()
            NiceMessageBox.success(self, tr("saved"), tr("saved_changes"))

        save_btn.clicked.connect(on_save)

        bottom_layout.addStretch()
        bottom_layout.addWidget(cancel_btn)
        bottom_layout.addWidget(save_btn)

        main_layout.addWidget(bottom)

        dialog.setStyleSheet(f"QDialog {{ background-color: {c['bg_main']}; font-family: 'Vazirmatn'; }}")
        dialog.exec()