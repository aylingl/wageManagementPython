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
        self.setStyleSheet("QScrollBar {background: transparent;border: none;margin: 0px;}")

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
        painter.drawRoundedRect(int(track_x), int(track_top), track_width, int(track_height), track_width/2, track_width/2)

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
        painter.drawRoundedRect(int(handle_x), int(handle_y), handle_width, int(handle_height), handle_width/2, handle_width/2)

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
        self._popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
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
            QListWidget {{ background: transparent; border: none; outline: none; padding: 6px; color: {c['text_main']}; font-family: "Vazirmatn"; font-size: 13px; }}
            QListWidget::item {{ background: transparent; color: {c['text_main']}; border-radius: 10px; padding: 10px 16px; margin: 2px 4px; min-height: 20px; }}
            QListWidget::item:hover {{ background-color: {c['bg_hover']}; color: {c['accent']}; }}
            QListWidget::item:selected {{ background-color: {c['accent']}; color: white; }}
            QScrollBar:vertical {{ width: 8px; background: transparent; border: none; margin: 6px 2px; }}
            QScrollBar::handle:vertical {{ background: {c['accent']}; border-radius: 4px; min-height: 24px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
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
    days = 355666 + (365*gy) + ((gy2+3)//4) - ((gy2+99)//100) + ((gy2+399)//400) + gd + g_d_m[gm-1]
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
    days = -355668 + (365*jy) + ((jy//33)*8) + (((jy%33)+3)//4) + jd + ((jm-1)*31 if jm<7 else ((jm-7)*30)+186)
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
    is_leap = (gy%4==0 and gy%100!=0) or (gy%400==0)
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

MONTH_NAMES = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]

WEEKDAY_SHORT = ["ش", "ی", "د", "س", "چ", "پ", "ج"]

def jalali_string(qdate):
    jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
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

        c = theme_manager.colors()

        if kind == "success":
            icon_char, color, bg = "✓", "#16A34A", "#DCFCE7"
        elif kind == "error":
            icon_char, color, bg = "✕", "#D93025", "#FEE2E2"
        elif kind == "warning":
            icon_char, color, bg = "!", "#F59E0B", "#FEF3C7"
        else:
            icon_char, color, bg = "i", "#1961C7", "#DBEAFE"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(f"background-color: {c['bg_card']};border-radius: 22px;border: 1px solid {c['border']};")
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)

        icon_label = QLabel(icon_char)
        icon_label.setFixedSize(56, 56)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"background-color: {bg};color: {color};border-radius: 28px;font-size: 26px;font-weight: 700;")

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()
        layout.addLayout(icon_row)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {c['text_main']};font-size: 16px;font-weight: 700;background: transparent;border: none;")
        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"color: {c['text_dim']};font-size: 12px;background: transparent;border: none;")
        layout.addWidget(text_label)
        layout.addStretch()

        btn = QPushButton(tr("ok"))
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(120)
        btn.setStyleSheet(f"background-color: {color};color: white;border: none;border-radius: 12px;font-size: 12px;font-weight: 600;padding: 0px 24px;")
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
        self.setFixedSize(300, 360)

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
            QLabel#calMonthLabel {{color: {c['text_main']};font-size: 13px;font-weight: 700;background: transparent;}}
            QPushButton#calNavBtn {{background-color: {c['accent_light']};color: {c['accent']};border: 1px solid {c['border_hover']};border-radius: 10px;font-size: 16px;font-weight: 700;padding: 0px;}}
            QPushButton#calNavBtn:hover {{background-color: {c['bg_hover']};}}
            QLabel#calWeekday {{color: {c['text_dim']};font-size: 10px;font-weight: 700;background: transparent;}}
            QPushButton#calDayBtn {{background-color: transparent;color: {c['text_main']};border: none;border-radius: 8px;font-size: 11px;font-weight: 600;min-height: 28px;}}
            QPushButton#calDayBtn:hover {{background-color: {c['bg_hover']};color: {c['accent']};}}
            QPushButton#calDayBtn[today="true"] {{border: 2px solid {c['accent']};color: {c['accent']};}}
            QPushButton#calDayBtn[selected="true"] {{background-color: {c['accent']};color: white;border: none;}}
        """)

    def refresh_grid(self):
        while self.days_layout.count():
            item = self.days_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.month_label.setText(f"{MONTH_NAMES[self.view_month - 1]} {self.view_year}")

        if self.view_month <= 6:
            days_in_month = 31
        elif self.view_month <= 11:
            days_in_month = 30
        elif is_jalali_leap(self.view_year):
            days_in_month = 30
        else:
            days_in_month = 29

        gy, gm, gd = jalali_to_gregorian(self.view_year, self.view_month, 1)
        first_qdate = QDate(gy, gm, gd)
        persian_weekday = (first_qdate.dayOfWeek() + 1) % 7

        today_qdate = QDate.currentDate()
        tjy, tjm, tjd = gregorian_to_jalali(today_qdate.year(), today_qdate.month(), today_qdate.day())

        row = 0
        col = persian_weekday

        for day in range(1, days_in_month + 1):
            btn = QPushButton(str(day))
            btn.setObjectName("calDayBtn")
            btn.setCursor(Qt.PointingHandCursor)

            is_today = (self.view_year == tjy and self.view_month == tjm and day == tjd)
            is_selected = (self.view_year == self.selected_jy and self.view_month == self.selected_jm and day == self.selected_jd)

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

    def __init__(self, parent=None, initial_qdate=None):
        super().__init__(parent)

        self._qdate = initial_qdate or QDate.currentDate()

        self.setObjectName("persianDateFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(46)
        self.setMinimumWidth(200)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 14, 0)
        layout.setSpacing(8)

        self.icon_label = QLabel("📅")
        self.icon_label.setObjectName("dateIconLabel")
        self.icon_label.setFixedSize(32, 32)
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
# PERSIAN MONTH POPUP
# =========================================================

class PersianMonthPopup(QWidget):

    monthSelected = Signal(int, int)

    def __init__(self, parent=None, current_year=None, current_month=None):
        super().__init__(parent)

        today = QDate.currentDate()
        jy, jm, jd = gregorian_to_jalali(today.year(), today.month(), today.day())
        if current_year is None:
            current_year = jy
        if current_month is None:
            current_month = jm

        self.view_year = current_year
        self.selected_year = current_year
        self.selected_month = current_month

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
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
        c = theme_manager.colors()
        r = self._radius
        m = self._margin
        rect = self.rect().adjusted(m, m, -m, -m)

        for i in range(6, 0, -1):
            shadow_color = QColor(0, 0, 0, 4 + (6 - i) * 2)
            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)
            painter.drawRoundedRect(rect.adjusted(-i, -i+2, i, i+2), r+i, r+i)

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
        layout.setContentsMargins(self._margin+14, self._margin+14, self._margin+14, self._margin+14)
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
            col = idx % 3
            btn = QPushButton(month_name)
            btn.setObjectName("monthBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(50)

            if idx + 1 == self.selected_month and self.view_year == self.selected_year:
                btn.setProperty("selected", "true")
            else:
                btn.setProperty("selected", "false")

            btn.clicked.connect(lambda checked=False, m=idx+1: self.pick_month(m))
            grid.addWidget(btn, r, col)

        layout.addLayout(grid, 1)

        self.setStyleSheet(f"""
            QLabel#calMonthLabel {{color: {c['text_main']};font-size: 14px;font-weight: 700;background: transparent;}}
            QPushButton#calNavBtn {{background-color: {c['accent_light']};color: {c['accent']};border: 1px solid {c['border_hover']};border-radius: 10px;font-size: 16px;font-weight: 700;padding: 0px;}}
            QPushButton#calNavBtn:hover {{background-color: {c['bg_hover']};}}
            QPushButton#monthBtn {{background-color: {c['bg_input']};color: {c['text_main']};border: 1px solid {c['border']};border-radius: 12px;font-size: 12px;font-weight: 600;}}
            QPushButton#monthBtn:hover {{background-color: {c['bg_hover']};color: {c['accent']};border: 1px solid {c['border_hover']};}}
            QPushButton#monthBtn[selected="true"] {{background-color: {c['accent']};color: white;border: 1px solid {c['accent']};}}
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
        self.monthSelected.emit(self.selected_year, self.selected_month)
        self.close()

# =========================================================
# PERSIAN MONTH BUTTON
# =========================================================

class PersianMonthButton(QFrame):

    monthChanged = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        today = QDate.currentDate()
        jy, jm, jd = gregorian_to_jalali(today.year(), today.month(), today.day())
        self.year = jy
        self.month = jm

        self.setObjectName("persianDateFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)
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
        self.month_btn.setText(f"{MONTH_NAMES[self.month - 1]} {self.year}")

    def _open_popup(self):
        self._popup = PersianMonthPopup(self, self.year, self.month)
        self._popup.monthSelected.connect(self._on_month_selected)
        global_pos = self.mapToGlobal(QPoint(0, self.height() + 4))
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
        self.my_name = "—"

        today = QDate.currentDate()
        jy, jm, jd = gregorian_to_jalali(today.year(), today.month(), today.day())
        self.selected_year = jy
        self.selected_month = jm

        # فیلترهای روزانه هر تب
        self.selected_day_qdate = None       # salaries
        self.bonus_filter_date = None         # bonuses
        self.deduction_filter_date = None     # deductions
        self.history_filter_date = None       # history

        self.setWindowTitle(tr("finance_title"))
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

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("finance_title"))
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
        try:
            current = self.stack.currentIndex()
            self.switch_tab(current)
        except Exception as e:
            print("FINANCE REFRESH ERROR:", e)

    def load_user_data(self):
        try:
            user = self.db.fetch_one(
                "SELECT userId, name FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if not user:
                return

            self.user_id = user["userId"]
            self.my_name = user.get("name") or "—"

            rows = self.db.fetch_all(
                """
                SELECT c.complexId, c.name, cm.memberId, cm.role
                FROM complexes c
                INNER JOIN complex_members cm ON cm.complexId = c.complexId
                WHERE cm.userId = %s AND cm.isActive = '1' AND c.isActive = '1'
                ORDER BY c.complexId ASC
                """,
                (self.user_id,)
            )
            self.complexes = rows or []

            if self.complexes:
                chosen = None
                if self.preselect_complex_id:
                    for cc in self.complexes:
                        if cc["complexId"] == self.preselect_complex_id:
                            chosen = cc
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

    # =====================================================
    # UI
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

        title = QLabel(tr("finance_title"))
        title.setObjectName("finTitle")

        subtitle = QLabel(tr("finance_subtitle"))
        subtitle.setObjectName("finSubtitle")

        title_text_layout.addWidget(title)
        title_text_layout.addWidget(subtitle)

        back_button = QPushButton("›")
        back_button.setObjectName("finBackBtn")
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
            self.complex_combo.setObjectName("finComplexCombo")
            self.complex_combo.setFixedHeight(42)
            self.complex_combo.setMinimumWidth(200)
            self.complex_combo.setAttribute(Qt.WA_StyledBackground, True)
            self.complex_combo.setCursor(Qt.PointingHandCursor)
            for cc in self.complexes:
                self.complex_combo.addItem(cc["name"], cc["complexId"])
            for i, cc in enumerate(self.complexes):
                if cc["complexId"] == self.complex_id:
                    self.complex_combo.setCurrentIndex(i)
                    break
            self.complex_combo.currentIndexChanged.connect(self.on_complex_changed)
            header.addWidget(self.complex_combo)

        main_layout.addLayout(header)

        self.is_owner = self.role in ("owner", "both")

        self.tab_btns = []

        if self.is_owner:
            tabs = QHBoxLayout()
            tabs.setSpacing(6)

            tab_keys = [
                ("tab_summary", "summary"),
                ("tab_salaries", "salaries"),
                ("tab_bonuses", "bonuses"),
                ("tab_deductions", "deductions"),
                ("tab_history", "history"),
            ]

            for i, (key, name) in enumerate(tab_keys):
                btn = QPushButton(tr(key))
                btn.setObjectName("tabButton")
                btn.setFixedHeight(40)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setAttribute(Qt.WA_StyledBackground, True)
                btn.clicked.connect(lambda checked=False, idx=i: self.switch_tab(idx))
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

        self.apply_stylesheet()

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""
            QWidget#financeWindow {{
                background-color: {c['bg_main']};
                font-family: "Vazirmatn";
                color: {c['text_main']};
            }}
            QWidget#financeWindow QLabel {{ background: transparent; }}

            QLabel#finTitle {{ font-size: 21px; font-weight: 700; color: {c['text_main']}; background: transparent; }}
            QLabel#finSubtitle {{ font-size: 10px; color: {c['text_dim']}; background: transparent; }}

            QPushButton#finBackBtn {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 21px;
                color: {c['accent']};
                font-size: 22px;
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton#finBackBtn:hover {{ background-color: {c['bg_hover']}; border-color: {c['border_hover']}; }}

            QComboBox#finComplexCombo {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 21px;
                padding: 0 18px;
                color: {c['text_main']};
                font-size: 12px;
                font-weight: 600;
            }}
            QComboBox#finComplexCombo:hover {{
                border-color: {c['accent']};
                background-color: {c['bg_hover']};
            }}
            QComboBox#finComplexCombo::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border: none;
                background: transparent;
            }}
            QComboBox#finComplexCombo::down-arrow {{
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
                padding: 0 22px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#tabButton:hover {{ background-color: {c['bg_hover']}; }}
            QPushButton#tabButton[selected="true"] {{
                background-color: {c['accent']};
                color: white;
                border: 1px solid {c['accent']};
            }}

            QFrame#box {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 28px;
            }}
            QFrame#boxSub {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 22px;
            }}
            QFrame#boxSub:hover {{
                border-color: {c['border_hover']};
                background-color: {c['bg_hover']};
            }}
            QFrame#contentBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 28px;
            }}

            QLabel#sectionTitle {{
                color: {c['text_main']};
                font-size: 14px;
                font-weight: 700;
                background: transparent;
            }}
            QLabel#statTitle {{ color: {c['text_dim']}; font-size: 11px; font-weight: 600; background: transparent; min-height: 18px; }}
            QLabel#statValue {{ color: {c['accent']}; font-size: 18px; font-weight: 800; background: transparent; }}
            QLabel#statValueGreen {{ color: {c['success']}; font-size: 18px; font-weight: 800; background: transparent; }}
            QLabel#statValueRed {{ color: {c['danger']}; font-size: 18px; font-weight: 800; background: transparent; }}

            QFrame#statBox {{ background-color: {c['bg_input']}; border: 1px solid {c['border']}; border-radius: 20px; }}
            QFrame#statBoxGreen {{ background-color: {c['success_bg']}; border: 1px solid {c['border']}; border-radius: 20px; }}
            QFrame#statBoxRed {{ background-color: {c['danger_bg']}; border: 1px solid {c['border']}; border-radius: 20px; }}

            QLabel#empName {{
                color: {c['text_main']};
                font-size: 14px;
                font-weight: 700;
                background: transparent;
                padding: 4px 0px;
                min-height: 22px;
            }}
            QLabel#empInfo {{
                color: {c['text_dim']};
                font-size: 10px;
                background: transparent;
                padding: 2px 0px;
                min-height: 16px;
            }}
            QLabel#moneyLabel {{
                color: {c['text_dim']};
                font-size: 11px;
                font-weight: 600;
                background: transparent;
                min-height: 18px;
            }}
            QLabel#moneyValue {{
                color: {c['text_main']};
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                min-height: 18px;
            }}
            QLabel#moneyValueGreen {{
                color: {c['success']};
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                min-height: 18px;
            }}
            QLabel#moneyValueRed {{
                color: {c['danger']};
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                min-height: 18px;
            }}
            QLabel#moneyValueBlue {{
                color: {c['accent']};
                font-size: 14px;
                font-weight: 800;
                background: transparent;
                min-height: 22px;
            }}

            QLabel#badgePending {{ color: {c['warning']}; background-color: {c['warning_bg']}; border: none; border-radius: 12px; padding: 4px 12px; font-size: 10px; font-weight: 700; }}
            QLabel#badgePaid {{ color: {c['success']}; background-color: {c['success_bg']}; border: none; border-radius: 12px; padding: 4px 12px; font-size: 10px; font-weight: 700; }}
            QLabel#badgeDraft {{ color: {c['text_dim']}; background-color: {c['bg_input']}; border: none; border-radius: 12px; padding: 4px 12px; font-size: 10px; font-weight: 700; }}

            QPushButton#payBtn {{
                background-color: {c['success_bg']};
                color: {c['success']};
                border: 1px solid {c['success']};
                border-radius: 14px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 700;
                min-height: 30px;
                max-height: 30px;
            }}
            QPushButton#payBtn:hover {{ background-color: {c['bg_hover']}; }}

            QPushButton#detailBtn {{
                background-color: {c['accent_light']};
                color: {c['accent']};
                border: 1px solid {c['accent']};
                border-radius: 14px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 700;
                min-height: 30px;
                max-height: 30px;
            }}
            QPushButton#detailBtn:hover {{ background-color: {c['bg_hover']}; }}

            QPushButton#primaryBtn {{ background-color: {c['accent']}; color: white; border: none; border-radius: 22px; padding: 8px 24px; font-size: 12px; font-weight: 700; min-height: 44px; }}
            QPushButton#primaryBtn:hover {{ background-color: {c['accent_hover']}; }}

            QPushButton#calcSalariesBtn {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 20px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 700;
                min-height: 38px;
                max-height: 38px;
            }}
            QPushButton#calcSalariesBtn:hover {{ background-color: {c['accent_hover']}; }}

            QPushButton#secondaryBtn {{ background-color: {c['accent_light']}; color: {c['accent']}; border: 1px solid {c['border_hover']}; border-radius: 22px; padding: 8px 24px; font-size: 12px; font-weight: 700; min-height: 44px; }}
            QPushButton#secondaryBtn:hover {{ background-color: {c['bg_hover']}; }}

            QPushButton#iconResetBtn {{
                background-color: {c['bg_input']};
                color: {c['text_dim']};
                border: 1px solid {c['border']};
                border-radius: 17px;
                font-size: 13px;
                font-weight: 700;
                padding: 0px;
            }}
            QPushButton#iconResetBtn:hover {{
                background-color: {c['bg_hover']};
                color: {c['accent']};
                border: 1px solid {c['border_hover']};
            }}

            QLabel#dateIconLabel {{ background-color: {c['accent_light']}; border: none; border-radius: 10px; font-size: 16px; font-weight: 700; }}
            QFrame#persianDateFrame {{ background-color: {c['bg_input']}; border: 1px solid {c['border']}; border-radius: 22px; }}
            QFrame#persianDateFrame:hover {{ background-color: {c['bg_card']}; border: 1px solid {c['border_hover']}; }}
            QPushButton#persianDateButton {{ background-color: transparent; border: none; padding: 0 4px; color: {c['text_main']}; font-size: 12px; font-weight: 700; text-align: center; }}
            QPushButton#persianDateButton:hover {{ color: {c['accent']}; }}

            QFrame#emptyCard {{ background-color: {c['bg_card']}; border: 1px dashed {c['border']}; border-radius: 22px; }}
            QLabel#emptyText {{ color: {c['text_dim']}; font-size: 12px; background: transparent; }}

            QScrollArea#financeScroll {{ background: transparent; border: none; border-radius: 28px; }}
            QScrollArea#financeScroll > QWidget {{ background: transparent; border-radius: 28px; }}
            QScrollArea#financeScroll > QWidget > QWidget {{ background: transparent; border-radius: 28px; }}
            QScrollArea#financeScroll::viewport {{ background: transparent; border: none; border-radius: 28px; }}

            QLineEdit#formInput {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 14px;
                padding: 0 16px;
                color: {c['text_main']};
                font-size: 13px;
                min-height: 42px;
            }}
            QLineEdit#formInput:focus {{ background: {c['bg_card']}; border: 2px solid {c['accent']}; }}
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

    # =====================================================
    # TAB BUILDERS
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

        month_lbl = QLabel(tr("month_label"))
        month_lbl.setStyleSheet(f"color: {theme_manager.colors()['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        self.dashboard_date_btn = PersianDateButton()
        self.dashboard_date_btn.dateChanged.connect(self.on_dashboard_day_changed)

        mb_layout.addWidget(month_lbl)
        mb_layout.addWidget(self.dashboard_date_btn)
        mb_layout.addStretch()

        layout.addWidget(month_box)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        self.dash_total_box = self.create_stat_box(tr("total_salary_month"), "0", "statBox")
        self.dash_paid_box = self.create_stat_box(tr("paid_amount"), "0", "statBoxGreen")
        self.dash_remain_box = self.create_stat_box(tr("remain_amount"), "0", "statBoxRed")
        self.dash_emp_box = self.create_stat_box(tr("employees_count"), "0", "statBox")

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

    def on_dashboard_day_changed(self, qdate):
        jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
        self.selected_year = jy
        self.selected_month = jm
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

        month_lbl = QLabel(tr("month_label"))
        month_lbl.setStyleSheet(f"color: {theme_manager.colors()['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        self.salary_date_btn = PersianDateButton()
        self.salary_date_btn.setMinimumWidth(230)
        self.salary_date_btn.dateChanged.connect(self.on_salary_day_changed)

        calc_btn = QPushButton(tr("calculate_salaries"))
        calc_btn.setObjectName("calcSalariesBtn")
        calc_btn.setCursor(Qt.PointingHandCursor)
        calc_btn.clicked.connect(self.calculate_all_salaries)

        top_layout.addWidget(month_lbl)
        top_layout.addWidget(self.salary_date_btn)
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

    def on_salary_day_changed(self, qdate):
        jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
        self.selected_year = jy
        self.selected_month = jm
        self.selected_day_qdate = qdate
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
        top_layout.setSpacing(8)

        title = QLabel(tr("tab_bonuses"))
        title.setObjectName("sectionTitle")

        self.bonus_date_btn = PersianDateButton()
        self.bonus_date_btn.dateChanged.connect(self.on_bonus_day_changed)

        self.bonus_reset_btn = QPushButton("✕")
        self.bonus_reset_btn.setObjectName("iconResetBtn")
        self.bonus_reset_btn.setFixedSize(34, 34)
        self.bonus_reset_btn.setCursor(Qt.PointingHandCursor)
        self.bonus_reset_btn.clicked.connect(self.reset_bonus_filter)

        add_btn = QPushButton(tr("add_bonus"))
        add_btn.setObjectName("primaryBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_bonus_dialog)

        top_layout.addWidget(title)
        top_layout.addSpacing(8)
        top_layout.addWidget(self.bonus_date_btn)
        top_layout.addWidget(self.bonus_reset_btn)
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

    def on_bonus_day_changed(self, qdate):
        self.bonus_filter_date = qdate
        self.refresh_bonuses()

    def reset_bonus_filter(self):
        self.bonus_filter_date = None
        self.refresh_bonuses()

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
        top_layout.setSpacing(8)

        title = QLabel(tr("tab_deductions"))
        title.setObjectName("sectionTitle")

        self.deduction_date_btn = PersianDateButton()
        self.deduction_date_btn.dateChanged.connect(self.on_deduction_day_changed)

        self.deduction_reset_btn = QPushButton("✕")
        self.deduction_reset_btn.setObjectName("iconResetBtn")
        self.deduction_reset_btn.setFixedSize(34, 34)
        self.deduction_reset_btn.setCursor(Qt.PointingHandCursor)
        self.deduction_reset_btn.clicked.connect(self.reset_deduction_filter)

        add_btn = QPushButton(tr("add_deduction"))
        add_btn.setObjectName("primaryBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_deduction_dialog)

        top_layout.addWidget(title)
        top_layout.addSpacing(8)
        top_layout.addWidget(self.deduction_date_btn)
        top_layout.addWidget(self.deduction_reset_btn)
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

    def on_deduction_day_changed(self, qdate):
        self.deduction_filter_date = qdate
        self.refresh_deductions()

    def reset_deduction_filter(self):
        self.deduction_filter_date = None
        self.refresh_deductions()

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
        top_layout.setSpacing(8)

        title = QLabel(tr("payment_history"))
        title.setObjectName("sectionTitle")

        self.history_date_btn = PersianDateButton()
        self.history_date_btn.dateChanged.connect(self.on_history_day_changed)

        self.history_reset_btn = QPushButton("✕")
        self.history_reset_btn.setObjectName("iconResetBtn")
        self.history_reset_btn.setFixedSize(34, 34)
        self.history_reset_btn.setCursor(Qt.PointingHandCursor)
        self.history_reset_btn.clicked.connect(self.reset_history_filter)

        top_layout.addWidget(title)
        top_layout.addSpacing(8)
        top_layout.addWidget(self.history_date_btn)
        top_layout.addWidget(self.history_reset_btn)
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

    def on_history_day_changed(self, qdate):
        self.history_filter_date = qdate
        self.refresh_history()

    def reset_history_filter(self):
        self.history_filter_date = None
        self.refresh_history()

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

        month_lbl = QLabel(tr("month_label"))
        month_lbl.setStyleSheet(f"color: {theme_manager.colors()['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        self.emp_date_btn = PersianDateButton()
        self.emp_date_btn.dateChanged.connect(self.on_emp_day_changed)

        top_layout.addWidget(month_lbl)
        top_layout.addWidget(self.emp_date_btn)
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

    def on_emp_day_changed(self, qdate):
        jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
        self.selected_year = jy
        self.selected_month = jm
        self.refresh_employee_history()

    # =====================================================
    # REFRESH: DASHBOARD
    # =====================================================

    def refresh_dashboard(self):
        if not self.is_owner or not self.complex_id:
            return

        year = self.selected_year
        month = self.selected_month

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

        total_row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(s.finalAmount), 0) AS total
            FROM salaries s
            INNER JOIN complex_members cm ON cm.memberId = s.memberId
            WHERE cm.complexId = %s
              AND s.salaryYear = %s
              AND s.salaryMonth = %s
            """,
            (self.complex_id, year, month)
        )
        total = float(total_row["total"] or 0) if total_row else 0

        paid_row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(p.amount), 0) AS paid
            FROM payments p
            INNER JOIN complex_members cm ON cm.memberId = p.memberId
            WHERE cm.complexId = %s
              AND p.paymentType = 'salary'
              AND DATE(p.paymentDate) BETWEEN %s AND %s
            """,
            (self.complex_id, first_day, last_day)
        )
        paid = float(paid_row["paid"] or 0) if paid_row else 0

        remain = max(0, total - paid)

        emp_result = self.db.fetch_one(
            """
            SELECT COUNT(*) AS cnt FROM complex_members
            WHERE complexId = %s AND role IN ('employee', 'both') AND isActive = '1'
            """,
            (self.complex_id,)
        )
        emp_count = emp_result["cnt"] if emp_result else 0

        self.dash_total_box.findChild(QLabel, "statValue").setText(format_money(total))
        self.dash_paid_box.findChild(QLabel, "statValueGreen").setText(format_money(paid))
        self.dash_remain_box.findChild(QLabel, "statValueRed").setText(format_money(remain))
        self.dash_emp_box.findChild(QLabel, "statValue").setText(str(emp_count))

    # =====================================================
    # REFRESH: SALARIES
    # =====================================================

    def refresh_salaries(self):
        if not self.is_owner or not self.complex_id:
            return

        if getattr(self, 'selected_day_qdate', None) is not None:
            self._refresh_salaries_for_day(self.selected_day_qdate)
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
            SELECT cm.memberId, u.name, u.phoneNumber, ep.jobTitle,
                   ep.salaryType, ep.baseSalary, ep.workDays, ep.workHours,
                   ep.employmentType, ep.allowOvertime,
                   s.salaryId, s.baseSalary AS calcBase, s.overtimeAmount,
                   s.bonusAmount, s.deductionAmount, s.loanAmount,
                   s.finalAmount, s.status, s.paidDate
            FROM complex_members cm
            INNER JOIN users u ON u.userId = cm.userId
            LEFT JOIN employee_profiles ep ON ep.memberId = cm.memberId
            LEFT JOIN salaries s ON s.memberId = cm.memberId
                AND s.salaryYear = %s AND s.salaryMonth = %s
            WHERE cm.complexId = %s AND cm.role IN ('employee', 'both') AND cm.isActive = '1'
            ORDER BY u.name ASC
            """,
            (year, month, self.complex_id)
        )

        if not rows:
            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setAttribute(Qt.WA_StyledBackground, True)
            empty.setMinimumHeight(120)
            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)
            t = QLabel(tr("no_employees_group"))
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

    def _refresh_salaries_for_day(self, qdate):
        while self.salaries_layout.count():
            item = self.salaries_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        c = theme_manager.colors()
        jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
        day_py = qdate.toPython()

        header = QFrame()
        header.setObjectName("box")
        header.setAttribute(Qt.WA_StyledBackground, True)
        h_l = QHBoxLayout(header)
        h_l.setContentsMargins(20, 12, 20, 12)
        h_l.setSpacing(10)

        title = QLabel(f"{tr('payment_history')} — {jd} {MONTH_NAMES[jm - 1]} {jy}")
        title.setStyleSheet(f"color: {c['text_main']}; font-size: 14px; font-weight: 700; background: transparent;")
        h_l.addWidget(title)
        h_l.addStretch()

        reset_btn = QPushButton("↩ " + tr("month_label"))
        reset_btn.setObjectName("secondaryBtn")
        reset_btn.setFixedHeight(36)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self._reset_day_filter)
        h_l.addWidget(reset_btn)

        self.salaries_layout.addWidget(header)

        rows = self.db.fetch_all(
            """
            SELECT p.paymentId, p.amount, p.paymentType, p.paymentDate,
                   p.description, u.name
            FROM payments p
            INNER JOIN complex_members cm ON cm.memberId = p.memberId
            INNER JOIN users u ON u.userId = cm.userId
            WHERE cm.complexId = %s AND DATE(p.paymentDate) = %s
            ORDER BY p.paymentDate DESC, p.paymentId DESC
            """,
            (self.complex_id, day_py)
        )

        if not rows:
            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setAttribute(Qt.WA_StyledBackground, True)
            empty.setMinimumHeight(120)
            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)
            t = QLabel(tr("no_payment"))
            t.setObjectName("emptyText")
            t.setAlignment(Qt.AlignCenter)
            el.addWidget(t)
            self.salaries_layout.addWidget(empty)
            self.salaries_layout.addStretch()
            return

        for row in rows:
            card = self.create_history_card(row)
            self.salaries_layout.addWidget(card)

        self.salaries_layout.addStretch()

    def _reset_day_filter(self):
        self.selected_day_qdate = None
        today = QDate.currentDate()
        jy, jm, jd = gregorian_to_jalali(today.year(), today.month(), today.day())
        self.selected_year = jy
        self.selected_month = jm
        if hasattr(self, 'salary_date_btn'):
            self.salary_date_btn.setDate(today)
        self.refresh_salaries()

    def create_salary_card(self, row):
        card = QFrame()
        card.setObjectName("boxSub")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(220)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(24)

        # ═══════ ستون راست ═══════
        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.setContentsMargins(0, 0, 0, 0)

        name_label = QLabel(row.get("name") or "—")
        name_label.setObjectName("empName")
        name_label.setMinimumHeight(24)
        name_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        phone = row.get("phoneNumber") or "-"
        phone_label = QLabel(phone)
        phone_label.setObjectName("empInfo")
        phone_label.setMinimumHeight(18)
        phone_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        job = row.get("jobTitle") or tr("no_job")
        salary_type_map = {"monthly": tr("monthly"), "daily": tr("daily"), "hourly": tr("hourly")}
        st = salary_type_map.get(row.get("salaryType"), "-")
        employment_map = {"fullTime": tr("full_time"), "partTime": tr("part_time")}
        emp_type = employment_map.get(row.get("employmentType"), "-")

        job_label = QLabel(f"{job}   •   {st}   •   {emp_type}")
        job_label.setObjectName("empInfo")
        job_label.setMinimumHeight(18)
        job_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        right_col.addWidget(name_label)
        right_col.addWidget(phone_label)
        right_col.addWidget(job_label)

        div1 = QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet(f"background-color: {theme_manager.colors()['border']}; border: none;")
        right_col.addSpacing(2)
        right_col.addWidget(div1)
        right_col.addSpacing(2)

        base_salary = float(row.get("baseSalary") or 0)
        base_row = QLabel(f"{tr('base_salary_short')}:  {format_money(base_salary)} {tr('toman')}")
        base_row.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        base_row.setMinimumHeight(26)
        base_row.setStyleSheet(f"color: {theme_manager.colors()['text_main']}; font-size: 13px; font-weight: 700; background: transparent; padding: 3px 0px;")
        right_col.addWidget(base_row)

        summary_title = QLabel(tr("summary_month"))
        summary_title.setMinimumHeight(20)
        summary_title.setStyleSheet(f"color: {theme_manager.colors()['accent']}; font-size: 11px; font-weight: 700; background: transparent; padding: 2px 0px;")
        summary_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
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
            rl.setContentsMargins(14, 1, 0, 1)
            rl.setSpacing(6)

            lb = QLabel(label_text)
            lb.setObjectName("moneyLabel")
            lb.setMinimumHeight(18)

            vl = QLabel(value_text)
            if kind == "green":
                vl.setObjectName("moneyValueGreen")
            elif kind == "red":
                vl.setObjectName("moneyValueRed")
            else:
                vl.setObjectName("moneyValue")
            vl.setMinimumHeight(18)
            vl.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)

            rl.addWidget(lb)
            rl.addWidget(vl, 1)
            right_col.addWidget(rw)

        has_any = False
        if overtime > 0:
            add_mini_row(f"{tr('overtime')}:", f"+ {format_money(overtime)}", "green")
            has_any = True
        if bonus > 0:
            add_mini_row(f"{tr('tab_bonuses')}:", f"+ {format_money(bonus)}", "green")
            has_any = True
        if deduction > 0:
            add_mini_row(f"{tr('tab_deductions')}:", f"- {format_money(deduction)}", "red")
            has_any = True
        if loan > 0:
            add_mini_row(f"{tr('payment_advance')}:", f"- {format_money(loan)}", "red")
            has_any = True

        if not has_any:
            no_extra = QLabel(tr("no_extra"))
            no_extra.setObjectName("empInfo")
            no_extra.setContentsMargins(14, 0, 0, 0)
            no_extra.setMinimumHeight(18)
            right_col.addWidget(no_extra)

        right_col.addStretch()
        layout.addLayout(right_col, 3)

        # ═══════ ستون چپ ═══════
        left_col = QVBoxLayout()
        left_col.setSpacing(6)
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setAlignment(Qt.AlignTop)

        final = float(row.get("finalAmount") or 0)
        final_title = QLabel(tr("final_salary"))
        final_title.setObjectName("statTitle")
        final_title.setMinimumHeight(18)
        final_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        final_value = QLabel(format_money(final) + " " + tr("toman"))
        final_value.setObjectName("moneyValueBlue")
        final_value.setMinimumHeight(24)
        final_value.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        left_col.addWidget(final_title)
        left_col.addWidget(final_value)
        left_col.addSpacing(4)

        status = row.get("status") or "draft"
        salary_id_for_check = row.get("salaryId")

        total_paid = 0
        if salary_id_for_check:
            paid_row = self.db.fetch_one(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM payments
                WHERE salaryId = %s AND paymentType = 'salary'
                """,
                (salary_id_for_check,)
            )
            total_paid = float(paid_row["total"] or 0) if paid_row else 0

        EPS = 1

        if salary_id_for_check and final > 0:
            if total_paid >= (final - EPS):
                real_status = "paid"
            elif total_paid > 0:
                real_status = "partial"
            else:
                if status == "calculated":
                    real_status = "pending"
                else:
                    real_status = "draft"
        else:
            real_status = status

        if real_status == "paid":
            badge = QLabel(tr("paid_status"))
            badge.setObjectName("badgePaid")
        elif real_status == "partial":
            remain_amount = max(0, final - total_paid)
            badge = QLabel(f"{tr('partial_status')} — {tr('remain_to_pay')}: {format_money(remain_amount)}")
            badge.setObjectName("badgePending")
        elif real_status == "pending":
            badge = QLabel(tr("pending_status"))
            badge.setObjectName("badgePending")
        else:
            badge = QLabel(tr("draft_status"))
            badge.setObjectName("badgeDraft")

        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(30)
        left_col.addWidget(badge)

        if real_status in ("draft", "pending", "partial") and row.get("salaryId"):
            pay_btn = QPushButton(tr("pay"))
            pay_btn.setObjectName("payBtn")
            pay_btn.setCursor(Qt.PointingHandCursor)
            pay_btn.setAttribute(Qt.WA_StyledBackground, True)
            pay_btn.clicked.connect(lambda checked=False, r=row: self.pay_salary(r))
            left_col.addWidget(pay_btn)
            left_col.addSpacing(4)

        detail_btn = QPushButton(tr("details"))
        detail_btn.setObjectName("detailBtn")
        detail_btn.setCursor(Qt.PointingHandCursor)
        detail_btn.setAttribute(Qt.WA_StyledBackground, True)
        detail_btn.clicked.connect(lambda checked=False, r=row: self.open_details_dialog(r))
        left_col.addWidget(detail_btn)

        left_col.addStretch()
        layout.addLayout(left_col, 2)
        return card

    # =====================================================
    # PAY SALARY
    # =====================================================

    def pay_salary(self, row):
        salary_id = row.get("salaryId")
        member_id = row.get("memberId")
        if not salary_id:
            return

        final_amount = float(row.get("finalAmount") or 0)
        employee_name = row.get("name") or "—"

        paid_row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE salaryId = %s AND paymentType = 'salary'
            """,
            (salary_id,)
        )
        total_paid = float(paid_row["total"] or 0) if paid_row else 0
        remain = max(0, final_amount - total_paid)

        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("pay_salary_title"))
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(460)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(28, 26, 28, 24)
        d_layout.setSpacing(10)

        title = QLabel(f"{tr('pay_salary_title')} — {employee_name}")
        title.setStyleSheet(f"color: {c['text_main']}; font-size: 16px; font-weight: 700; background: transparent;")
        d_layout.addWidget(title)

        remain_lbl = QLabel(f"{tr('remain_to_pay')}:  {format_money(remain)} {tr('toman')}")
        remain_lbl.setStyleSheet(f"color: {c['warning']}; font-size: 12px; font-weight: 700; background: transparent;")
        d_layout.addWidget(remain_lbl)

        d_layout.addSpacing(6)

        amount_lbl = QLabel(tr("pay_amount_label"))
        amount_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")
        d_layout.addWidget(amount_lbl)

        amount_input = QLineEdit()
        amount_input.setText(str(int(remain)))
        amount_input.setLayoutDirection(Qt.LeftToRight)
        amount_input.setFixedHeight(46)
        amount_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 23px;
                padding: 0 18px;
                color: {c['text_main']};
                font-size: 14px;
                font-weight: 700;
            }}
            QLineEdit:focus {{
                background-color: {c['bg_card']};
                border: 2px solid {c['accent']};
            }}
        """)
        d_layout.addWidget(amount_input)

        d_layout.addSpacing(6)

        date_lbl = QLabel(tr("pay_date_label"))
        date_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")
        d_layout.addWidget(date_lbl)

        date_picker = PersianDateButton(initial_qdate=QDate.currentDate())
        d_layout.addWidget(date_picker)

        d_layout.addSpacing(10)

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

        pay_btn = QPushButton(tr("confirm_payment"))
        pay_btn.setFixedHeight(46)
        pay_btn.setCursor(Qt.PointingHandCursor)
        pay_btn.setStyleSheet(f"""
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

        def on_pay():
            amount_text = amount_input.text().strip()

            if not amount_text:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_amount_required"))
                return

            try:
                amount = float(amount_text.replace(",", "").replace("٬", ""))
            except ValueError:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_amount_invalid"))
                return

            if amount <= 0:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_amount_positive"))
                return

            selected_qdate = date_picker.date()
            now = datetime.now()
            pay_dt = datetime(
                selected_qdate.year(),
                selected_qdate.month(),
                selected_qdate.day(),
                now.hour,
                now.minute,
                now.second
            )

            self.db.execute(
                """
                INSERT INTO payments (memberId, complexId, salaryId, amount,
                    paymentType, paymentDate, paidBy, description)
                VALUES (%s, %s, %s, %s, 'salary', %s, %s, %s)
                """,
                (member_id, self.complex_id, salary_id, amount, pay_dt, self.user_id,
                 f"Salary {MONTH_NAMES[self.selected_month - 1]} {self.selected_year}")
            )

            total_paid_row = self.db.fetch_one(
                """
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM payments
                WHERE salaryId = %s AND paymentType = 'salary'
                """,
                (salary_id,)
            )
            new_total_paid = float(total_paid_row["total"] or 0) if total_paid_row else 0

            EPS = 1
            if new_total_paid >= (final_amount - EPS):
                self.db.execute(
                    "UPDATE salaries SET status = 'paid', paidDate = %s, paidBy = %s WHERE salaryId = %s",
                    (pay_dt, self.user_id, salary_id)
                )
            else:
                self.db.execute(
                    "UPDATE salaries SET status = 'calculated' WHERE salaryId = %s",
                    (salary_id,)
                )

            dialog.accept()

            NiceMessageBox.success(
                self,
                tr("payment_recorded"),
                tr("payment_recorded_msg", amount=format_money(amount), name=employee_name)
            )

            self.refresh_salaries()
            self.refresh_dashboard()
            signals.data_changed.emit("all")

        pay_btn.clicked.connect(on_pay)

        btns.addWidget(cancel_btn)
        btns.addWidget(pay_btn)
        d_layout.addLayout(btns)

        dialog.setStyleSheet(f"QDialog {{ background-color: {c['bg_main']}; font-family: 'Vazirmatn'; }}")
        dialog.exec()

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
            SELECT cm.memberId, ep.baseSalary, ep.salaryType, ep.workDays,
                   ep.workHours, ep.employmentType, ep.allowOvertime
            FROM complex_members cm
            LEFT JOIN employee_profiles ep ON ep.memberId = cm.memberId
            WHERE cm.complexId = %s AND cm.role IN ('employee', 'both') AND cm.isActive = '1'
            """,
            (self.complex_id,)
        )

        if not members:
            NiceMessageBox.warning(self, tr("error"), tr("no_salary_to_calc"))
            return

        for m in members:
            self.calculate_one_salary(
                m["memberId"], m.get("baseSalary") or 0,
                m.get("salaryType") or "monthly", m.get("workDays") or 26,
                m.get("workHours") or 8, m.get("employmentType") or "fullTime",
                m.get("allowOvertime") or "1", year, month
            )

        self.refresh_salaries()
        NiceMessageBox.success(self, tr("calc_done"), tr("calc_done_msg"))
        signals.data_changed.emit("all")

    def calculate_one_salary(self, member_id, base_salary, salary_type, work_days,
                             work_hours, employment_type, allow_overtime, year, month):
        base_salary = float(base_salary or 0)
        work_days = float(work_days or 26)
        work_hours = float(work_hours or 8)

        emp_ratio = 0.5 if employment_type == "partTime" else 1.0

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
            SELECT COUNT(DISTINCT workDate) AS days,
                   COALESCE(SUM(workedMinutes), 0) AS minutes,
                   COALESCE(SUM(overtimeMinutes), 0) AS overtime
            FROM attendance
            WHERE memberId = %s AND workDate BETWEEN %s AND %s AND approvalStatus = 'approved'
            """,
            (member_id, first_day, last_day)
        )

        days_present = float(att["days"] or 0) if att else 0
        minutes_worked = float(att["minutes"] or 0) if att else 0
        overtime_min = float(att["overtime"] or 0) if att else 0

        if salary_type == "monthly":
            ratio = days_present / work_days if work_days else 0
            calc_base = base_salary * ratio
            hourly_rate = (base_salary / work_days / work_hours) if (work_days and work_hours) else 0
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

        calc_base *= emp_ratio
        overtime_amount *= emp_ratio

        if str(allow_overtime) != "1":
            overtime_amount = 0

        bonus_row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total FROM bonuses
            WHERE memberId = %s AND YEAR(bonusDate) = %s AND MONTH(bonusDate) = %s AND status = 'approved'
            """,
            (member_id, gy, gm)
        )
        bonus_amount = float(bonus_row["total"] or 0) if bonus_row else 0

        ded_row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total FROM deductions
            WHERE memberId = %s AND YEAR(deductionDate) = %s AND MONTH(deductionDate) = %s AND status = 'approved'
            """,
            (member_id, gy, gm)
        )
        deduction_amount = float(ded_row["total"] or 0) if ded_row else 0

        loan_row = self.db.fetch_one(
            """
            SELECT COALESCE(SUM(li.amount), 0) AS total
            FROM loan_installments li
            INNER JOIN loans l ON l.loanId = li.loanId
            WHERE l.memberId = %s AND YEAR(li.dueDate) = %s AND MONTH(li.dueDate) = %s AND li.status = 'pending'
            """,
            (member_id, gy, gm)
        )
        loan_amount = float(loan_row["total"] or 0) if loan_row else 0

        final = calc_base + overtime_amount + bonus_amount - deduction_amount - loan_amount
        if final < 0:
            final = 0

        existing = self.db.fetch_one(
            "SELECT salaryId, status FROM salaries WHERE memberId = %s AND salaryYear = %s AND salaryMonth = %s LIMIT 1",
            (member_id, year, month)
        )

        if existing:
            current_status = existing.get("status") or "draft"
            new_status = "paid" if current_status == "paid" else "calculated"
            self.db.execute(
                """
                UPDATE salaries SET baseSalary = %s, overtimeAmount = %s,
                    bonusAmount = %s, deductionAmount = %s, loanAmount = %s,
                    finalAmount = %s, status = %s WHERE salaryId = %s
                """,
                (calc_base, overtime_amount, bonus_amount, deduction_amount,
                 loan_amount, final, new_status, existing["salaryId"])
            )
        else:
            self.db.execute(
                """
                INSERT INTO salaries (memberId, salaryYear, salaryMonth, baseSalary,
                    overtimeAmount, bonusAmount, deductionAmount, loanAmount,
                    finalAmount, status, createdDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'calculated', NOW())
                """,
                (member_id, year, month, calc_base, overtime_amount, bonus_amount,
                 deduction_amount, loan_amount, final)
            )

    # =====================================================
    # BONUSES / DEDUCTIONS / HISTORY
    # =====================================================

    def refresh_bonuses(self):
        if not self.is_owner or not self.complex_id:
            return

        while self.bonuses_layout.count():
            item = self.bonuses_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if getattr(self, 'bonus_filter_date', None) is not None:
            day_py = self.bonus_filter_date.toPython()
            rows = self.db.fetch_all(
                """
                SELECT b.bonusId, b.amount, b.title, b.description, b.bonusDate, b.status, u.name
                FROM bonuses b
                INNER JOIN complex_members cm ON cm.memberId = b.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s AND DATE(b.bonusDate) = %s
                ORDER BY b.bonusDate DESC, b.bonusId DESC
                """,
                (self.complex_id, day_py)
            )
        else:
            rows = self.db.fetch_all(
                """
                SELECT b.bonusId, b.amount, b.title, b.description, b.bonusDate, b.status, u.name
                FROM bonuses b
                INNER JOIN complex_members cm ON cm.memberId = b.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                ORDER BY b.bonusDate DESC, b.bonusId DESC LIMIT 100
                """,
                (self.complex_id,)
            )

        if not rows:
            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setAttribute(Qt.WA_StyledBackground, True)
            empty.setMinimumHeight(120)
            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)
            t = QLabel(tr("no_bonus"))
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

        name = QLabel(row.get("name") or "—")
        name.setObjectName("empName")
        name.setMinimumWidth(140)
        name.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        title = QLabel(row.get("title") or "—")
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
        self._open_add_transaction_dialog("bonus")

    def open_add_deduction_dialog(self):
        self._open_add_transaction_dialog("deduction")

    def _open_add_transaction_dialog(self, kind):
        is_bonus = (kind == "bonus")
        c = theme_manager.colors()

        dialog = QDialog(self)
        title_text = tr("add_bonus_title") if is_bonus else tr("add_deduction_title")
        dialog.setWindowTitle(title_text)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(440)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setStyleSheet(f"color: {c['text_main']}; font-size: 16px; font-weight: 700; background: transparent;")
        layout.addWidget(title)

        emp_lbl = QLabel(tr("employee_label"))
        emp_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        emp_combo = RoundedComboBox()
        emp_combo.setFixedHeight(44)
        emp_combo.setAttribute(Qt.WA_StyledBackground, True)
        emp_combo.setCursor(Qt.PointingHandCursor)
        emp_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
                padding: 0 16px;
                color: {c['text_main']};
                font-size: 13px;
            }}
            QComboBox::drop-down {{ width: 28px; border: none; }}
            QComboBox::down-arrow {{
                image: none;
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {c['accent']};
                margin-right: 10px;
            }}
        """)

        members = self.db.fetch_all(
            """
            SELECT cm.memberId, u.name FROM complex_members cm
            INNER JOIN users u ON u.userId = cm.userId
            WHERE cm.complexId = %s AND cm.role IN ('employee', 'both') AND cm.isActive = '1'
            ORDER BY u.name ASC
            """,
            (self.complex_id,)
        )

        for m in members or []:
            emp_combo.addItem(m["name"] or "—", m["memberId"])

        layout.addWidget(emp_lbl)
        layout.addWidget(emp_combo)

        t_lbl = QLabel(tr("bonus_title") if is_bonus else tr("deduction_title"))
        t_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        title_input = QLineEdit()
        title_input.setPlaceholderText(tr("bonus_title_ph") if is_bonus else tr("deduction_title_ph"))
        title_input.setFixedHeight(44)
        title_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
                padding: 0 18px;
                color: {c['text_main']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                background-color: {c['bg_card']};
                border: 2px solid {c['accent']};
            }}
        """)

        layout.addWidget(t_lbl)
        layout.addWidget(title_input)

        a_lbl = QLabel(tr("amount_label"))
        a_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        amount_input = QLineEdit()
        amount_input.setPlaceholderText(tr("amount_ph"))
        amount_input.setLayoutDirection(Qt.LeftToRight)
        amount_input.setFixedHeight(44)
        amount_input.setStyleSheet(title_input.styleSheet())

        layout.addWidget(a_lbl)
        layout.addWidget(amount_input)

        d_lbl = QLabel(tr("desc_optional"))
        d_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        desc_input = QLineEdit()
        desc_input.setFixedHeight(44)
        desc_input.setStyleSheet(title_input.styleSheet())

        layout.addWidget(d_lbl)
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

        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

        def on_save():
            if emp_combo.count() == 0:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_no_employee"))
                return

            member_id = emp_combo.currentData()
            title_text = title_input.text().strip()
            amount_text = amount_input.text().strip()
            desc_text = desc_input.text().strip()

            if not title_text:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_title"))
                return
            if not amount_text:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_amount"))
                return

            try:
                amount = float(amount_text.replace(",", "").replace("٬", ""))
            except ValueError:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_invalid_amount"))
                return

            today = date.today()

            if is_bonus:
                self.db.execute(
                    """
                    INSERT INTO bonuses (memberId, amount, title, description, bonusDate,
                        createdBy, status, approvedBy)
                    VALUES (%s, %s, %s, %s, %s, %s, 'approved', %s)
                    """,
                    (member_id, amount, title_text, desc_text or None, today, self.user_id, self.user_id)
                )
                dialog.accept()
                self.refresh_bonuses()
                NiceMessageBox.success(self, tr("saved"), tr("bonus_saved"))
            else:
                self.db.execute(
                    """
                    INSERT INTO deductions (memberId, amount, title, description, deductionDate,
                        createdBy, status, approvedBy)
                    VALUES (%s, %s, %s, %s, %s, %s, 'approved', %s)
                    """,
                    (member_id, amount, title_text, desc_text or None, today, self.user_id, self.user_id)
                )
                dialog.accept()
                self.refresh_deductions()
                NiceMessageBox.success(self, tr("saved"), tr("deduction_saved"))

            signals.data_changed.emit("all")

        save_btn.clicked.connect(on_save)
        dialog.setStyleSheet(f"QDialog {{ background-color: {c['bg_main']}; font-family: 'Vazirmatn'; }}")
        dialog.exec()

    def refresh_deductions(self):
        if not self.is_owner or not self.complex_id:
            return

        while self.deductions_layout.count():
            item = self.deductions_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if getattr(self, 'deduction_filter_date', None) is not None:
            day_py = self.deduction_filter_date.toPython()
            rows = self.db.fetch_all(
                """
                SELECT d.deductionId, d.amount, d.title, d.description, d.deductionDate, d.status, u.name
                FROM deductions d
                INNER JOIN complex_members cm ON cm.memberId = d.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s AND DATE(d.deductionDate) = %s
                ORDER BY d.deductionDate DESC, d.deductionId DESC
                """,
                (self.complex_id, day_py)
            )
        else:
            rows = self.db.fetch_all(
                """
                SELECT d.deductionId, d.amount, d.title, d.description, d.deductionDate, d.status, u.name
                FROM deductions d
                INNER JOIN complex_members cm ON cm.memberId = d.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                ORDER BY d.deductionDate DESC, d.deductionId DESC LIMIT 100
                """,
                (self.complex_id,)
            )

        if not rows:
            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setAttribute(Qt.WA_StyledBackground, True)
            empty.setMinimumHeight(120)
            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)
            t = QLabel(tr("no_deduction"))
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

        name = QLabel(row.get("name") or "—")
        name.setObjectName("empName")
        name.setMinimumWidth(140)
        name.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        title = QLabel(row.get("title") or "—")
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

    def refresh_history(self):
        if not self.is_owner or not self.complex_id:
            return

        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if getattr(self, 'history_filter_date', None) is not None:
            day_py = self.history_filter_date.toPython()
            rows = self.db.fetch_all(
                """
                SELECT p.paymentId, p.amount, p.paymentType, p.paymentDate, p.description, u.name
                FROM payments p
                INNER JOIN complex_members cm ON cm.memberId = p.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s AND DATE(p.paymentDate) = %s
                ORDER BY p.paymentDate DESC, p.paymentId DESC
                """,
                (self.complex_id, day_py)
            )
        else:
            rows = self.db.fetch_all(
                """
                SELECT p.paymentId, p.amount, p.paymentType, p.paymentDate, p.description, u.name
                FROM payments p
                INNER JOIN complex_members cm ON cm.memberId = p.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                ORDER BY p.paymentDate DESC, p.paymentId DESC LIMIT 100
                """,
                (self.complex_id,)
            )

        if not rows:
            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setAttribute(Qt.WA_StyledBackground, True)
            empty.setMinimumHeight(120)
            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)
            t = QLabel(tr("no_payment"))
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

        name = QLabel(row.get("name") or "—")
        name.setObjectName("empName")
        name.setMinimumWidth(140)
        name.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        ptype_map = {
            "salary": tr("payment_salary"),
            "job": tr("payment_job"),
            "bonus": tr("payment_bonus"),
            "advance": tr("payment_advance"),
            "other": tr("payment_other"),
        }
        ptype = ptype_map.get(row.get("paymentType"), tr("salary_type_pay"))

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

        my_name = self.my_name
        c = theme_manager.colors()

        profile = self.db.fetch_one(
            """
            SELECT jobTitle, salaryType, baseSalary, workDays, workHours,
                   employmentType, allowOvertime
            FROM employee_profiles WHERE memberId = %s LIMIT 1
            """,
            (self.member_id,)
        )

        current_salary = self.db.fetch_one(
            """
            SELECT salaryId, baseSalary, overtimeAmount, bonusAmount,
                   deductionAmount, loanAmount, finalAmount, status, paidDate
            FROM salaries
            WHERE memberId = %s AND salaryYear = %s AND salaryMonth = %s LIMIT 1
            """,
            (self.member_id, self.selected_year, self.selected_month)
        )

        total_paid = 0
        if current_salary and current_salary.get("salaryId"):
            paid_row = self.db.fetch_one(
                "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE salaryId = %s AND paymentType = 'salary'",
                (current_salary["salaryId"],)
            )
            total_paid = float(paid_row["total"] or 0) if paid_row else 0

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
            SELECT COUNT(DISTINCT workDate) AS days,
                   COALESCE(SUM(workedMinutes), 0) AS minutes,
                   COALESCE(SUM(overtimeMinutes), 0) AS overtime
            FROM attendance
            WHERE memberId = %s AND workDate BETWEEN %s AND %s AND approvalStatus = 'approved'
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

        s_title = QLabel(f"📊  {tr('employee_history_title')} {MONTH_NAMES[self.selected_month - 1]} {self.selected_year}")
        s_title.setStyleSheet(f"color: {c['text_main']}; font-size: 15px; font-weight: 800; background: transparent;")
        s_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        s_layout.addWidget(s_title)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background-color: {c['border']}; border: none;")
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
                add_row(f"{tr('base_salary_short')}:", format_money(calc_base))
            if overtime > 0:
                ot_h = overtime_min // 60
                ot_m = overtime_min % 60
                add_row(f"{tr('overtime')} ({ot_h}{tr('hour_short')} {ot_m}{tr('min_short')}):", f"+ {format_money(overtime)}", "green")
            if bonus > 0:
                add_row(f"{tr('tab_bonuses')}:", f"+ {format_money(bonus)}", "green")
            if deduction > 0:
                add_row(f"{tr('tab_deductions')}:", f"- {format_money(deduction)}", "red")
            if loan > 0:
                add_row(f"{tr('payment_advance')}:", f"- {format_money(loan)}", "red")

            div2 = QFrame()
            div2.setFixedHeight(1)
            div2.setStyleSheet(f"background-color: {c['border']}; border: none;")
            s_layout.addWidget(div2)

            add_row(f"{tr('final_salary')}:", format_money(final), "blue")
            add_row(f"{tr('paid_so_far')}:", format_money(total_paid), "green")

            remain_amount = max(0, final - total_paid)
            if remain_amount > 0:
                add_row(f"{tr('remain_to_pay')}:", format_money(remain_amount), "red")

            EPS = 1

            if total_paid >= (final - EPS) and final > 0:
                status_text = tr("paid_status")
                status_color = "#16A34A"
                status_bg = "#EAF6EE"
            elif total_paid > 0:
                status_text = tr("partial_status")
                status_color = "#B87900"
                status_bg = "#FFF4DD"
            elif current_salary.get("status") == "calculated":
                status_text = tr("pending_status")
                status_color = "#B87900"
                status_bg = "#FFF4DD"
            else:
                status_text = tr("draft_status")
                status_color = "#526273"
                status_bg = "#EEF2F6"

            status_lbl = QLabel(status_text)
            status_lbl.setAlignment(Qt.AlignCenter)
            status_lbl.setFixedHeight(32)
            status_lbl.setStyleSheet(f"color: {status_color}; background-color: {status_bg}; border: none; border-radius: 16px; font-size: 12px; font-weight: 700; padding: 0 16px;")
            s_layout.addSpacing(4)
            s_layout.addWidget(status_lbl)
        else:
            no_calc = QLabel(tr("no_calc_wait") + "\n" + tr("no_calc_wait_sub"))
            no_calc.setAlignment(Qt.AlignCenter)
            no_calc.setWordWrap(True)
            no_calc.setStyleSheet(f"color: {c['text_dim']}; background-color: {c['bg_input']}; border: 1px dashed {c['border']}; border-radius: 14px; padding: 20px 16px; font-size: 12px; font-weight: 600;")
            s_layout.addWidget(no_calc)

        s_layout.addSpacing(6)
        att_title = QLabel(tr("attendance_summary"))
        att_title.setStyleSheet(f"color: {c['text_main']}; font-size: 13px; font-weight: 700; background: transparent;")
        att_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        s_layout.addWidget(att_title)

        add_row(f"{tr('days_present')}:", f"{days_present}")
        total_h = minutes_worked // 60
        total_m = minutes_worked % 60
        add_row(f"{tr('total_work_hours')}:", f"{total_h}{tr('hour_short')} {total_m}{tr('min_short')}")

        ot_h = overtime_min // 60
        ot_m = overtime_min % 60
        if overtime_min > 0:
            add_row(f"{tr('overtime')}:", f"{ot_h}{tr('hour_short')} {ot_m}{tr('min_short')}", "green")
        else:
            add_row(f"{tr('overtime')}:", tr("doesnt_have_short"))

        if current_salary or profile:
            detail_btn = QPushButton(tr("view_details"))
            detail_btn.setObjectName("detailBtn")
            detail_btn.setFixedHeight(38)
            detail_btn.setCursor(Qt.PointingHandCursor)
            detail_btn.setAttribute(Qt.WA_StyledBackground, True)
            detail_btn.clicked.connect(
                lambda checked=False, m=self.member_id, n=my_name:
                self.open_details_dialog({"memberId": m, "name": n})
            )
            s_layout.addSpacing(6)
            s_layout.addWidget(detail_btn)

        self.emp_history_layout.addWidget(summary_card)

        history_title = QLabel(tr("payment_history_emp"))
        history_title.setObjectName("sectionTitle")
        history_title.setStyleSheet(f"color: {c['text_main']}; font-size: 14px; font-weight: 700; background: transparent; padding: 8px 4px 0px 4px;")
        self.emp_history_layout.addWidget(history_title)

        rows = self.db.fetch_all(
            """
            SELECT paymentId, amount, paymentType, paymentDate, description
            FROM payments WHERE memberId = %s
            ORDER BY paymentDate DESC, paymentId DESC LIMIT 100
            """,
            (self.member_id,)
        )

        if not rows:
            empty = QFrame()
            empty.setObjectName("emptyCard")
            empty.setAttribute(Qt.WA_StyledBackground, True)
            empty.setMinimumHeight(100)
            el = QVBoxLayout(empty)
            el.setContentsMargins(20, 30, 20, 30)
            t = QLabel(tr("no_payment_for_you"))
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

    # =====================================================
    # DETAILS DIALOG
    # =====================================================

    def open_details_dialog(self, row):
        member_id = row.get("memberId")
        name = row.get("name") or "—"
        if not member_id:
            return

        year = self.selected_year
        month = self.selected_month
        c = theme_manager.colors()

        profile = self.db.fetch_one(
            """
            SELECT jobTitle, employmentType, salaryType, baseSalary,
                   workDays, workHours, allowOvertime
            FROM employee_profiles WHERE memberId = %s LIMIT 1
            """,
            (member_id,)
        )

        if not profile:
            NiceMessageBox.error(self, tr("error"), "No profile.")
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
            SELECT COUNT(DISTINCT workDate) AS days,
                   COALESCE(SUM(workedMinutes), 0) AS minutes,
                   COALESCE(SUM(overtimeMinutes), 0) AS overtime
            FROM attendance
            WHERE memberId = %s AND workDate BETWEEN %s AND %s AND approvalStatus = 'approved'
            """,
            (member_id, first_day, last_day)
        )

        days_present = int(att["days"] or 0) if att else 0
        minutes_worked = int(att["minutes"] or 0) if att else 0
        overtime_min = int(att["overtime"] or 0) if att else 0

        salary = self.db.fetch_one(
            """
            SELECT baseSalary, overtimeAmount, bonusAmount, deductionAmount,
                   loanAmount, finalAmount, status, paidDate
            FROM salaries
            WHERE memberId = %s AND salaryYear = %s AND salaryMonth = %s LIMIT 1
            """,
            (member_id, year, month)
        )

        total_paid = 0
        if salary:
            salary_id_row = self.db.fetch_one(
                "SELECT salaryId FROM salaries WHERE memberId = %s AND salaryYear = %s AND salaryMonth = %s LIMIT 1",
                (member_id, year, month)
            )
            if salary_id_row:
                paid_row = self.db.fetch_one(
                    "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE salaryId = %s AND paymentType = 'salary'",
                    (salary_id_row["salaryId"],)
                )
                total_paid = float(paid_row["total"] or 0) if paid_row else 0

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("details_title"))
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(650)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QScrollArea::viewport { background: transparent; }")
        vbar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(vbar)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_main']};")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        header_frame = QFrame()
        header_frame.setAttribute(Qt.WA_StyledBackground, True)
        header_frame.setObjectName("detailsHeader")
        header_frame.setStyleSheet(f"""
            QFrame#detailsHeader {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 20px;
            }}
        """)
        h_layout = QVBoxLayout(header_frame)
        h_layout.setContentsMargins(22, 18, 22, 18)
        h_layout.setSpacing(6)

        h_name = QLabel(name)
        h_name.setStyleSheet(f"color: {c['text_main']}; font-size: 17px; font-weight: 800; background: transparent;")

        h_sub = QLabel(f"📅  {MONTH_NAMES[month - 1]} {year}   •   {tr('details_title')}")
        h_sub.setStyleSheet(f"color: {c['accent']}; font-size: 11px; font-weight: 600; background: transparent;")

        h_layout.addWidget(h_name)
        h_layout.addWidget(h_sub)
        layout.addWidget(header_frame)

        section1 = self._create_section(tr("profile_info_section"))
        emp_map = {"fullTime": tr("full_time"), "partTime": tr("part_time")}
        st_map = {"monthly": tr("monthly"), "daily": tr("daily"), "hourly": tr("hourly")}
        allow_ot = str(profile.get("allowOvertime") or "1") == "1"

        section1["layout"].addWidget(self._create_row(tr("job"), profile.get("jobTitle") or "—"))
        section1["layout"].addWidget(self._create_row(tr("employment_type"), emp_map.get(profile.get("employmentType"), "—")))
        section1["layout"].addWidget(self._create_row(tr("salary_type"), st_map.get(profile.get("salaryType"), "—")))
        section1["layout"].addWidget(self._create_row(tr("base_salary_short"), format_money(profile.get("baseSalary") or 0) + " " + tr("toman")))
        section1["layout"].addWidget(self._create_row(tr("overtime_allow"), tr("has") if allow_ot else tr("doesnt_have")))
        layout.addWidget(section1["frame"])

        section2 = self._create_section(tr("attendance_section"))
        section2["layout"].addWidget(self._create_row(tr("days_present"), f"{days_present}"))
        th = minutes_worked // 60
        tm = minutes_worked % 60
        section2["layout"].addWidget(self._create_row(tr("total_work_hours"), f"{th} {tr('hour_short')} {tm} {tr('min_short')}"))
        oh = overtime_min // 60
        om = overtime_min % 60
        section2["layout"].addWidget(self._create_row(tr("overtime_month"), f"{oh} {tr('hour_short')} {om} {tr('min_short')}"))
        layout.addWidget(section2["frame"])

        if salary:
            section4 = self._create_section(tr("salary_details_section"))

            calc_base = float(salary.get("baseSalary") or 0)
            ot_amt = float(salary.get("overtimeAmount") or 0)
            bonus_amt = float(salary.get("bonusAmount") or 0)
            ded_amt = float(salary.get("deductionAmount") or 0)
            loan_amt = float(salary.get("loanAmount") or 0)
            final_amt = float(salary.get("finalAmount") or 0)

            section4["layout"].addWidget(self._create_row(tr("base_calc_short"), "+ " + format_money(calc_base)))

            if ot_amt > 0:
                section4["layout"].addWidget(self._create_row(tr("overtime"), "+ " + format_money(ot_amt), "green"))
            if bonus_amt > 0:
                section4["layout"].addWidget(self._create_row(tr("tab_bonuses"), "+ " + format_money(bonus_amt), "green"))
            if ded_amt > 0:
                section4["layout"].addWidget(self._create_row(tr("tab_deductions"), "- " + format_money(ded_amt), "red"))
            if loan_amt > 0:
                section4["layout"].addWidget(self._create_row(tr("payment_advance"), "- " + format_money(loan_amt), "red"))

            divider = QFrame()
            divider.setFixedHeight(1)
            divider.setStyleSheet(f"background-color: {c['border']}; border: none;")
            section4["layout"].addWidget(divider)

            final_row = QFrame()
            final_row.setAttribute(Qt.WA_StyledBackground, True)
            final_row.setObjectName("finalRow")
            final_row.setStyleSheet(f"""
                QFrame#finalRow {{
                    background-color: {c['accent_light']};
                    border: none;
                    border-radius: 16px;
                }}
            """)

            fr_layout = QHBoxLayout(final_row)
            fr_layout.setContentsMargins(16, 14, 16, 14)
            fr_layout.setSpacing(8)

            fr_lbl = QLabel(tr("final_salary"))
            fr_lbl.setStyleSheet(f"color: {c['accent']}; font-size: 13px; font-weight: 800; background: transparent;")

            fr_val = QLabel(format_money(final_amt) + " " + tr("toman"))
            fr_val.setStyleSheet(f"color: {c['accent']}; font-size: 15px; font-weight: 800; background: transparent;")
            fr_val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            fr_layout.addWidget(fr_lbl)
            fr_layout.addStretch()
            fr_layout.addWidget(fr_val)
            section4["layout"].addWidget(final_row)

            section4["layout"].addWidget(self._create_row(tr("paid_so_far"), format_money(total_paid) + " " + tr("toman"), "green"))
            remain_amt = max(0, final_amt - total_paid)
            if remain_amt > 0:
                section4["layout"].addWidget(self._create_row(tr("remain_to_pay"), format_money(remain_amt) + " " + tr("toman"), "red"))

            EPS = 1

            if total_paid >= (final_amt - EPS) and final_amt > 0:
                status_text = tr("paid_status")
                status_color = "#16A34A"
                status_bg = "#EAF6EE"
            elif total_paid > 0:
                status_text = tr("partial_status")
                status_color = "#B87900"
                status_bg = "#FFF4DD"
            elif salary.get("status") == "calculated":
                status_text = tr("pending_status")
                status_color = "#B87900"
                status_bg = "#FFF4DD"
            else:
                status_text = tr("draft_status")
                status_color = "#526273"
                status_bg = "#EEF2F6"

            status_row = QFrame()
            status_row.setAttribute(Qt.WA_StyledBackground, True)
            status_row.setObjectName("statusRow")
            status_row.setStyleSheet(f"""
                QFrame#statusRow {{
                    background-color: {status_bg};
                    border: none;
                    border-radius: 16px;
                }}
            """)

            sr_layout = QHBoxLayout(status_row)
            sr_layout.setContentsMargins(16, 12, 16, 12)

            sr_lbl = QLabel(tr("status") + ":")
            sr_lbl.setStyleSheet(f"color: {status_color}; font-size: 12px; font-weight: 700; background: transparent;")

            sr_val = QLabel(status_text)
            sr_val.setStyleSheet(f"color: {status_color}; font-size: 13px; font-weight: 800; background: transparent;")
            sr_val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            sr_layout.addWidget(sr_lbl)
            sr_layout.addStretch()
            sr_layout.addWidget(sr_val)
            section4["layout"].addWidget(status_row)

            layout.addWidget(section4["frame"])
        else:
            no_salary = QLabel(tr("no_calc_yet"))
            no_salary.setStyleSheet(f"color: {c['warning']}; background-color: {c['warning_bg']}; border: 1px solid {c['warning']}; border-radius: 16px; padding: 18px 20px; font-size: 13px; font-weight: 700;")
            no_salary.setWordWrap(True)
            no_salary.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_salary)

        layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        bottom = QFrame()
        bottom.setAttribute(Qt.WA_StyledBackground, True)
        bottom.setObjectName("bottomBar")
        bottom.setStyleSheet(f"""
            QFrame#bottomBar {{
                background-color: {c['bg_card']};
                border-top: 1px solid {c['border']};
            }}
        """)
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(24, 14, 24, 14)

        close_btn = QPushButton(tr("close"))
        close_btn.setFixedHeight(46)
        close_btn.setMinimumWidth(150)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setAttribute(Qt.WA_StyledBackground, True)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 23px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 28px;
            }}
            QPushButton:hover {{
                background-color: {c['accent_hover']};
            }}
        """)
        close_btn.clicked.connect(dialog.accept)

        bottom_layout.addStretch()
        bottom_layout.addWidget(close_btn)
        bottom_layout.addStretch()
        main_layout.addWidget(bottom)

        dialog.setStyleSheet(f"QDialog {{ background-color: {c['bg_main']}; font-family: 'Vazirmatn'; }}")
        dialog.exec()

    def _create_section(self, title_text):
        c = theme_manager.colors()
        frame = QFrame()
        frame.setAttribute(Qt.WA_StyledBackground, True)
        frame.setObjectName("detailSection")
        frame.setStyleSheet(f"""
            QFrame#detailSection {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 20px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setStyleSheet(f"color: {c['text_main']}; font-size: 14px; font-weight: 800; background: transparent;")
        layout.addWidget(title)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {c['border']}; border: none;")
        layout.addWidget(divider)

        return {"frame": frame, "layout": layout}

    def _create_row(self, label_text, value_text, kind="normal"):
        c = theme_manager.colors()
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 4, 0, 4)
        rl.setSpacing(12)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignTop | Qt.AlignVCenter)

        val = QLabel(value_text)
        if kind == "green":
            val.setStyleSheet(f"color: {c['success']}; font-size: 13px; font-weight: 700; background: transparent;")
        elif kind == "red":
            val.setStyleSheet(f"color: {c['danger']}; font-size: 13px; font-weight: 700; background: transparent;")
        elif kind == "blue":
            val.setStyleSheet(f"color: {c['accent']}; font-size: 14px; font-weight: 800; background: transparent;")
        else:
            val.setStyleSheet(f"color: {c['text_main']}; font-size: 13px; font-weight: 700; background: transparent;")

        val.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        val.setWordWrap(True)
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)

        rl.addWidget(lbl, 1)
        rl.addWidget(val, 2)
        return row