import os
from datetime import datetime, date, timedelta

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QDialog, QGridLayout,
    QComboBox, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect,
    QApplication
)

from PySide6.QtCore import (
    Qt, QTimer, QDate, QPoint, QSize, Signal, QRectF
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
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
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
            QListWidget {{background: transparent;border: none;outline: none;padding: 6px;color: {c['text_main']};font-family: "Vazirmatn";font-size: 12px;}}
            QListWidget::item {{background: transparent;color: {c['text_main']};border-radius: 10px;padding: 10px 14px;margin: 2px 4px;min-height: 20px;}}
            QListWidget::item:hover {{background-color: {c['bg_hover']};color: {c['accent']};}}
            QListWidget::item:selected {{background-color: {c['accent']};color: white;}}
            QScrollBar:vertical {{width: 8px;background: transparent;border: none;margin: 6px 2px;}}
            QScrollBar::handle:vertical {{background: {c['accent']};border-radius: 4px;min-height: 24px;}}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{height: 0px;}}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{background: transparent;}}
        """)

        for i in range(self.count()):
            item = QListWidgetItem(self.itemText(i))
            item.setData(Qt.UserRole, i)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setSizeHint(QSize(0, 40))
            self._list.addItem(item)
            if i == self.currentIndex():
                self._list.setCurrentItem(item)

        self._list.itemClicked.connect(self._on_item_clicked)
        card_layout.addWidget(self._list)

        self._popup.setStyleSheet(f"QFrame#comboCard {{background-color: {c['bg_card']};border: 1px solid {c['border']};border-radius: 16px;}}")

        count = max(self.count(), 1)
        content_h = count * 40 + 32
        popup_w = max(self.width(), 180)
        popup_h = min(content_h, 240)
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

WEEKDAY_NAMES = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یک‌شنبه"]
WEEKDAY_SHORT = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
MONTH_NAMES = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]

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

def jalali_month_days(jy, jm):
    if jm <= 6:
        return 31
    if jm <= 11:
        return 30
    if is_jalali_leap(jy):
        return 30
    return 29

def persian_date_long(d):
    if isinstance(d, datetime):
        d = d.date()
    jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
    weekday = WEEKDAY_NAMES[d.weekday()]
    return f"{weekday} {jd} {MONTH_NAMES[jm - 1]} {jy}"

def persian_date_short(d):
    if isinstance(d, datetime):
        d = d.date()
    jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
    return f"{jy:04d}/{jm:02d}/{jd:02d}"

def format_time_12h(dt):
    if dt is None:
        return "—"
    if isinstance(dt, datetime):
        h, m = dt.hour, dt.minute
    else:
        try:
            h, m = dt.hour, dt.minute
        except Exception:
            return str(dt)[:5]
    if h < 5:
        period = "بامداد"
    elif h < 12:
        period = "صبح"
    elif h < 13:
        period = "ظهر"
    elif h < 19:
        period = "عصر"
    else:
        period = "شب"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12}:{m:02d} {period}"

def format_money(amount):
    try:
        return f"{amount:,.0f}"
    except Exception:
        return "0"

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

    def __init__(self, parent=None, initial_qdate=None):
        super().__init__(parent)

        self._qdate = initial_qdate if initial_qdate is not None else QDate.currentDate()

        self.setObjectName("persianDateFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(42)
        self.setMinimumWidth(180)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 14, 0)
        layout.setSpacing(8)

        self.icon_label = QLabel("📅")
        self.icon_label.setObjectName("dateIconLabel")
        self.icon_label.setFixedSize(30, 30)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

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

    def to_python_date(self):
        return date(self._qdate.year(), self._qdate.month(), self._qdate.day())

    def setDate(self, qdate):
        self._qdate = qdate
        self._refresh_text()

    def _open_dialog(self):
        self._popup = PersianCalendarPopup(self, self._qdate)
        self._popup.dateSelected.connect(self._on_date_selected)
        global_pos = self.mapToGlobal(QPoint(0, self.height() + 4))

        try:
            screen = QApplication.primaryScreen().availableGeometry()
            x = global_pos.x()
            if x + self._popup.width() > screen.right():
                x = screen.right() - self._popup.width()
            if x < screen.left():
                x = screen.left()
            global_pos.setX(x)
        except Exception:
            pass

        self._popup.move(global_pos)
        self._popup.show()

    def _on_date_selected(self, qdate):
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
        self.setFixedSize(340, 230)

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
        card.setStyleSheet(f"background-color: {c['bg_card']};border-radius: 20px;border: 1px solid {c['border']};")
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(10)

        icon_label = QLabel(icon_char)
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"background-color: {bg};color: {color};border-radius: 24px;font-size: 22px;font-weight: 700;")

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()
        layout.addLayout(icon_row)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {c['text_main']};font-size: 14px;font-weight: 700;background: transparent;border: none;")
        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"color: {c['text_dim']};font-size: 11px;background: transparent;border: none;")
        layout.addWidget(text_label)
        layout.addStretch()

        btn = QPushButton(tr("ok"))
        btn.setFixedHeight(38)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(100)
        btn.setStyleSheet(f"background-color: {color};color: white;border: none;border-radius: 19px;font-size: 12px;font-weight: 600;padding: 0px 20px;")
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

# =========================================================
# STAT BOX HELPER
# =========================================================

def create_stat_box(label_text, value_text, color_kind="blue", min_width=100):
    c = theme_manager.colors()

    box = QFrame()
    box.setObjectName("statBox")
    box.setAttribute(Qt.WA_StyledBackground, True)
    box.setMinimumWidth(min_width)

    if color_kind == "green":
        bg = c['success_bg']
        fg = c['success']
    elif color_kind == "red":
        bg = "#FFE5E8"
        fg = "#D93025"
    elif color_kind == "orange":
        bg = "#FFF4DD"
        fg = "#B87900"
    else:
        bg = c['accent_light']
        fg = c['accent']

    box.setStyleSheet(f"""
        QFrame#statBox {{
            background-color: {bg};
            border: none;
            border-radius: 14px;
        }}
    """)

    layout = QVBoxLayout(box)
    layout.setContentsMargins(14, 8, 14, 8)
    layout.setSpacing(2)

    lbl = QLabel(label_text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        f"color: {c['text_dim']}; font-size: 9px; "
        f"font-weight: 700; background: transparent;"
    )

    val = QLabel(value_text)
    val.setAlignment(Qt.AlignCenter)
    val.setStyleSheet(
        f"color: {fg}; font-size: 13px; "
        f"font-weight: 800; background: transparent;"
    )

    layout.addWidget(lbl)
    layout.addWidget(val)
    return box

# =========================================================
# REPORTS WINDOW
# =========================================================

class ReportsWindow(QWidget):

    def __init__(self, parent_window=None, phone_number=None, complex_id=None):
        super().__init__()

        self.parent_window = parent_window
        self.phone_number = phone_number
        self.complex_id = complex_id

        if self.phone_number is None and parent_window is not None:
            self.phone_number = getattr(parent_window, "phone_number", None)

        if self.complex_id is None and parent_window is not None:
            self.complex_id = getattr(parent_window, "complex_id", None)
            if not self.complex_id:
                getter = getattr(parent_window, "get_current_complex_id", None)
                if callable(getter):
                    self.complex_id = getter()

        self.db = Database()
        self.user_id = None

        # پیش‌فرض: ۳ ماه اخیر
        self.date_range = "last_3_months"

        self.summary = {
            "employees": 0,
            "hours": 0,
            "payments": 0,
            "tasks": 0,
        }

        self.setWindowTitle(tr("reports_title"))
        self.setMinimumSize(500, 400)
        self.resize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("reportsWindow")

        self.load_user_id()
        self.setup_ui()
        self.calculate_reports()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)
        signals.data_changed.connect(self.on_data_changed)

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("reports_title"))
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
        self.calculate_reports()

    def on_data_changed(self, kind):
        self.calculate_reports()

    def load_user_id(self):
        if not self.phone_number:
            return
        try:
            user = self.db.fetch_one(
                "SELECT userId FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if user:
                self.user_id = user["userId"]
        except Exception as e:
            print("REPORTS LOAD USER ID ERROR:", e)

    # =====================================================
    # DATE RANGE (فقط preset)
    # =====================================================

    def _compute_preset_range(self):
        today = date.today()

        if self.date_range == "today":
            return today, today

        if self.date_range == "this_week":
            start = today - timedelta(days=today.weekday())
            return start, today

        if self.date_range == "this_month":
            jy, jm, jd = gregorian_to_jalali(today.year, today.month, today.day)
            gy, gm, gd = jalali_to_gregorian(jy, jm, 1)
            return date(gy, gm, gd), today

        if self.date_range == "last_3_months":
            jy, jm, jd = gregorian_to_jalali(today.year, today.month, today.day)
            jm -= 3
            if jm < 1:
                jm += 12
                jy -= 1
            gy, gm, gd = jalali_to_gregorian(jy, jm, 1)
            return date(gy, gm, gd), today

        if self.date_range == "last_year":
            jy, jm, jd = gregorian_to_jalali(today.year, today.month, today.day)
            jy -= 1
            gy, gm, gd = jalali_to_gregorian(jy, 1, 1)
            return date(gy, gm, gd), today

        return today, today

    def get_date_range_gregorian(self):
        return self._compute_preset_range()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        # HEADER
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(38, 38)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title = QLabel(tr("reports_title"))
        title.setObjectName("reportsTitle")

        subtitle = QLabel(tr("reports_subtitle"))
        subtitle.setObjectName("reportsSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # FILTER BOX (فقط preset)
        filter_box = QFrame()
        filter_box.setObjectName("filterBox")
        filter_box.setAttribute(Qt.WA_StyledBackground, True)

        filter_layout = QVBoxLayout(filter_box)
        filter_layout.setContentsMargins(16, 14, 16, 14)
        filter_layout.setSpacing(10)

        filter_title = QLabel("📅  انتخاب بازه زمانی")
        filter_title.setObjectName("filterLabel")
        filter_title.setAlignment(Qt.AlignRight)
        filter_layout.addWidget(filter_title)

        preset_row = QHBoxLayout()
        preset_row.setSpacing(8)

        presets = [
            ("امروز", "today"),
            ("این هفته", "this_week"),
            ("این ماه", "this_month"),
            ("۳ ماه اخیر", "last_3_months"),
            ("۱ سال اخیر", "last_year"),
        ]

        self.preset_buttons = []
        for label, key in presets:
            btn = QPushButton(label)
            btn.setObjectName("presetBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(38)
            btn.clicked.connect(
                lambda checked=False, k=key: self.on_preset_selected(k)
            )
            preset_row.addWidget(btn)
            self.preset_buttons.append((key, btn))

        preset_row.addStretch()
        filter_layout.addLayout(preset_row)

        main_layout.addWidget(filter_box)

        # SCROLL
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        round_bar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(round_bar)

        content = QWidget()
        content.setObjectName("scrollContent")
        content.setAttribute(Qt.WA_TranslucentBackground, True)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(4, 4, 8, 4)
        content_layout.setSpacing(14)

        summary_title = QLabel(tr("report_summary"))
        summary_title.setObjectName("sectionTitle")
        content_layout.addWidget(summary_title)

        summary_grid = QGridLayout()
        summary_grid.setSpacing(12)

        self.emp_value = self.create_summary_card(
            summary_grid, 0, 0, "👥",
            tr("employees_count_title"), "0", "statBlue"
        )
        self.hours_value = self.create_summary_card(
            summary_grid, 0, 1, "◷",
            tr("working_hours_title"), "0", "statBlue"
        )
        self.pay_value = self.create_summary_card(
            summary_grid, 0, 2, "₮",
            tr("total_payments"), "0", "statGreen"
        )
        self.tasks_value = self.create_summary_card(
            summary_grid, 0, 3, "✓",
            tr("tasks_done"), "0", "statGreen"
        )

        content_layout.addLayout(summary_grid)

        available_title = QLabel(tr("available_reports"))
        available_title.setObjectName("sectionTitle")
        content_layout.addWidget(available_title)

        reports_grid = QGridLayout()
        reports_grid.setSpacing(12)

        self.create_report_card(
            reports_grid, 0, 0, "◷",
            tr("report_attendance"),
            tr("report_attendance_desc"),
            "attendance"
        )
        self.create_report_card(
            reports_grid, 0, 1, "₮",
            tr("report_finance"),
            tr("report_finance_desc"),
            "finance"
        )
        self.create_report_card(
            reports_grid, 1, 0, "👥",
            tr("report_employees"),
            tr("report_employees_desc"),
            "employees"
        )
        self.create_report_card(
            reports_grid, 1, 1, "✓",
            tr("report_tasks"),
            tr("report_tasks_desc"),
            "tasks"
        )

        content_layout.addLayout(reports_grid)
        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        self.apply_stylesheet()
        self._refresh_preset_buttons()

    def _refresh_preset_buttons(self):
        c = theme_manager.colors()
        for key, btn in self.preset_buttons:
            if key == self.date_range:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c['accent']};
                        color: white;
                        border: none;
                        border-radius: 19px;
                        padding: 0 20px;
                        font-size: 12px;
                        font-weight: 700;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c['bg_input']};
                        color: {c['text_dim']};
                        border: 1px solid {c['border']};
                        border-radius: 19px;
                        padding: 0 20px;
                        font-size: 12px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color: {c['accent_light']};
                        color: {c['accent']};
                        border: 1px solid {c['accent']};
                    }}
                """)

    def on_preset_selected(self, key):
        self.date_range = key
        self._refresh_preset_buttons()
        self.calculate_reports()

    def create_summary_card(self, grid, row, col, icon, title, value, box_name):
        card = QFrame()
        card.setObjectName(box_name)
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(100)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        icon_label.setFixedSize(42, 42)
        icon_label.setAlignment(Qt.AlignCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        value_label = QLabel(value)
        value_label.setObjectName("statValue")

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()

        grid.addWidget(card, row, col)
        return value_label

    def create_report_card(self, grid, row, col, icon, title, description, report_type):
        card = QFrame()
        card.setObjectName("reportCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(140)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setObjectName("reportIcon")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("reportTitle")

        top_layout.addWidget(icon_label)
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        desc_label = QLabel(description)
        desc_label.setObjectName("reportDesc")
        desc_label.setWordWrap(True)

        btn = QPushButton(tr("view_report"))
        btn.setObjectName("reportBtn")
        btn.setFixedHeight(34)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setAttribute(Qt.WA_StyledBackground, True)
        btn.clicked.connect(lambda checked=False, rt=report_type: self.open_report(rt))

        layout.addLayout(top_layout)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(btn, alignment=Qt.AlignLeft)

        grid.addWidget(card, row, col)

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""

        QWidget#reportsWindow {{
            background-color: {c['bg_main']};
            font-family: Vazirmatn;
            color: {c['text_main']};
        }}

        QLabel#reportsTitle {{
            color: {c['text_main']};
            font-size: 20px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#reportsSubtitle {{
            color: {c['text_dim']};
            font-size: 11px;
            background: transparent;
        }}

        QPushButton#backButton {{
            background-color: {c['bg_card']};
            color: {c['accent']};
            border: 1px solid {c['border']};
            border-radius: 19px;
            font-size: 20px;
            font-weight: 600;
            padding: 0px;
        }}

        QPushButton#backButton:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['border_hover']};
        }}

        QFrame#filterBox {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}

        QLabel#filterLabel {{
            color: {c['text_main']};
            font-size: 13px;
            font-weight: 800;
            background: transparent;
            border: none;
        }}

        QScrollArea {{
            background: transparent;
            border: none;
        }}

        QScrollArea::viewport {{
            background: transparent;
        }}

        QWidget#scrollContent {{
            background: transparent;
        }}

        QLabel#sectionTitle {{
            color: {c['text_main']};
            font-size: 14px;
            font-weight: 700;
            background: transparent;
            padding: 4px 2px;
        }}

        QFrame#statBlue {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}

        QFrame#statGreen {{
            background-color: {c['success_bg']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}

        QLabel#statIcon {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border-radius: 12px;
            font-size: 18px;
            font-weight: 700;
        }}

        QLabel#statTitle {{
            color: {c['text_dim']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }}

        QLabel#statValue {{
            color: {c['accent']};
            font-size: 17px;
            font-weight: 800;
            background: transparent;
        }}

        QFrame#reportCard {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}

        QFrame#reportCard:hover {{
            border-color: {c['accent']};
            background-color: {c['bg_hover']};
        }}

        QLabel#reportIcon {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border-radius: 12px;
            font-size: 17px;
            font-weight: 700;
        }}

        QLabel#reportTitle {{
            color: {c['text_main']};
            font-size: 13px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#reportDesc {{
            color: {c['text_dim']};
            font-size: 11px;
            background: transparent;
        }}

        QPushButton#reportBtn {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border: none;
            border-radius: 17px;
            padding: 0 18px;
            font-size: 11px;
            font-weight: 700;
        }}

        QPushButton#reportBtn:hover {{
            background-color: {c['bg_hover']};
            color: {c['accent']};
        }}

        """)

    def calculate_reports(self):
        if not self.complex_id:
            return

        start_date, end_date = self.get_date_range_gregorian()

        try:
            emp = self.db.fetch_one(
                """
                SELECT COUNT(*) AS cnt FROM complex_members
                WHERE complexId = %s AND role IN ('employee', 'both') AND isActive = '1'
                """,
                (self.complex_id,)
            )
            emp_count = int(emp["cnt"]) if emp else 0

            hours_row = self.db.fetch_one(
                """
                SELECT COALESCE(SUM(a.workedMinutes), 0) AS total
                FROM attendance a
                INNER JOIN complex_members cm ON cm.memberId = a.memberId
                WHERE cm.complexId = %s
                  AND a.workDate BETWEEN %s AND %s
                  AND a.checkIn IS NOT NULL
                """,
                (self.complex_id, start_date, end_date)
            )
            total_minutes = int(hours_row["total"]) if hours_row else 0
            total_hours = total_minutes // 60

            pay_row = self.db.fetch_one(
                """
                SELECT COALESCE(SUM(p.amount), 0) AS total
                FROM payments p
                INNER JOIN complex_members cm ON cm.memberId = p.memberId
                WHERE cm.complexId = %s
                  AND DATE(p.paymentDate) BETWEEN %s AND %s
                """,
                (self.complex_id, start_date, end_date)
            )
            total_payments = float(pay_row["total"]) if pay_row else 0

            task_row = self.db.fetch_one(
                """
                SELECT COUNT(*) AS cnt
                FROM employee_jobs ej
                INNER JOIN complex_members cm ON cm.memberId = ej.memberId
                WHERE cm.complexId = %s
                  AND ej.status = 'completed'
                  AND DATE(ej.assignedDate) BETWEEN %s AND %s
                """,
                (self.complex_id, start_date, end_date)
            )
            tasks_done = int(task_row["cnt"]) if task_row else 0

            self.emp_value.setText(str(emp_count))
            self.hours_value.setText(f"{total_hours} {tr('hours_text')}")
            self.pay_value.setText(f"{format_money(total_payments)} {tr('toman')}")
            self.tasks_value.setText(str(tasks_done))

        except Exception as e:
            print("REPORTS CALC ERROR:", e)

    # =====================================================
    # DIALOG STYLESHEET
    # =====================================================

    def dialog_stylesheet(self):
        c = theme_manager.colors()
        return f"""
            QDialog {{
                background-color: {c['bg_main']};
                font-family: "Vazirmatn";
            }}

            QFrame#dialogHeader {{
                background-color: {c['bg_card']};
                border-bottom: 1px solid {c['border']};
            }}

            QFrame#dialogBottom {{
                background-color: {c['bg_card']};
                border-top: 1px solid {c['border']};
            }}

            QFrame#datePickerBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 18px;
            }}

            QLabel#dateFieldLabel {{
                color: {c['text_dim']};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
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

            QPushButton#applyDatesBtn {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 21px;
                padding: 0 24px;
                font-size: 13px;
                font-weight: 700;
                min-height: 42px;
            }}

            QPushButton#applyDatesBtn:hover {{
                background-color: {c['accent_hover']};
            }}

            QFrame#employeeStatCard {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 20px;
            }}

            QFrame#employeeStatCard:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid {c['accent']};
            }}

            QFrame#statBox {{
                border: none;
                border-radius: 14px;
            }}

            QFrame#detailRow {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 16px;
            }}

            QFrame#statusBadgeGreen {{
                background-color: {c['success_bg']};
                border: none;
                border-radius: 11px;
            }}

            QFrame#statusBadgeOrange {{
                background-color: #FFF4DD;
                border: none;
                border-radius: 11px;
            }}

            QFrame#statusBadgeRed {{
                background-color: #FFE5E8;
                border: none;
                border-radius: 11px;
            }}

            QFrame#summaryStatBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 16px;
            }}

            QFrame#summaryStatBoxGreen {{
                background-color: {c['success_bg']};
                border: 1px solid {c['border']};
                border-radius: 16px;
            }}

            QFrame#summaryStatBoxOrange {{
                background-color: #FFF4DD;
                border: 1px solid {c['border']};
                border-radius: 16px;
            }}

            QFrame#summaryStatBoxRed {{
                background-color: #FFE5E8;
                border: 1px solid {c['border']};
                border-radius: 16px;
            }}
        """

    # =====================================================
    # OPEN REPORT (با Date Picker برای همه)
    # =====================================================

    def open_report(self, report_type):
        if not self.complex_id:
            return

        initial_start, initial_end = self.get_date_range_gregorian()
        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumSize(800, 720)
        dialog.resize(940, 800)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        title_map = {
            "attendance": tr("report_attendance"),
            "finance": tr("report_finance"),
            "employees": tr("report_employees"),
            "tasks": tr("report_tasks"),
        }
        report_title = title_map.get(report_type, tr("reports_title"))
        dialog.setWindowTitle(report_title)

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ═══ Header ═══
        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setAttribute(Qt.WA_StyledBackground, True)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(28, 20, 28, 20)
        h_layout.setSpacing(4)

        h_title = QLabel(report_title)
        h_title.setAlignment(Qt.AlignCenter)
        h_title.setStyleSheet(
            f"color: {c['text_main']}; font-size: 20px; "
            f"font-weight: 800; background: transparent;"
        )

        h_layout.addWidget(h_title)
        main_layout.addWidget(header)

        # ═══ Date Picker Box (برای همه گزارش‌ها) ═══
        date_box = QFrame()
        date_box.setObjectName("datePickerBox")
        date_box.setAttribute(Qt.WA_StyledBackground, True)
        db_layout = QVBoxLayout(date_box)
        db_layout.setContentsMargins(20, 14, 20, 14)
        db_layout.setSpacing(10)

        db_title = QLabel("📅  انتخاب بازه زمانی")
        db_title.setAlignment(Qt.AlignRight)
        db_title.setStyleSheet(
            f"color: {c['text_main']}; font-size: 13px; "
            f"font-weight: 800; background: transparent;"
        )
        db_layout.addWidget(db_title)

        picker_row = QHBoxLayout()
        picker_row.setSpacing(12)

        # از
        start_col = QVBoxLayout()
        start_col.setSpacing(4)
        start_lbl = QLabel("از تاریخ")
        start_lbl.setObjectName("dateFieldLabel")
        start_picker = PersianDateButton(
            initial_qdate=QDate(initial_start.year, initial_start.month, initial_start.day)
        )
        start_col.addWidget(start_lbl)
        start_col.addWidget(start_picker)
        picker_row.addLayout(start_col, 2)

        # تا
        end_col = QVBoxLayout()
        end_col.setSpacing(4)
        end_lbl = QLabel("تا تاریخ")
        end_lbl.setObjectName("dateFieldLabel")
        end_picker = PersianDateButton(
            initial_qdate=QDate(initial_end.year, initial_end.month, initial_end.day)
        )
        end_col.addWidget(end_lbl)
        end_col.addWidget(end_picker)
        picker_row.addLayout(end_col, 2)

        # اعمال
        apply_btn = QPushButton("اعمال")
        apply_btn.setObjectName("applyDatesBtn")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setFixedHeight(42)
        picker_row.addWidget(apply_btn, 1, Qt.AlignBottom)

        db_layout.addLayout(picker_row)

        # فاصله
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        wrap_layout = QVBoxLayout(wrap)
        wrap_layout.setContentsMargins(20, 12, 20, 0)
        wrap_layout.setSpacing(0)
        wrap_layout.addWidget(date_box)
        main_layout.addWidget(wrap)

        # ═══ Scroll ═══
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        bar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(bar)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_main']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)

        main_layout.addWidget(scroll, 1)

        # ═══ refresh function ═══
        def refresh_content():
            while content_layout.count():
                item = content_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

            sd = start_picker.to_python_date()
            ed = end_picker.to_python_date()

            # محدوده نمایش داده بشه
            range_lbl = QLabel(f"از {persian_date_short(sd)} تا {persian_date_short(ed)}")
            range_lbl.setAlignment(Qt.AlignCenter)
            range_lbl.setStyleSheet(
                f"color: {c['accent']}; font-size: 12px; "
                f"font-weight: 700; background: transparent; padding: 4px;"
            )
            content_layout.addWidget(range_lbl)
            content_layout.addSpacing(4)

            if report_type == "attendance":
                self.build_attendance_report(content_layout, sd, ed)
            elif report_type == "finance":
                self.build_finance_report(content_layout, sd, ed)
            elif report_type == "employees":
                self.build_employees_report(content_layout)
            elif report_type == "tasks":
                self.build_tasks_report(content_layout, sd, ed)

            content_layout.addStretch()

        apply_btn.clicked.connect(refresh_content)

        # initial build
        refresh_content()
        scroll.setWidget(content)

        # ═══ Bottom ═══
        bottom = QFrame()
        bottom.setObjectName("dialogBottom")
        bottom.setAttribute(Qt.WA_StyledBackground, True)
        b_layout = QHBoxLayout(bottom)
        b_layout.setContentsMargins(20, 12, 20, 12)

        close_btn = QPushButton(tr("close"))
        close_btn.setFixedHeight(44)
        close_btn.setMinimumWidth(150)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 28px;
            }}
            QPushButton:hover {{
                background-color: {c['accent_hover']};
            }}
        """)
        close_btn.clicked.connect(dialog.accept)

        b_layout.addStretch()
        b_layout.addWidget(close_btn)
        b_layout.addStretch()
        main_layout.addWidget(bottom)

        dialog.setStyleSheet(self.dialog_stylesheet())
        dialog.exec()

    # =====================================================
    # BUILD ATTENDANCE REPORT
    # =====================================================

    def build_attendance_report(self, layout, start_date, end_date):
        c = theme_manager.colors()

        try:
            employees = self.db.fetch_all(
                """
                SELECT cm.memberId, u.name, u.phoneNumber
                FROM complex_members cm
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                  AND cm.role IN ('employee', 'both')
                  AND cm.isActive = '1'
                ORDER BY u.name ASC
                """,
                (self.complex_id,)
            )
        except Exception as e:
            print("BUILD ATTENDANCE REPORT ERROR:", e)
            employees = []

        if not employees:
            empty = QLabel("کارمندی یافت نشد.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 13px; "
                f"padding: 40px; background: transparent;"
            )
            layout.addWidget(empty)
            return

        hint = QLabel("💡 برای دیدن تاریخچه کامل هر کارمند، روی کارت او کلیک کنید.")
        hint.setAlignment(Qt.AlignRight)
        hint.setStyleSheet(
            f"color: {c['text_dim']}; font-size: 11px; "
            f"padding: 4px 4px; background: transparent;"
        )
        layout.addWidget(hint)

        for emp in employees:
            try:
                stats = self.db.fetch_one(
                    """
                    SELECT
                        COUNT(DISTINCT CASE WHEN status = 'absent' THEN workDate END) AS absent_days,
                        COUNT(DISTINCT CASE WHEN checkIn IS NOT NULL THEN workDate END) AS present_days,
                        COALESCE(SUM(CASE WHEN checkIn IS NOT NULL THEN workedMinutes ELSE 0 END), 0) AS minutes,
                        COALESCE(SUM(CASE WHEN checkIn IS NOT NULL THEN overtimeMinutes ELSE 0 END), 0) AS ot
                    FROM attendance
                    WHERE memberId = %s
                      AND workDate BETWEEN %s AND %s
                    """,
                    (emp["memberId"], start_date, end_date)
                )
            except Exception as e:
                print("EMP ATT STATS ERROR:", e)
                stats = None

            present_days = int(stats["present_days"] or 0) if stats else 0
            absent_days = int(stats["absent_days"] or 0) if stats else 0
            minutes = int(stats["minutes"] or 0) if stats else 0
            ot = int(stats["ot"] or 0) if stats else 0

            h = minutes // 60
            m = minutes % 60
            ot_h = ot // 60
            ot_m = ot % 60

            card = QFrame()
            card.setObjectName("employeeStatCard")
            card.setAttribute(Qt.WA_StyledBackground, True)
            card.setCursor(Qt.PointingHandCursor)
            card.setMinimumHeight(96)

            cl = QHBoxLayout(card)
            cl.setContentsMargins(18, 14, 18, 14)
            cl.setSpacing(16)

            name_text = emp.get("name") or "—"
            initial = name_text.strip()[0] if name_text.strip() else "?"

            avatar = QLabel(initial)
            avatar.setFixedSize(48, 48)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setStyleSheet(
                f"background-color: {c['accent_light']}; "
                f"color: {c['accent']}; "
                f"border-radius: 24px; "
                f"font-size: 18px; font-weight: 800;"
            )

            info_col = QVBoxLayout()
            info_col.setSpacing(3)

            name_lbl = QLabel(name_text)
            name_lbl.setStyleSheet(
                f"color: {c['text_main']}; font-size: 14px; "
                f"font-weight: 700; background: transparent;"
            )

            phone_lbl = QLabel(emp.get("phoneNumber") or "—")
            phone_lbl.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 11px; "
                f"background: transparent;"
            )

            info_col.addWidget(name_lbl)
            info_col.addWidget(phone_lbl)

            stats_col = QHBoxLayout()
            stats_col.setSpacing(10)

            stats_col.addWidget(create_stat_box(
                "روز حاضر", str(present_days), "green", 90
            ))
            stats_col.addWidget(create_stat_box(
                "روز غایب", str(absent_days), "red" if absent_days > 0 else "blue", 90
            ))
            stats_col.addWidget(create_stat_box(
                "ساعت کار", f"{h}س {m}د", "blue", 110
            ))
            stats_col.addWidget(create_stat_box(
                "اضافه کاری",
                f"{ot_h}س {ot_m}د" if ot > 0 else "ندارد",
                "orange" if ot > 0 else "blue",
                110
            ))

            cl.addWidget(avatar)
            cl.addLayout(info_col, 2)
            cl.addLayout(stats_col, 6)

            card.mousePressEvent = (
                lambda event, e=emp: self.open_employee_attendance_detail(
                    e, start_date, end_date
                )
            )

            layout.addWidget(card)

    # =====================================================
    # EMPLOYEE ATTENDANCE DETAIL
    # =====================================================

    def open_employee_attendance_detail(self, employee, start_date, end_date):
        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumSize(820, 700)
        dialog.resize(960, 760)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        name_text = employee.get("name") or "—"
        dialog.setWindowTitle(f"تاریخچه حضور — {name_text}")

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setAttribute(Qt.WA_StyledBackground, True)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(28, 20, 28, 20)
        h_layout.setSpacing(4)

        h_name = QLabel(name_text)
        h_name.setAlignment(Qt.AlignCenter)
        h_name.setStyleSheet(
            f"color: {c['text_main']}; font-size: 20px; "
            f"font-weight: 800; background: transparent;"
        )

        h_phone = QLabel(employee.get("phoneNumber") or "—")
        h_phone.setAlignment(Qt.AlignCenter)
        h_phone.setStyleSheet(
            f"color: {c['text_dim']}; font-size: 12px; "
            f"font-weight: 600; background: transparent;"
        )

        range_text = f"از {persian_date_short(start_date)} تا {persian_date_short(end_date)}"
        h_range = QLabel(range_text)
        h_range.setAlignment(Qt.AlignCenter)
        h_range.setStyleSheet(
            f"color: {c['accent']}; font-size: 12px; "
            f"font-weight: 700; background: transparent;"
        )

        h_layout.addWidget(h_name)
        h_layout.addWidget(h_phone)
        h_layout.addWidget(h_range)
        main_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        bar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(bar)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_main']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)

        try:
            records = self.db.fetch_all(
                """
                SELECT workDate, checkIn, checkOut, workedMinutes,
                       overtimeMinutes, approvalStatus, status
                FROM attendance
                WHERE memberId = %s
                  AND workDate BETWEEN %s AND %s
                ORDER BY workDate DESC
                """,
                (employee["memberId"], start_date, end_date)
            )
        except Exception as e:
            print("EMP ATT DETAIL ERROR:", e)
            records = []

        if not records:
            empty = QLabel("رکوردی در این بازه یافت نشد.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 13px; "
                f"padding: 60px; background: transparent;"
            )
            content_layout.addWidget(empty)
            content_layout.addStretch()
        else:
            present_count = 0
            absent_count = 0
            total_minutes = 0
            total_ot = 0

            for r in records:
                if r.get("status") == "absent":
                    absent_count += 1
                elif r.get("checkIn"):
                    present_count += 1
                    total_minutes += int(r.get("workedMinutes") or 0)
                    total_ot += int(r.get("overtimeMinutes") or 0)

            h = total_minutes // 60
            m = total_minutes % 60
            ot_h = total_ot // 60
            ot_m = total_ot % 60

            summary_box = QFrame()
            summary_box.setObjectName("summaryStatBox")
            summary_box.setAttribute(Qt.WA_StyledBackground, True)
            sl = QHBoxLayout(summary_box)
            sl.setContentsMargins(16, 14, 16, 14)
            sl.setSpacing(12)

            sl.addWidget(create_stat_box("روز حاضر", str(present_count), "green", 110))
            sl.addWidget(create_stat_box("روز غایب", str(absent_count), "red" if absent_count > 0 else "blue", 110))
            sl.addWidget(create_stat_box("کل ساعت کار", f"{h}س {m}د", "blue", 140))
            sl.addWidget(create_stat_box("کل اضافه کاری", f"{ot_h}س {ot_m}د", "orange" if total_ot > 0 else "blue", 140))

            content_layout.addWidget(summary_box)
            content_layout.addSpacing(6)

            for r in records:
                is_absent = (r.get("status") == "absent")

                card = QFrame()
                card.setObjectName("detailRow")
                card.setAttribute(Qt.WA_StyledBackground, True)
                card.setMinimumHeight(76)

                rl = QHBoxLayout(card)
                rl.setContentsMargins(16, 12, 16, 12)
                rl.setSpacing(10)

                wd = r.get("workDate")
                if isinstance(wd, (date, datetime)):
                    date_str = persian_date_long(wd)
                else:
                    date_str = str(wd) if wd else "—"

                date_lbl = QLabel(date_str)
                date_lbl.setStyleSheet(
                    f"color: {c['text_main']}; font-size: 12px; "
                    f"font-weight: 700; background: transparent;"
                )
                date_lbl.setMinimumWidth(200)

                if is_absent:
                    in_lbl = QLabel("—")
                    in_lbl.setStyleSheet(
                        f"color: {c['text_dim']}; font-size: 11px; "
                        f"background: transparent;"
                    )
                    in_lbl.setMinimumWidth(140)

                    out_lbl = QLabel("—")
                    out_lbl.setStyleSheet(
                        f"color: {c['text_dim']}; font-size: 11px; "
                        f"background: transparent;"
                    )
                    out_lbl.setMinimumWidth(140)

                    hours_lbl = QLabel("—")
                    hours_lbl.setStyleSheet(
                        f"color: {c['text_dim']}; font-size: 12px; "
                        f"background: transparent;"
                    )
                    hours_lbl.setMinimumWidth(70)

                    ot_lbl = QLabel("—")
                    ot_lbl.setStyleSheet(
                        f"color: {c['text_dim']}; font-size: 11px; "
                        f"background: transparent;"
                    )

                    rl.addWidget(date_lbl, 2)
                    rl.addWidget(in_lbl, 1)
                    rl.addWidget(out_lbl, 1)
                    rl.addWidget(hours_lbl, 1)
                    rl.addWidget(ot_lbl, 1)
                    rl.addStretch()
                else:
                    ci_text = format_time_12h(r.get("checkIn")) if r.get("checkIn") else "—"
                    co_text = format_time_12h(r.get("checkOut")) if r.get("checkOut") else "—"

                    in_lbl = QLabel(f"ورود: {ci_text}")
                    in_lbl.setStyleSheet(
                        f"color: {c['text_dim']}; font-size: 11px; "
                        f"background: transparent;"
                    )
                    in_lbl.setMinimumWidth(140)

                    out_lbl = QLabel(f"خروج: {co_text}")
                    out_lbl.setStyleSheet(
                        f"color: {c['text_dim']}; font-size: 11px; "
                        f"background: transparent;"
                    )
                    out_lbl.setMinimumWidth(140)

                    wm = int(r.get("workedMinutes") or 0)
                    wh, wmin = wm // 60, wm % 60

                    hours_lbl = QLabel(f"{wh}س {wmin}د")
                    hours_lbl.setStyleSheet(
                        f"color: {c['accent']}; font-size: 12px; "
                        f"font-weight: 700; background: transparent;"
                    )
                    hours_lbl.setMinimumWidth(70)

                    ot_val = int(r.get("overtimeMinutes") or 0)
                    if ot_val > 0:
                        ot_h2, ot_m2 = ot_val // 60, ot_val % 60
                        ot_lbl = QLabel(f"OT {ot_h2}س {ot_m2}د")
                        ot_lbl.setStyleSheet(
                            f"color: #B87900; font-size: 11px; "
                            f"font-weight: 700; background: transparent;"
                        )
                    else:
                        ot_lbl = QLabel("—")
                        ot_lbl.setStyleSheet(
                            f"color: {c['text_dim']}; font-size: 11px; "
                            f"background: transparent;"
                        )

                    appr = r.get("approvalStatus") or "pending"
                    if appr == "approved":
                        status_text = "تایید"
                        badge_name = "statusBadgeGreen"
                        status_color = c['success']
                    elif appr == "rejected":
                        status_text = "رد"
                        badge_name = "statusBadgeRed"
                        status_color = "#D93025"
                    else:
                        status_text = "در انتظار"
                        badge_name = "statusBadgeOrange"
                        status_color = "#B87900"

                    badge = QFrame()
                    badge.setObjectName(badge_name)
                    badge.setAttribute(Qt.WA_StyledBackground, True)
                    badge.setFixedSize(84, 26)
                    bl = QHBoxLayout(badge)
                    bl.setContentsMargins(0, 0, 0, 0)
                    bl.setAlignment(Qt.AlignCenter)
                    blbl = QLabel(status_text)
                    blbl.setStyleSheet(
                        f"color: {status_color}; font-size: 10px; "
                        f"font-weight: 700; background: transparent;"
                    )
                    bl.addWidget(blbl)

                    rl.addWidget(date_lbl, 2)
                    rl.addWidget(in_lbl, 1)
                    rl.addWidget(out_lbl, 1)
                    rl.addWidget(hours_lbl, 1)
                    rl.addWidget(ot_lbl, 1)
                    rl.addStretch()
                    rl.addWidget(badge)

                content_layout.addWidget(card)

            content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        bottom = QFrame()
        bottom.setObjectName("dialogBottom")
        bottom.setAttribute(Qt.WA_StyledBackground, True)
        bl2 = QHBoxLayout(bottom)
        bl2.setContentsMargins(20, 12, 20, 12)

        close_btn = QPushButton(tr("close"))
        close_btn.setFixedHeight(44)
        close_btn.setMinimumWidth(150)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 28px;
            }}
            QPushButton:hover {{
                background-color: {c['accent_hover']};
            }}
        """)
        close_btn.clicked.connect(dialog.accept)

        bl2.addStretch()
        bl2.addWidget(close_btn)
        bl2.addStretch()
        main_layout.addWidget(bottom)

        dialog.setStyleSheet(self.dialog_stylesheet())
        dialog.exec()

    # =====================================================
    # BUILD FINANCE REPORT
    # =====================================================

    def build_finance_report(self, layout, start_date, end_date):
        c = theme_manager.colors()

        try:
            employees = self.db.fetch_all(
                """
                SELECT cm.memberId, u.name, u.phoneNumber
                FROM complex_members cm
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                  AND cm.role IN ('employee', 'both')
                  AND cm.isActive = '1'
                ORDER BY u.name ASC
                """,
                (self.complex_id,)
            )
        except Exception as e:
            print("BUILD FINANCE REPORT ERROR:", e)
            employees = []

        if not employees:
            empty = QLabel("کارمندی یافت نشد.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 13px; "
                f"padding: 40px; background: transparent;"
            )
            layout.addWidget(empty)
            return

        hint = QLabel("💡 برای دیدن تاریخچه مالی کامل هر کارمند، روی کارت او کلیک کنید.")
        hint.setAlignment(Qt.AlignRight)
        hint.setStyleSheet(
            f"color: {c['text_dim']}; font-size: 11px; "
            f"padding: 4px 4px; background: transparent;"
        )
        layout.addWidget(hint)

        for emp in employees:
            try:
                stats = self.db.fetch_one(
                    """
                    SELECT COUNT(*) AS cnt,
                           COALESCE(SUM(amount), 0) AS total
                    FROM payments
                    WHERE memberId = %s
                      AND DATE(paymentDate) BETWEEN %s AND %s
                    """,
                    (emp["memberId"], start_date, end_date)
                )
            except Exception as e:
                print("EMP FIN STATS ERROR:", e)
                stats = None

            count = int(stats["cnt"] or 0) if stats else 0
            total = float(stats["total"] or 0) if stats else 0

            card = QFrame()
            card.setObjectName("employeeStatCard")
            card.setAttribute(Qt.WA_StyledBackground, True)
            card.setCursor(Qt.PointingHandCursor)
            card.setMinimumHeight(96)

            cl = QHBoxLayout(card)
            cl.setContentsMargins(18, 14, 18, 14)
            cl.setSpacing(16)

            name_text = emp.get("name") or "—"
            initial = name_text.strip()[0] if name_text.strip() else "?"

            avatar = QLabel(initial)
            avatar.setFixedSize(48, 48)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setStyleSheet(
                f"background-color: {c['accent_light']}; "
                f"color: {c['accent']}; "
                f"border-radius: 24px; "
                f"font-size: 18px; font-weight: 800;"
            )

            info_col = QVBoxLayout()
            info_col.setSpacing(3)

            name_lbl = QLabel(name_text)
            name_lbl.setStyleSheet(
                f"color: {c['text_main']}; font-size: 14px; "
                f"font-weight: 700; background: transparent;"
            )

            phone_lbl = QLabel(emp.get("phoneNumber") or "—")
            phone_lbl.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 11px; "
                f"background: transparent;"
            )

            info_col.addWidget(name_lbl)
            info_col.addWidget(phone_lbl)

            stats_col = QHBoxLayout()
            stats_col.setSpacing(10)

            stats_col.addWidget(create_stat_box("تعداد پرداخت", str(count), "blue", 120))
            stats_col.addWidget(create_stat_box(
                "جمع پرداخت",
                f"{format_money(total)} ت",
                "green",
                160
            ))

            cl.addWidget(avatar)
            cl.addLayout(info_col, 2)
            cl.addLayout(stats_col, 5)

            card.mousePressEvent = (
                lambda event, e=emp: self.open_employee_finance_detail(
                    e, start_date, end_date
                )
            )

            layout.addWidget(card)

    # =====================================================
    # EMPLOYEE FINANCE DETAIL
    # =====================================================

    def open_employee_finance_detail(self, employee, start_date, end_date):
        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumSize(820, 700)
        dialog.resize(960, 760)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        name_text = employee.get("name") or "—"
        dialog.setWindowTitle(f"تاریخچه مالی — {name_text}")

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setAttribute(Qt.WA_StyledBackground, True)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(28, 20, 28, 20)
        h_layout.setSpacing(4)

        h_name = QLabel(name_text)
        h_name.setAlignment(Qt.AlignCenter)
        h_name.setStyleSheet(
            f"color: {c['text_main']}; font-size: 20px; "
            f"font-weight: 800; background: transparent;"
        )

        h_phone = QLabel(employee.get("phoneNumber") or "—")
        h_phone.setAlignment(Qt.AlignCenter)
        h_phone.setStyleSheet(
            f"color: {c['text_dim']}; font-size: 12px; "
            f"font-weight: 600; background: transparent;"
        )

        range_text = f"از {persian_date_short(start_date)} تا {persian_date_short(end_date)}"
        h_range = QLabel(range_text)
        h_range.setAlignment(Qt.AlignCenter)
        h_range.setStyleSheet(
            f"color: {c['accent']}; font-size: 12px; "
            f"font-weight: 700; background: transparent;"
        )

        h_layout.addWidget(h_name)
        h_layout.addWidget(h_phone)
        h_layout.addWidget(h_range)
        main_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        bar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(bar)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_main']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)

        try:
            records = self.db.fetch_all(
                """
                SELECT paymentType, amount, paymentDate, description
                FROM payments
                WHERE memberId = %s
                  AND DATE(paymentDate) BETWEEN %s AND %s
                ORDER BY paymentDate DESC
                """,
                (employee["memberId"], start_date, end_date)
            )
        except Exception as e:
            print("EMP FIN DETAIL ERROR:", e)
            records = []

        if not records:
            empty = QLabel("رکوردی در این بازه یافت نشد.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 13px; "
                f"padding: 60px; background: transparent;"
            )
            content_layout.addWidget(empty)
            content_layout.addStretch()
        else:
            total_amount = sum(float(r.get("amount") or 0) for r in records)

            summary_box = QFrame()
            summary_box.setObjectName("summaryStatBox")
            summary_box.setAttribute(Qt.WA_StyledBackground, True)
            sl = QHBoxLayout(summary_box)
            sl.setContentsMargins(16, 14, 16, 14)
            sl.setSpacing(12)

            sl.addWidget(create_stat_box("تعداد پرداخت", str(len(records)), "blue", 140))
            sl.addWidget(create_stat_box(
                "جمع کل",
                f"{format_money(total_amount)} تومان",
                "green",
                220
            ))
            content_layout.addWidget(summary_box)
            content_layout.addSpacing(6)

            type_map = {
                "salary": tr("payment_salary"),
                "job": tr("payment_job"),
                "bonus": tr("payment_bonus"),
                "advance": tr("payment_advance"),
                "other": tr("payment_other"),
            }

            for r in records:
                card = QFrame()
                card.setObjectName("detailRow")
                card.setAttribute(Qt.WA_StyledBackground, True)
                card.setMinimumHeight(76)

                rl = QHBoxLayout(card)
                rl.setContentsMargins(16, 12, 16, 12)
                rl.setSpacing(10)

                pd = r.get("paymentDate")
                if isinstance(pd, datetime):
                    date_str = persian_date_long(pd)
                    time_str = format_time_12h(pd)
                elif isinstance(pd, date):
                    date_str = persian_date_long(pd)
                    time_str = ""
                else:
                    date_str = str(pd) if pd else "—"
                    time_str = ""

                date_lbl = QLabel(date_str)
                date_lbl.setStyleSheet(
                    f"color: {c['text_main']}; font-size: 12px; "
                    f"font-weight: 700; background: transparent;"
                )
                date_lbl.setMinimumWidth(200)

                time_lbl = QLabel(time_str if time_str else "—")
                time_lbl.setStyleSheet(
                    f"color: {c['text_dim']}; font-size: 11px; "
                    f"background: transparent;"
                )
                time_lbl.setMinimumWidth(110)

                type_text = type_map.get(r.get("paymentType"), "—")
                type_lbl = QLabel(type_text)
                type_lbl.setStyleSheet(
                    f"color: {c['accent']}; font-size: 11px; "
                    f"font-weight: 700; background: transparent;"
                )
                type_lbl.setMinimumWidth(90)

                amount_lbl = QLabel(f"{format_money(r.get('amount') or 0)} تومان")
                amount_lbl.setStyleSheet(
                    f"color: {c['success']}; font-size: 13px; "
                    f"font-weight: 800; background: transparent;"
                )

                rl.addWidget(date_lbl, 2)
                rl.addWidget(time_lbl, 1)
                rl.addWidget(type_lbl, 1)
                rl.addStretch()
                rl.addWidget(amount_lbl)

                content_layout.addWidget(card)

            content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        bottom = QFrame()
        bottom.setObjectName("dialogBottom")
        bottom.setAttribute(Qt.WA_StyledBackground, True)
        bl2 = QHBoxLayout(bottom)
        bl2.setContentsMargins(20, 12, 20, 12)

        close_btn = QPushButton(tr("close"))
        close_btn.setFixedHeight(44)
        close_btn.setMinimumWidth(150)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 28px;
            }}
            QPushButton:hover {{
                background-color: {c['accent_hover']};
            }}
        """)
        close_btn.clicked.connect(dialog.accept)

        bl2.addStretch()
        bl2.addWidget(close_btn)
        bl2.addStretch()
        main_layout.addWidget(bottom)

        dialog.setStyleSheet(self.dialog_stylesheet())
        dialog.exec()

    # =====================================================
    # BUILD EMPLOYEES REPORT
    # =====================================================

    def build_employees_report(self, layout):
        c = theme_manager.colors()

        try:
            employees = self.db.fetch_all(
                """
                SELECT u.name, u.phoneNumber, cm.role,
                       ep.jobTitle, ep.employmentType, ep.salaryType,
                       ep.baseSalary, ep.workDays, ep.workHours,
                       ep.workStartTime, ep.workEndTime
                FROM complex_members cm
                INNER JOIN users u ON u.userId = cm.userId
                LEFT JOIN employee_profiles ep ON ep.memberId = cm.memberId
                WHERE cm.complexId = %s
                  AND cm.role IN ('employee', 'both')
                  AND cm.isActive = '1'
                ORDER BY u.name ASC
                """,
                (self.complex_id,)
            )
        except Exception as e:
            print("BUILD EMPLOYEES REPORT ERROR:", e)
            employees = []

        if not employees:
            empty = QLabel("کارمندی یافت نشد.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 13px; "
                f"padding: 40px; background: transparent;"
            )
            layout.addWidget(empty)
            return

        for emp in employees:
            card = QFrame()
            card.setObjectName("detailRow")
            card.setAttribute(Qt.WA_StyledBackground, True)
            card.setMinimumHeight(110)

            rl = QHBoxLayout(card)
            rl.setContentsMargins(18, 14, 18, 14)
            rl.setSpacing(16)

            name_text = emp.get("name") or "—"
            initial = name_text.strip()[0] if name_text.strip() else "?"

            avatar = QLabel(initial)
            avatar.setFixedSize(48, 48)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setStyleSheet(
                f"background-color: {c['accent_light']}; "
                f"color: {c['accent']}; "
                f"border-radius: 24px; "
                f"font-size: 18px; font-weight: 800;"
            )

            info_col = QVBoxLayout()
            info_col.setSpacing(3)

            name_lbl = QLabel(name_text)
            name_lbl.setStyleSheet(
                f"color: {c['text_main']}; font-size: 14px; "
                f"font-weight: 700; background: transparent;"
            )

            phone_lbl = QLabel(emp.get("phoneNumber") or "—")
            phone_lbl.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 11px; "
                f"background: transparent;"
            )

            job_lbl = QLabel(emp.get("jobTitle") or "—")
            job_lbl.setStyleSheet(
                f"color: {c['accent']}; font-size: 11px; "
                f"font-weight: 700; background: transparent;"
            )

            info_col.addWidget(name_lbl)
            info_col.addWidget(phone_lbl)
            info_col.addWidget(job_lbl)

            stats_col = QHBoxLayout()
            stats_col.setSpacing(10)

            base = float(emp.get("baseSalary") or 0)
            days = float(emp.get("workDays") or 26)
            hours = float(emp.get("workHours") or 8)

            stats_col.addWidget(create_stat_box(
                "حقوق پایه", f"{format_money(base)}", "green", 140
            ))
            stats_col.addWidget(create_stat_box(
                "روز کارکرد", f"{days:g} روز", "blue", 110
            ))
            stats_col.addWidget(create_stat_box(
                "ساعت روزانه", f"{hours:g} ساعت", "blue", 110
            ))

            rl.addWidget(avatar)
            rl.addLayout(info_col, 2)
            rl.addLayout(stats_col, 5)

            layout.addWidget(card)

    # =====================================================
    # BUILD TASKS REPORT
    # =====================================================

    def build_tasks_report(self, layout, start_date, end_date):
        c = theme_manager.colors()

        try:
            stats = self.db.fetch_one(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN ej.status = 'pending' THEN 1 ELSE 0 END) AS pending,
                    SUM(CASE WHEN ej.status = 'inProgress' THEN 1 ELSE 0 END) AS in_progress,
                    SUM(CASE WHEN ej.status = 'completed' THEN 1 ELSE 0 END) AS completed,
                    SUM(CASE WHEN ej.status = 'rejected' THEN 1 ELSE 0 END) AS rejected,
                    SUM(CASE WHEN ej.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
                    COALESCE(SUM(CASE WHEN ej.status = 'completed' THEN ej.price ELSE 0 END), 0) AS total_paid
                FROM employee_jobs ej
                INNER JOIN complex_members cm ON cm.memberId = ej.memberId
                WHERE cm.complexId = %s
                  AND DATE(ej.assignedDate) BETWEEN %s AND %s
                """,
                (self.complex_id, start_date, end_date)
            )
        except Exception as e:
            print("TASKS STATS ERROR:", e)
            stats = None

        total = int(stats["total"] or 0) if stats else 0
        pending = int(stats["pending"] or 0) if stats else 0
        in_progress = int(stats["in_progress"] or 0) if stats else 0
        completed = int(stats["completed"] or 0) if stats else 0
        rejected = int(stats["rejected"] or 0) if stats else 0
        cancelled = int(stats["cancelled"] or 0) if stats else 0
        total_paid = float(stats["total_paid"] or 0) if stats else 0

        summary_grid = QGridLayout()
        summary_grid.setSpacing(10)

        summary_grid.addWidget(
            self._create_summary_stat("کل کارها", str(total), "summaryStatBox"),
            0, 0
        )
        summary_grid.addWidget(
            self._create_summary_stat("در انتظار", str(pending), "summaryStatBoxOrange"),
            0, 1
        )
        summary_grid.addWidget(
            self._create_summary_stat("در حال انجام", str(in_progress), "summaryStatBoxOrange"),
            0, 2
        )
        summary_grid.addWidget(
            self._create_summary_stat("تکمیل شده", str(completed), "summaryStatBoxGreen"),
            0, 3
        )
        summary_grid.addWidget(
            self._create_summary_stat("رد شده", str(rejected), "summaryStatBoxRed"),
            1, 0
        )
        summary_grid.addWidget(
            self._create_summary_stat("لغو شده", str(cancelled), "summaryStatBox"),
            1, 1
        )
        summary_grid.addWidget(
            self._create_summary_stat(
                "جمع پرداخت‌شده",
                f"{format_money(total_paid)} ت",
                "summaryStatBoxGreen"
            ),
            1, 2, 1, 2
        )

        layout.addLayout(summary_grid)
        layout.addSpacing(10)

        section = QLabel("عملکرد کارمندان")
        section.setStyleSheet(
            f"color: {c['text_main']}; font-size: 13px; "
            f"font-weight: 700; background: transparent; padding: 4px;"
        )
        layout.addWidget(section)

        try:
            per_emp = self.db.fetch_all(
                """
                SELECT u.name,
                       COUNT(ej.employeeJobId) AS total,
                       SUM(CASE WHEN ej.status = 'completed' THEN 1 ELSE 0 END) AS done,
                       SUM(CASE WHEN ej.status = 'inProgress' THEN 1 ELSE 0 END) AS in_prog,
                       COALESCE(SUM(CASE WHEN ej.status = 'completed' THEN ej.price ELSE 0 END), 0) AS earned
                FROM employee_jobs ej
                INNER JOIN complex_members cm ON cm.memberId = ej.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                  AND DATE(ej.assignedDate) BETWEEN %s AND %s
                GROUP BY u.userId, u.name
                ORDER BY done DESC, u.name ASC
                """,
                (self.complex_id, start_date, end_date)
            )
        except Exception as e:
            print("PER EMP TASKS ERROR:", e)
            per_emp = []

        if per_emp:
            for emp in per_emp:
                card = QFrame()
                card.setObjectName("detailRow")
                card.setAttribute(Qt.WA_StyledBackground, True)
                card.setMinimumHeight(84)

                rl = QHBoxLayout(card)
                rl.setContentsMargins(18, 12, 18, 12)
                rl.setSpacing(14)

                name_text = emp.get("name") or "—"
                initial = name_text.strip()[0] if name_text.strip() else "?"

                avatar = QLabel(initial)
                avatar.setFixedSize(44, 44)
                avatar.setAlignment(Qt.AlignCenter)
                avatar.setStyleSheet(
                    f"background-color: {c['accent_light']}; "
                    f"color: {c['accent']}; "
                    f"border-radius: 22px; "
                    f"font-size: 16px; font-weight: 800;"
                )

                name_lbl = QLabel(name_text)
                name_lbl.setStyleSheet(
                    f"color: {c['text_main']}; font-size: 13px; "
                    f"font-weight: 700; background: transparent;"
                )
                name_lbl.setMinimumWidth(160)

                tot = int(emp.get("total") or 0)
                done = int(emp.get("done") or 0)
                in_prog = int(emp.get("in_prog") or 0)
                earned = float(emp.get("earned") or 0)

                stats_col = QHBoxLayout()
                stats_col.setSpacing(10)

                stats_col.addWidget(create_stat_box("کل", str(tot), "blue", 90))
                stats_col.addWidget(create_stat_box("تکمیل", str(done), "green", 90))
                stats_col.addWidget(create_stat_box("در حال انجام", str(in_prog), "orange", 100))
                stats_col.addWidget(create_stat_box("درآمد", f"{format_money(earned)}", "green", 150))

                rl.addWidget(avatar)
                rl.addWidget(name_lbl, 2)
                rl.addLayout(stats_col, 6)

                layout.addWidget(card)

        layout.addSpacing(10)

        detail_section = QLabel("جزئیات کارها (با تاریخ)")
        detail_section.setStyleSheet(
            f"color: {c['text_main']}; font-size: 13px; "
            f"font-weight: 700; background: transparent; padding: 4px;"
        )
        layout.addWidget(detail_section)

        try:
            tasks = self.db.fetch_all(
                """
                SELECT u.name, j.jobTitle, ej.status, ej.price,
                       ej.assignedDate, ej.completedDate, ej.description
                FROM employee_jobs ej
                INNER JOIN complex_members cm ON cm.memberId = ej.memberId
                INNER JOIN users u ON u.userId = cm.userId
                LEFT JOIN jobs j ON j.jobId = ej.jobId
                WHERE cm.complexId = %s
                  AND DATE(ej.assignedDate) BETWEEN %s AND %s
                ORDER BY ej.assignedDate DESC
                LIMIT 200
                """,
                (self.complex_id, start_date, end_date)
            )
        except Exception as e:
            print("TASKS DETAIL ERROR:", e)
            tasks = []

        if not tasks:
            empty = QLabel("کاری یافت نشد.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 12px; "
                f"padding: 30px; background: transparent;"
            )
            layout.addWidget(empty)
            return

        status_map = {
            "pending": ("در انتظار", "statusBadgeOrange", "#B87900"),
            "inProgress": ("در حال انجام", "statusBadgeOrange", "#B87900"),
            "completed": ("تکمیل", "statusBadgeGreen", c['success']),
            "rejected": ("رد شده", "statusBadgeRed", "#D93025"),
            "cancelled": ("لغو شده", "statusBadgeRed", "#D93025"),
        }

        for t in tasks:
            card = QFrame()
            card.setObjectName("detailRow")
            card.setAttribute(Qt.WA_StyledBackground, True)
            card.setMinimumHeight(72)

            rl = QHBoxLayout(card)
            rl.setContentsMargins(16, 12, 16, 12)
            rl.setSpacing(10)

            ad = t.get("assignedDate")
            if isinstance(ad, datetime):
                date_str = persian_date_long(ad)
                time_str = format_time_12h(ad)
            elif isinstance(ad, date):
                date_str = persian_date_long(ad)
                time_str = ""
            else:
                date_str = str(ad) if ad else "—"
                time_str = ""

            date_lbl = QLabel(date_str)
            date_lbl.setStyleSheet(
                f"color: {c['text_main']}; font-size: 12px; "
                f"font-weight: 700; background: transparent;"
            )
            date_lbl.setMinimumWidth(180)

            time_lbl = QLabel(time_str if time_str else "—")
            time_lbl.setStyleSheet(
                f"color: {c['text_dim']}; font-size: 11px; "
                f"background: transparent;"
            )
            time_lbl.setMinimumWidth(110)

            name_lbl = QLabel(t.get("name") or "—")
            name_lbl.setStyleSheet(
                f"color: {c['accent']}; font-size: 12px; "
                f"font-weight: 700; background: transparent;"
            )
            name_lbl.setMinimumWidth(140)

            title_lbl = QLabel(t.get("jobTitle") or "—")
            title_lbl.setStyleSheet(
                f"color: {c['text_main']}; font-size: 12px; "
                f"background: transparent;"
            )

            price_lbl = QLabel(f"{format_money(t.get('price') or 0)} ت")
            price_lbl.setStyleSheet(
                f"color: {c['success']}; font-size: 12px; "
                f"font-weight: 700; background: transparent;"
            )

            status_key = t.get("status") or "pending"
            st_text, st_badge, st_color = status_map.get(
                status_key, ("—", "statusBadgeOrange", "#B87900")
            )

            badge = QFrame()
            badge.setObjectName(st_badge)
            badge.setAttribute(Qt.WA_StyledBackground, True)
            badge.setFixedSize(90, 26)
            bl = QHBoxLayout(badge)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setAlignment(Qt.AlignCenter)
            blbl = QLabel(st_text)
            blbl.setStyleSheet(
                f"color: {st_color}; font-size: 10px; "
                f"font-weight: 700; background: transparent;"
            )
            bl.addWidget(blbl)

            rl.addWidget(date_lbl, 2)
            rl.addWidget(time_lbl, 1)
            rl.addWidget(name_lbl, 1)
            rl.addWidget(title_lbl, 3)
            rl.addStretch()
            rl.addWidget(price_lbl)
            rl.addWidget(badge)

            layout.addWidget(card)

    def _create_summary_stat(self, title, value, object_name):
        c = theme_manager.colors()

        card = QFrame()
        card.setObjectName(object_name)
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(76)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        t = QLabel(title)
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet(
            f"color: {c['text_dim']}; font-size: 11px; "
            f"font-weight: 600; background: transparent;"
        )

        v = QLabel(value)
        v.setAlignment(Qt.AlignCenter)
        v.setStyleSheet(
            f"color: {c['accent']}; font-size: 18px; "
            f"font-weight: 800; background: transparent;"
        )

        layout.addWidget(t)
        layout.addWidget(v)
        return card