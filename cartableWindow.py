import os
from datetime import datetime, date

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QDialog, QLineEdit,
    QListWidget, QListWidgetItem, QGraphicsDropShadowEffect, QGridLayout,
    QApplication
)

from PySide6.QtCore import (
    Qt, QTimer, QDate, QPoint, QSize, Signal, QRectF
)
from PySide6.QtGui import (
    QPainter, QColor, QRegion, QPainterPath, QGuiApplication
)

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
        track_height = self.height() - 12
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(c["bg_input"]))
        painter.drawRoundedRect(int(track_x), int(track_top), track_width, int(track_height), track_width/2, track_width/2)
        minimum = self.minimum()
        maximum = self.maximum()
        page_step = self.pageStep()
        if maximum <= minimum:
            return
        groove_height = self.height() - 12
        total_range = maximum - minimum + page_step
        handle_height = max(42, int(groove_height * page_step / total_range))
        handle_height = min(handle_height, groove_height)
        available_space = groove_height - handle_height
        if maximum == minimum:
            handle_y = 6
        else:
            value_ratio = (self.value() - minimum) / (maximum - minimum)
            handle_y = 6 + available_space * value_ratio
        handle_width = 8
        handle_x = (self.width() - handle_width) / 2
        painter.setBrush(QColor(c["accent"]))
        painter.drawRoundedRect(int(handle_x), int(handle_y), handle_width, int(handle_height), handle_width/2, handle_width/2)

# =========================================================
# ROUNDED COMBO BOX
# =========================================================

class RoundedComboBox(QWidget):
    currentIndexChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current_index = -1
        self._popup = None
        self._list = None
        self._placeholder = "انتخاب کنید"
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)
        self.setMinimumWidth(180)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def addItem(self, text, data=None):
        self._items.append((text, data))
        if self._current_index == -1:
            self._current_index = 0
        self.update()

    def clear(self):
        self._items = []
        self._current_index = -1
        self.update()

    def count(self):
        return len(self._items)

    def currentData(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][1]
        return None

    def currentText(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][0]
        return ""

    def setCurrentIndex(self, idx):
        if 0 <= idx < len(self._items):
            self._current_index = idx
            self.update()
            self.currentIndexChanged.emit(idx)

    def setPlaceholderText(self, text):
        self._placeholder = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = theme_manager.colors()

        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setPen(QColor(c["border"]))
        painter.setBrush(QColor(c["bg_input"]))
        painter.drawRoundedRect(rect, 22, 22)

        painter.setPen(QColor(c["text_main"]))
        font = painter.font()
        font.setFamily("Vazirmatn")
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)

        text = self.currentText() if self._current_index != -1 else self._placeholder
        text_rect = rect.adjusted(20, 0, -40, 0)
        painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, text)

        arrow_rect = rect.adjusted(rect.width() - 34, 0, -12, 0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(c["accent"]))
        cx = arrow_rect.center().x()
        cy = arrow_rect.center().y()
        painter.drawPolygon(
            QPoint(cx - 5, cy - 2),
            QPoint(cx + 5, cy - 2),
            QPoint(cx, cy + 4)
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.showPopup()
            event.accept()

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
            QListWidget {{background: transparent;border: none;outline: none;
                padding: 6px;color: {c['text_main']};
                font-family: "Vazirmatn";font-size: 12px;}}
            QListWidget::item {{background: transparent;color: {c['text_main']};
                border-radius: 10px;padding: 10px 14px;margin: 2px 4px;
                min-height: 20px;}}
            QListWidget::item:hover {{background-color: {c['bg_hover']};
                color: {c['accent']};}}
            QListWidget::item:selected {{background-color: {c['accent']};
                color: white;}}
            QScrollBar:vertical {{width: 8px;background: transparent;
                border: none;margin: 6px 2px;}}
            QScrollBar::handle:vertical {{background: {c['accent']};
                border-radius: 4px;min-height: 24px;}}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{height: 0px;}}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{background: transparent;}}
        """)

        for i, (text, data) in enumerate(self._items):
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, i)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setSizeHint(QSize(0, 42))
            self._list.addItem(item)
            if i == self._current_index:
                self._list.setCurrentItem(item)

        self._list.itemClicked.connect(self._on_item_clicked)
        card_layout.addWidget(self._list)

        self._popup.setStyleSheet(
            f"QFrame#comboCard {{background-color: {c['bg_card']};"
            f"border: 1px solid {c['border']};border-radius: 18px;}}"
        )

        count = max(len(self._items), 1)
        content_h = count * 42 + 32
        popup_w = max(self.width(), 200)
        popup_h = min(content_h, 260)
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
    return gy, gm, gm, gd if False else (gy, gm, gd)

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

def jalali_string(d):
    if isinstance(d, datetime):
        qdate = QDate(d.year, d.month, d.day)
    elif isinstance(d, date):
        qdate = QDate(d.year, d.month, d.day)
    else:
        return str(d) if d else "—"
    jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
    return f"{jy:04d}/{jm:02d}/{jd:02d}"

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
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 4 + (6 - i) * 2))
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
        path.addRoundedRect(QRectF(self.rect()),
                            self._radius + self._margin,
                            self._radius + self._margin)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def build_ui(self):
        c = theme_manager.colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self._margin + 14, self._margin + 14,
                                   self._margin + 14, self._margin + 14)
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
            QLabel#calMonthLabel {{color: {c['text_main']};font-size: 13px;
                font-weight: 700;background: transparent;}}
            QPushButton#calNavBtn {{background-color: {c['accent_light']};
                color: {c['accent']};border: 1px solid {c['border_hover']};
                border-radius: 10px;font-size: 16px;font-weight: 700;padding: 0px;}}
            QPushButton#calNavBtn:hover {{background-color: {c['bg_hover']};}}
            QLabel#calWeekday {{color: {c['text_dim']};font-size: 10px;
                font-weight: 700;background: transparent;}}
            QPushButton#calDayBtn {{background-color: transparent;
                color: {c['text_main']};border: none;border-radius: 8px;
                font-size: 11px;font-weight: 600;min-height: 28px;}}
            QPushButton#calDayBtn:hover {{background-color: {c['bg_hover']};
                color: {c['accent']};}}
            QPushButton#calDayBtn[today="true"] {{border: 2px solid {c['accent']};
                color: {c['accent']};}}
            QPushButton#calDayBtn[selected="true"] {{background-color: {c['accent']};
                color: white;border: none;}}
        """)

    def refresh_grid(self):
        while self.days_layout.count():
            item = self.days_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
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
            is_selected = (self.view_year == self.selected_jy
                           and self.view_month == self.selected_jm
                           and day == self.selected_jd)
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
        gy, gm, gd = jalali_to_gregorian(
            self.selected_jy, self.selected_jm, self.selected_jd
        )
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
        self.setFixedHeight(44)
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
            screen = QGuiApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                if global_pos.x() + self._popup.width() > geo.right():
                    global_pos.setX(geo.right() - self._popup.width() - 8)
                if global_pos.x() < geo.left():
                    global_pos.setX(geo.left() + 8)
                if global_pos.y() + self._popup.height() > geo.bottom():
                    global_pos.setY(
                        self.mapToGlobal(QPoint(0, 0)).y() - self._popup.height() - 4
                    )
        except Exception:
            pass
        self._popup.move(global_pos)
        self._popup.show()

    def _on_date_selected(self, qdate):
        self._qdate = qdate
        self._refresh_text()
        self.dateChanged.emit(self._qdate)

# =========================================================
# FILTER POPUP
# =========================================================

class FilterPopup(QWidget):
    filterSelected = Signal(str)

    def __init__(self, parent=None, current_filter="all"):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.setLayoutDirection(Qt.RightToLeft)

        self._radius = 18
        self._margin = 6
        self.setFixedSize(230, 350)
        self.current_filter = current_filter
        self.build_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = theme_manager.colors()
        r = self._radius
        m = self._margin
        rect = self.rect().adjusted(m, m, -m, -m)
        for i in range(6, 0, -1):
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 4 + (6 - i) * 2))
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
        path.addRoundedRect(QRectF(self.rect()),
                            self._radius + self._margin,
                            self._radius + self._margin)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def build_ui(self):
        c = theme_manager.colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self._margin + 12, self._margin + 12,
                                   self._margin + 12, self._margin + 12)
        layout.setSpacing(5)

        options = [
            ("all", tr("cartable_all")),
            ("pending", tr("cartable_pending")),
            ("inProgress", tr("cartable_in_progress")),
            ("completed", tr("cartable_completed")),
            ("approved", "تأییدشده"),
            ("rejected", tr("cartable_rejected")),
            ("cancelled", tr("cartable_cancelled")),
        ]

        for key, label in options:
            btn = QPushButton(label)
            btn.setObjectName("filterPopupOption")
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("selected", "true" if key == self.current_filter else "false")
            btn.clicked.connect(lambda checked=False, k=key: self._select(k))
            layout.addWidget(btn)

        layout.addStretch()

        self.setStyleSheet(f"""
            QPushButton#filterPopupOption {{
                background-color: transparent;
                color: {c['text_main']};
                border: none;
                border-radius: 12px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 600;
                text-align: right;
            }}
            QPushButton#filterPopupOption:hover {{
                background-color: {c['bg_hover']};
                color: {c['accent']};
            }}
            QPushButton#filterPopupOption[selected="true"] {{
                background-color: {c['accent']};
                color: white;
            }}
        """)

    def _select(self, key):
        self.filterSelected.emit(key)
        self.close()

# =========================================================
# NICE MESSAGE BOX
# =========================================================

class NiceMessageDialog(QDialog):
    def __init__(self, parent, title, text, kind="info", yes_no=False):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedSize(380, 260)

        self.result_value = False
        c = theme_manager.colors()

        if kind == "success":
            icon_char, color, bg = "✓", "#16A34A", "#DCFCE7"
        elif kind == "error":
            icon_char, color, bg = "✕", "#D93025", "#FEE2E2"
        elif kind == "warning":
            icon_char, color, bg = "!", "#F59E0B", "#FEF3C7"
        elif kind == "question":
            icon_char, color, bg = "?", "#1961C7", "#DBEAFE"
        else:
            icon_char, color, bg = "i", "#1961C7", "#DBEAFE"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['bg_card']};"
            f"border-radius: 22px;border: 1px solid {c['border']};"
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

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        if yes_no:
            no_btn = QPushButton(tr("no"))
            no_btn.setFixedHeight(42)
            no_btn.setMinimumWidth(110)
            no_btn.setCursor(Qt.PointingHandCursor)
            no_btn.setStyleSheet(
                f"background-color: {c['bg_input']};color: {c['text_dim']};"
                f"border: 1px solid {c['border']};border-radius: 12px;"
                f"font-size: 13px;font-weight: 600;padding: 0 20px;"
            )
            no_btn.clicked.connect(self.reject)
            btn_row.addWidget(no_btn)

        yes_btn = QPushButton(tr("yes") if yes_no else tr("ok"))
        yes_btn.setFixedHeight(42)
        yes_btn.setMinimumWidth(120)
        yes_btn.setCursor(Qt.PointingHandCursor)
        yes_btn.setStyleSheet(
            f"background-color: {color};color: white;"
            f"border: none;border-radius: 12px;font-size: 13px;"
            f"font-weight: 700;padding: 0 24px;"
        )

        def on_yes():
            self.result_value = True
            self.accept()

        yes_btn.clicked.connect(on_yes)
        btn_row.addWidget(yes_btn)
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

    @staticmethod
    def ask(parent, title, text):
        d = NiceMessageDialog(parent, title, text, "question", yes_no=True)
        d.exec()
        return d.result_value

# =========================================================
# JOB DIALOG (Add / Edit)
# =========================================================

class JobDialog(QDialog):
    """دیالوگ تعریف/ویرایش کار"""

    def __init__(self, parent, db, complex_id, owner_id, members, edit_data=None):
        super().__init__(parent)

        self.db = db
        self.complex_id = complex_id
        self.owner_id = owner_id
        self.members = members
        self.edit_data = edit_data
        self.is_edit = edit_data is not None

        title_text = "ویرایش کار" if self.is_edit else "تعریف کار جدید"
        self.setWindowTitle(title_text)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumSize(520, 700)
        self.resize(560, 740)

        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet(
            "QScrollArea {background: transparent;border: none;}"
            "QScrollArea::viewport {background: transparent;}"
        )
        vbar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(vbar)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(6)

        c = theme_manager.colors()

        title = QLabel("ویرایش کار" if self.is_edit else "تعریف کار جدید")
        title.setStyleSheet(
            f"color: {c['text_main']};font-size: 17px;"
            f"font-weight: 800;background: transparent;"
        )
        layout.addWidget(title)
        layout.addSpacing(6)

        emp_lbl = QLabel("کارمند")
        emp_lbl.setObjectName("fieldLabel")
        layout.addWidget(emp_lbl)

        self.emp_combo = RoundedComboBox()
        for m in self.members:
            self.emp_combo.addItem(m["name"] or "—", m["memberId"])
        layout.addWidget(self.emp_combo)
        layout.addSpacing(4)

        title_lbl = QLabel("عنوان کار")
        title_lbl.setObjectName("fieldLabel")
        layout.addWidget(title_lbl)

        self.title_input = QLineEdit()
        self.title_input.setObjectName("formInput")
        self.title_input.setPlaceholderText("مثلاً: نصب کولر، رنگ‌آمیزی دیوار")
        self.title_input.setFixedHeight(44)
        self.title_input.textChanged.connect(self._clear_title_error)
        layout.addWidget(self.title_input)

        self.title_error = QLabel()
        self.title_error.setObjectName("fieldError")
        self.title_error.setAlignment(Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter)
        self.title_error.setFixedHeight(18)
        self.title_error.hide()
        layout.addWidget(self.title_error)
        layout.addSpacing(4)

        desc_lbl = QLabel("توضیحات (اختیاری)")
        desc_lbl.setObjectName("fieldLabel")
        layout.addWidget(desc_lbl)

        self.desc_input = QLineEdit()
        self.desc_input.setObjectName("formInput")
        self.desc_input.setPlaceholderText("توضیحات بیشتر درباره کار")
        self.desc_input.setFixedHeight(44)
        layout.addWidget(self.desc_input)
        layout.addSpacing(4)

        money_row = QHBoxLayout()
        money_row.setSpacing(10)

        price_col = QVBoxLayout()
        price_col.setSpacing(4)
        price_lbl = QLabel("مبلغ واحد (تومان)")
        price_lbl.setObjectName("fieldLabel")
        self.price_input = QLineEdit()
        self.price_input.setObjectName("formInput")
        self.price_input.setPlaceholderText("مثلاً: 500000")
        self.price_input.setFixedHeight(44)
        self.price_input.setLayoutDirection(Qt.LeftToRight)
        self.price_input.textChanged.connect(self._clear_price_error)
        price_col.addWidget(price_lbl)
        price_col.addWidget(self.price_input)

        qty_col = QVBoxLayout()
        qty_col.setSpacing(4)
        qty_lbl = QLabel("تعداد")
        qty_lbl.setObjectName("fieldLabel")
        self.qty_input = QLineEdit()
        self.qty_input.setObjectName("formInput")
        self.qty_input.setPlaceholderText("مثلاً: 5")
        self.qty_input.setFixedHeight(44)
        self.qty_input.setLayoutDirection(Qt.LeftToRight)
        self.qty_input.setText("1")
        qty_col.addWidget(qty_lbl)
        qty_col.addWidget(self.qty_input)

        money_row.addLayout(price_col, 1)
        money_row.addLayout(qty_col, 1)
        layout.addLayout(money_row)

        self.price_error = QLabel()
        self.price_error.setObjectName("fieldError")
        self.price_error.setAlignment(Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter)
        self.price_error.setFixedHeight(18)
        self.price_error.hide()
        layout.addWidget(self.price_error)
        layout.addSpacing(4)

        date_row = QHBoxLayout()
        date_row.setSpacing(10)

        start_col = QVBoxLayout()
        start_col.setSpacing(4)
        start_lbl = QLabel("تاریخ شروع")
        start_lbl.setObjectName("fieldLabel")
        self.start_date = PersianDateButton(initial_qdate=QDate.currentDate())
        start_col.addWidget(start_lbl)
        start_col.addWidget(self.start_date)

        deadline_col = QVBoxLayout()
        deadline_col.setSpacing(4)
        deadline_lbl = QLabel("مهلت")
        deadline_lbl.setObjectName("fieldLabel")
        self.deadline_date = PersianDateButton(initial_qdate=QDate.currentDate())
        deadline_col.addWidget(deadline_lbl)
        deadline_col.addWidget(self.deadline_date)

        date_row.addLayout(start_col, 1)
        date_row.addLayout(deadline_col, 1)
        layout.addLayout(date_row)

        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        bottom = QFrame()
        bottom.setAttribute(Qt.WA_StyledBackground, True)
        bottom.setObjectName("bottomBar")
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(28, 14, 28, 14)
        bl.setSpacing(10)

        cancel_btn = QPushButton(tr("cancel"))
        cancel_btn.setFixedHeight(46)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("ذخیره تغییرات" if self.is_edit else "ثبت کار")
        save_btn.setFixedHeight(46)
        save_btn.setMinimumWidth(160)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.on_save)

        bl.addStretch()
        bl.addWidget(cancel_btn)
        bl.addWidget(save_btn)

        main_layout.addWidget(bottom)

        if self.is_edit:
            self._prefill()

    def _clear_title_error(self):
        self.title_error.clear()
        self.title_error.hide()

    def _clear_price_error(self):
        self.price_error.clear()
        self.price_error.hide()

    def _prefill(self):
        d = self.edit_data
        for i, (text, data) in enumerate(self.emp_combo._items):
            if data == d.get("member_id"):
                self.emp_combo.setCurrentIndex(i)
                break

        self.title_input.setText(d.get("title") or "")
        self.desc_input.setText(d.get("description") or "")

        price = d.get("price") or 0
        try:
            self.price_input.setText(f"{int(float(price)):,}")
        except Exception:
            self.price_input.setText("0")

        qty = d.get("quantity")
        if qty:
            try:
                self.qty_input.setText(f"{float(qty):g}")
            except Exception:
                self.qty_input.setText("1")
        else:
            self.qty_input.setText("1")

        sd = d.get("start_date")
        if isinstance(sd, (date, datetime)):
            self.start_date.setDate(QDate(sd.year, sd.month, sd.day))
        dl = d.get("deadline")
        if isinstance(dl, (date, datetime)):
            self.deadline_date.setDate(QDate(dl.year, dl.month, dl.day))

    def on_save(self):
        if self.emp_combo.count() == 0:
            NiceMessageBox.error(self, "خطا", "کارمندی برای انتخاب وجود ندارد.")
            return

        member_id = self.emp_combo.currentData()
        if not member_id:
            NiceMessageBox.error(self, "خطا", "لطفاً کارمند را انتخاب کنید.")
            return

        title_text = self.title_input.text().strip()
        self._clear_title_error()
        if not title_text:
            self.title_error.setText("لطفاً عنوان کار را وارد کنید.")
            self.title_error.show()
            self.title_input.setFocus()
            return
        if len(title_text) < 3:
            self.title_error.setText("عنوان کار باید حداقل ۳ حرف داشته باشد.")
            self.title_error.show()
            self.title_input.setFocus()
            return

        price_text = self.price_input.text().strip()
        self._clear_price_error()
        if not price_text:
            self.price_error.setText("لطفاً مبلغ را وارد کنید.")
            self.price_error.show()
            self.price_input.setFocus()
            return

        try:
            price = float(price_text.replace(",", "").replace("٬", ""))
        except ValueError:
            self.price_error.setText("مبلغ وارد شده معتبر نیست.")
            self.price_error.show()
            self.price_input.setFocus()
            return

        if price <= 0:
            self.price_error.setText("مبلغ باید بیشتر از صفر باشد.")
            self.price_error.show()
            self.price_input.setFocus()
            return

        qty_text = self.qty_input.text().strip()
        quantity = 1.0
        if qty_text:
            try:
                quantity = float(qty_text)
            except ValueError:
                NiceMessageBox.error(self, "خطا", "تعداد باید عدد باشد.")
                self.qty_input.setFocus()
                return
            if quantity <= 0:
                NiceMessageBox.error(self, "خطا", "تعداد باید بیشتر از صفر باشد.")
                self.qty_input.setFocus()
                return

        desc_text = self.desc_input.text().strip()

        start_py = self.start_date.to_python_date()
        deadline_py = self.deadline_date.to_python_date()

        if deadline_py < start_py:
            NiceMessageBox.error(self, "خطا", "مهلت نمی‌تواند قبل از تاریخ شروع باشد.")
            return

        try:
            if self.is_edit:
                job_id = self.edit_data.get("job_id")
                ej_id = self.edit_data.get("id")

                if job_id:
                    self.db.execute(
                        "UPDATE jobs SET jobTitle = %s, description = %s, basePrice = %s "
                        "WHERE jobId = %s",
                        (title_text, desc_text or None, price, job_id)
                    )

                self.db.execute(
                    """
                    UPDATE employee_jobs
                    SET memberId = %s, startDate = %s, deadline = %s,
                        quantity = %s, price = %s, description = %s
                    WHERE employeeJobId = %s
                    """,
                    (member_id, start_py, deadline_py, quantity, price,
                     desc_text or None, ej_id)
                )
            else:
                existing_job = self.db.fetch_one(
                    "SELECT jobId FROM jobs WHERE complexId = %s AND jobTitle = %s LIMIT 1",
                    (self.complex_id, title_text)
                )
                if existing_job:
                    job_id = existing_job["jobId"]
                else:
                    job_id = self.db.execute(
                        """
                        INSERT INTO jobs
                        (complexId, jobTitle, description, employmentType,
                         basePrice, isActive, createdDate)
                        VALUES (%s, %s, %s, 'daily', %s, '1', NOW())
                        """,
                        (self.complex_id, title_text, desc_text or None, price)
                    )
                    if not job_id:
                        NiceMessageBox.error(self, "خطا", "ساخت کار ناموفق بود.")
                        return

                ej_id = self.db.execute(
                    """
                    INSERT INTO employee_jobs
                    (jobId, memberId, assignedBy, assignedDate,
                     startDate, deadline, quantity, price,
                     status, description)
                    VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, 'pending', %s)
                    """,
                    (job_id, member_id, self.owner_id,
                     start_py, deadline_py, quantity, price,
                     desc_text or None)
                )
                if not ej_id:
                    NiceMessageBox.error(self, "خطا", "ثبت کار ناموفق بود.")
                    return

            signals.data_changed.emit("jobs")
            self.accept()
            NiceMessageBox.success(self, "ثبت شد", "تغییرات با موفقیت ذخیره شد.")

        except Exception as e:
            print("JOB SAVE ERROR:", e)
            NiceMessageBox.error(self, "خطا", "خطا در ذخیره‌سازی.")

    def apply_stylesheet(self):
        c = theme_manager.colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c['bg_main']};
                font-family: "Vazirmatn";
            }}
            QLabel#fieldLabel {{
                color: {c['text_dim']};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
                padding: 2px 0px;
            }}
            QLabel#fieldError {{
                color: {c['danger']};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
                padding: 0px 4px;
            }}
            QLineEdit#formInput {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
                padding: 0 18px;
                color: {c['text_main']};
                font-size: 12px;
                min-height: 44px;
            }}
            QLineEdit#formInput:focus {{
                background-color: {c['bg_card']};
                border: 2px solid {c['accent']};
            }}
            QFrame#persianDateFrame {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
            }}
            QFrame#persianDateFrame:hover {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border_hover']};
            }}
            QLabel#dateIconLabel {{
                background-color: {c['accent_light']};
                border: none;
                border-radius: 10px;
                font-size: 15px;
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
            QFrame#bottomBar {{
                background-color: {c['bg_card']};
                border-top: 1px solid {c['border']};
            }}
            QPushButton#cancelBtn {{
                background-color: {c['bg_input']};
                color: {c['text_dim']};
                border: 1px solid {c['border']};
                border-radius: 23px;
                padding: 0 26px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton#cancelBtn:hover {{
                background-color: {c['bg_hover']};
            }}
            QPushButton#saveBtn {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 23px;
                padding: 0 30px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton#saveBtn:hover {{
                background-color: {c['accent_hover']};
            }}
        """)

# =========================================================
# CARTABLE WINDOW
# =========================================================

class CartableWindow(QWidget):

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
        self.member_id = None
        self.role = None
        self.is_owner = False
        self.members = []
        self.all_items = []
        self.current_filter = "all"

        self.setWindowTitle(tr("cartable_title"))
        self.setMinimumSize(500, 400)
        self.resize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("cartableWindow")

        self.load_user_data()
        self.setup_ui()
        self.load_items()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)
        signals.employee_added.connect(self.on_employee_changed)
        signals.employee_updated.connect(self.on_employee_changed)
        signals.data_changed.connect(self.on_data_changed)

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("cartable_title"))
        QTimer.singleShot(0, self._rebuild)

    def _rebuild(self):
        old = self.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                w = item.widget()
                if w:
                    w.setParent(None)
                    w.deleteLater()
        self.setup_ui()
        self.load_items()

    def on_employee_changed(self, complex_id):
        if complex_id == self.complex_id:
            self.load_members()
            self.load_items()

    def on_data_changed(self, kind):
        if kind in ("all", "jobs", "attendance", "finance"):
            self.load_items()

    def load_user_data(self):
        if not self.phone_number:
            return
        try:
            user = self.db.fetch_one(
                "SELECT userId FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if not user:
                return
            self.user_id = user["userId"]

            if self.complex_id:
                member = self.db.fetch_one(
                    """
                    SELECT memberId, role
                    FROM complex_members
                    WHERE complexId = %s AND userId = %s AND isActive = '1'
                    LIMIT 1
                    """,
                    (self.complex_id, self.user_id)
                )
                if member:
                    self.member_id = member["memberId"]
                    self.role = member["role"]
                    self.is_owner = self.role in ("owner", "both")

            self.load_members()

        except Exception as e:
            print("CARTABLE LOAD USER ERROR:", e)

    def load_members(self):
        self.members = []
        if not self.complex_id:
            return
        try:
            rows = self.db.fetch_all(
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
            for r in rows or []:
                self.members.append({
                    "memberId": r["memberId"],
                    "name": r.get("name") or "—"
                })
        except Exception as e:
            print("LOAD MEMBERS ERROR:", e)

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

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

        title = QLabel(tr("cartable_title"))
        title.setObjectName("cartableTitle")

        subtitle = QLabel(tr("cartable_subtitle"))
        subtitle.setObjectName("cartableSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        if self.is_owner:
            add_btn = QPushButton("＋  تعریف کار جدید")
            add_btn.setObjectName("addJobBtn")
            add_btn.setFixedHeight(42)
            add_btn.setCursor(Qt.PointingHandCursor)
            add_btn.setAttribute(Qt.WA_StyledBackground, True)
            add_btn.clicked.connect(self.open_add_job_dialog)
            header_layout.addWidget(add_btn)

        main_layout.addLayout(header_layout)

        filter_box = QFrame()
        filter_box.setObjectName("filterBox")
        filter_box.setAttribute(Qt.WA_StyledBackground, True)

        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setContentsMargins(14, 10, 14, 10)
        filter_layout.setSpacing(10)

        filter_lbl = QLabel("نمایش:")
        filter_lbl.setObjectName("filterLabel")
        filter_layout.addWidget(filter_lbl)

        self.filter_dropdown_btn = QPushButton()
        self.filter_dropdown_btn.setObjectName("filterDropdown")
        self.filter_dropdown_btn.setFixedHeight(42)
        self.filter_dropdown_btn.setMinimumWidth(180)
        self.filter_dropdown_btn.setCursor(Qt.PointingHandCursor)
        self.filter_dropdown_btn.setAttribute(Qt.WA_StyledBackground, True)
        self.filter_dropdown_btn.clicked.connect(self.open_filter_popup)
        self._refresh_filter_button_text()
        filter_layout.addWidget(self.filter_dropdown_btn)

        filter_layout.addStretch()

        self.count_label = QLabel()
        self.count_label.setObjectName("countLabel")
        filter_layout.addWidget(self.count_label)

        main_layout.addWidget(filter_box)

        records_box = QFrame()
        records_box.setObjectName("recordsBox")
        records_box.setAttribute(Qt.WA_StyledBackground, True)

        records_layout = QVBoxLayout(records_box)
        records_layout.setContentsMargins(14, 14, 14, 14)
        records_layout.setSpacing(8)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        round_bar = RoundScrollBar(Qt.Vertical, self.scroll)
        self.scroll.setVerticalScrollBar(round_bar)

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setAttribute(Qt.WA_TranslucentBackground, True)

        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setContentsMargins(4, 4, 8, 4)

        self.scroll.setWidget(scroll_content)
        records_layout.addWidget(self.scroll)

        main_layout.addWidget(records_box, 1)

        self.apply_stylesheet()

    def _filter_label_for(self, key):
        return {
            "all": tr("cartable_all"),
            "pending": tr("cartable_pending"),
            "inProgress": tr("cartable_in_progress"),
            "completed": tr("cartable_completed"),
            "approved": "تأییدشده",
            "rejected": tr("cartable_rejected"),
            "cancelled": tr("cartable_cancelled"),
        }.get(key, tr("cartable_all"))

    def _refresh_filter_button_text(self):
        label = self._filter_label_for(self.current_filter)
        self.filter_dropdown_btn.setText(f"{label}   ▾")

    def open_filter_popup(self):
        self._popup = FilterPopup(self, self.current_filter)
        self._popup.filterSelected.connect(self.on_filter_selected)

        global_pos = self.filter_dropdown_btn.mapToGlobal(
            QPoint(0, self.filter_dropdown_btn.height() + 4)
        )
        try:
            screen = QGuiApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                if global_pos.x() + self._popup.width() > geo.right():
                    global_pos.setX(geo.right() - self._popup.width() - 8)
                if global_pos.x() < geo.left():
                    global_pos.setX(geo.left() + 8)
        except Exception:
            pass
        self._popup.move(global_pos)
        self._popup.show()

    def on_filter_selected(self, key):
        self.current_filter = key
        self._refresh_filter_button_text()
        self.refresh_records()

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""

        QWidget#cartableWindow {{
            background-color: {c['bg_main']};
            font-family: Vazirmatn;
            color: {c['text_main']};
        }}

        QLabel#cartableTitle {{
            color: {c['text_main']};
            font-size: 20px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#cartableSubtitle {{
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

        QPushButton#addJobBtn {{
            background-color: {c['accent']};
            color: white;
            border: none;
            border-radius: 21px;
            padding: 0 22px;
            font-size: 12px;
            font-weight: 700;
        }}

        QPushButton#addJobBtn:hover {{
            background-color: {c['accent_hover']};
        }}

        QFrame#filterBox {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}

        QLabel#filterLabel {{
            color: {c['text_dim']};
            font-size: 12px;
            font-weight: 700;
            background: transparent;
            padding-right: 4px;
        }}

        QPushButton#filterDropdown {{
            background-color: {c['bg_input']};
            color: {c['text_main']};
            border: 1px solid {c['border']};
            border-radius: 21px;
            padding: 0 20px;
            font-size: 12px;
            font-weight: 700;
            text-align: right;
        }}

        QPushButton#filterDropdown:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['border_hover']};
            color: {c['accent']};
        }}

        QLabel#countLabel {{
            color: {c['text_dim']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }}

        QFrame#recordsBox {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}

        QWidget#scrollContent {{
            background: transparent;
        }}

        QScrollArea {{
            background: transparent;
            border: none;
        }}

        QScrollArea::viewport {{
            background: transparent;
        }}

        QFrame#itemCard {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 16px;
        }}

        QFrame#itemCard:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['accent']};
        }}

        QFrame#itemCard QLabel {{
            background: transparent;
            border: none;
        }}

        QLabel#itemTitle {{
            color: {c['text_main']};
            font-size: 13px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#itemName {{
            color: {c['accent']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }}

        QLabel#itemInfo {{
            color: {c['text_dim']};
            font-size: 10px;
            background: transparent;
        }}

        QLabel#itemDesc {{
            color: {c['text_dim']};
            font-size: 11px;
            background: transparent;
        }}

        QLabel#statusPending {{
            color: {c['warning']};
            background-color: {c['warning_bg']};
            border: none;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#statusInProgress {{
            color: {c['accent']};
            background-color: {c['accent_light']};
            border: 1px solid {c['accent']};
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#statusCompleted {{
            color: #B87900;
            background-color: #FFF4DD;
            border: 1px solid #B87900;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#statusApproved {{
            color: #16A34A;
            background-color: {c['success_bg']};
            border: 1px solid #16A34A;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#statusRejected {{
            color: {c['danger']};
            background-color: {c['danger_bg']};
            border: 1px solid {c['danger']};
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#statusCancelled {{
            color: {c['text_dim']};
            background-color: {c['bg_input']};
            border: 1px solid {c['border']};
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QPushButton#editBtn {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border: 1px solid {c['border_hover']};
            border-radius: 14px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            min-height: 28px;
        }}

        QPushButton#editBtn:hover {{
            background-color: {c['bg_hover']};
        }}

        QPushButton#approveBtn {{
            background-color: {c['success_bg']};
            color: #16A34A;
            border: 1px solid #16A34A;
            border-radius: 14px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            min-height: 28px;
        }}

        QPushButton#approveBtn:hover {{
            background-color: {c['bg_hover']};
        }}

        QPushButton#rejectBtn {{
            background-color: {c['danger_bg']};
            color: {c['danger']};
            border: 1px solid {c['danger']};
            border-radius: 14px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            min-height: 28px;
        }}

        QPushButton#rejectBtn:hover {{
            background-color: {c['bg_hover']};
        }}

        QPushButton#startBtn {{
            background-color: {c['accent']};
            color: white;
            border: 1px solid {c['accent']};
            border-radius: 14px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            min-height: 30px;
        }}

        QPushButton#startBtn:hover {{
            background-color: {c['accent_hover']};
        }}

        QPushButton#startBtn:disabled {{
            background-color: {c['bg_input']};
            color: {c['text_dim']};
            border: 1px solid {c['border']};
        }}

        QPushButton#doneBtn {{
            background-color: {c['success_bg']};
            color: #16A34A;
            border: 1px solid #16A34A;
            border-radius: 14px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            min-height: 30px;
        }}

        QPushButton#doneBtn:hover {{
            background-color: #D6F0DD;
        }}

        QPushButton#doneBtn:disabled {{
            background-color: {c['bg_input']};
            color: {c['text_dim']};
            border: 1px dashed {c['border']};
        }}

        QPushButton#employeeDeleteBtn {{
            background-color: {c['danger_bg']};
            color: {c['danger']};
            border: 1px solid {c['danger']};
            border-radius: 14px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            min-height: 28px;
        }}

        QPushButton#employeeDeleteBtn:hover {{
            background-color: {c['danger']};
            color: white;
        }}

        QPushButton#ownerDeleteBtn {{
            background-color: transparent;
            color: {c['danger']};
            border: 1px dashed {c['danger']};
            border-radius: 14px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            min-height: 28px;
        }}

        QPushButton#ownerDeleteBtn:hover {{
            background-color: {c['danger_bg']};
            border-style: solid;
        }}

        QLabel#emptyLabel {{
            color: {c['text_dim']};
            font-size: 13px;
            padding: 40px;
            background: transparent;
        }}

        """)

    def load_items(self):
        self.all_items = []

        if not self.complex_id or not self.member_id:
            self.refresh_records()
            return

        try:
            if self.is_owner:
                rows = self.db.fetch_all(
                    """
                    SELECT ej.employeeJobId, ej.jobId, ej.memberId, ej.assignedBy,
                           ej.assignedDate, ej.startDate, ej.deadline, ej.quantity,
                           ej.price, ej.status, ej.description, ej.completedDate,
                           u.name AS employee_name,
                           au.name AS assigner_name,
                           j.jobTitle
                    FROM employee_jobs ej
                    INNER JOIN complex_members cm ON cm.memberId = ej.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    LEFT JOIN users au ON au.userId = ej.assignedBy
                    LEFT JOIN jobs j ON j.jobId = ej.jobId
                    WHERE cm.complexId = %s
                    ORDER BY ej.assignedDate DESC
                    LIMIT 200
                    """,
                    (self.complex_id,)
                )
            else:
                rows = self.db.fetch_all(
                    """
                    SELECT ej.employeeJobId, ej.jobId, ej.memberId, ej.assignedBy,
                           ej.assignedDate, ej.startDate, ej.deadline, ej.quantity,
                           ej.price, ej.status, ej.description, ej.completedDate,
                           u.name AS employee_name,
                           au.name AS assigner_name,
                           j.jobTitle
                    FROM employee_jobs ej
                    INNER JOIN complex_members cm ON cm.memberId = ej.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    LEFT JOIN users au ON au.userId = ej.assignedBy
                    LEFT JOIN jobs j ON j.jobId = ej.jobId
                    WHERE cm.complexId = %s AND ej.memberId = %s
                    ORDER BY ej.assignedDate DESC
                    LIMIT 200
                    """,
                    (self.complex_id, self.member_id)
                )

            for r in rows or []:
                self.all_items.append({
                    "id": r["employeeJobId"],
                    "job_id": r.get("jobId"),
                    "member_id": r.get("memberId"),
                    "title": r.get("jobTitle") or tr("job_no_desc"),
                    "employee_name": r.get("employee_name") or "—",
                    "assigner_name": r.get("assigner_name") or "—",
                    "assigned_date": r.get("assignedDate"),
                    "start_date": r.get("startDate"),
                    "deadline": r.get("deadline"),
                    "quantity": r.get("quantity"),
                    "price": r.get("price"),
                    "status": (r.get("status") or "pending"),
                    "description": r.get("description") or "",
                    "completed_date": r.get("completedDate"),
                })

        except Exception as e:
            print("CARTABLE LOAD ERROR:", e)

        self.refresh_records()

    def refresh_records(self):
        # ═══ پاک‌سازی فوری برای جلوگیری از artifact ═══
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        # پردازش رویدادها برای اطمینان از پاک شدن
        QApplication.processEvents()

        if self.current_filter == "all":
            filtered = self.all_items
        else:
            filtered = [i for i in self.all_items if i["status"] == self.current_filter]

        self.count_label.setText(f"{len(filtered)} کار")

        if not filtered:
            empty = QLabel(tr("no_cartable_items"))
            empty.setObjectName("emptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty)
            self.scroll_layout.addStretch()
            return

        for it in filtered:
            self.scroll_layout.addWidget(self.create_item_card(it))

        self.scroll_layout.addStretch()

    def create_item_card(self, item):

        card = QFrame()
        card.setObjectName("itemCard")
        card.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        title = QLabel(item["title"])
        title.setObjectName("itemTitle")
        title.setWordWrap(True)

        emp = QLabel(f"{tr('job_assigned_to')}: {item['employee_name']}")
        emp.setObjectName("itemName")

        info1 = QLabel(
            f"{tr('job_start_date')}: {jalali_string(item['start_date'])}   •   "
            f"{tr('job_deadline')}: {jalali_string(item['deadline'])}"
        )
        info1.setObjectName("itemInfo")

        qty_text = f"{item['quantity']:g}" if item.get("quantity") else "1"
        price_text = f"{format_money(item['price'])} {tr('toman')}" if item.get("price") else "-"
        info2 = QLabel(
            f"{tr('job_quantity')}: {qty_text}   •   "
            f"{tr('job_price')}: {price_text}"
        )
        info2.setObjectName("itemInfo")

        text_col.addWidget(title)
        text_col.addWidget(emp)
        text_col.addWidget(info1)
        text_col.addWidget(info2)

        if item.get("description"):
            desc = QLabel(item["description"])
            desc.setObjectName("itemDesc")
            desc.setWordWrap(True)
            text_col.addWidget(desc)

        layout.addLayout(text_col, 1)

        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.setAlignment(Qt.AlignTop)

        status = item["status"]
        badge = QLabel()
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(26)

        if status == "approved":
            badge.setText("✓ تأییدشده")
            badge.setObjectName("statusApproved")
        elif status == "completed":
            badge.setText("◔ منتظر تأیید")
            badge.setObjectName("statusCompleted")
        elif status == "inProgress":
            badge.setText("▶ در حال انجام")
            badge.setObjectName("statusInProgress")
        elif status == "rejected":
            badge.setText(tr("cartable_rejected"))
            badge.setObjectName("statusRejected")
        elif status == "cancelled":
            badge.setText(tr("cartable_cancelled"))
            badge.setObjectName("statusCancelled")
        else:
            badge.setText(tr("cartable_pending"))
            badge.setObjectName("statusPending")

        right_col.addWidget(badge)

        # ═══════════════════════════════════════════════
        # مالک
        # ═══════════════════════════════════════════════
        if self.is_owner:
            edit_btn = QPushButton("✎ ویرایش")
            edit_btn.setObjectName("editBtn")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.clicked.connect(
                lambda checked=False, i=item: self.open_edit_job_dialog(i)
            )
            right_col.addWidget(edit_btn)

            if status == "completed":
                approve_btn = QPushButton("✓ تأیید")
                approve_btn.setObjectName("approveBtn")
                approve_btn.setCursor(Qt.PointingHandCursor)
                approve_btn.clicked.connect(
                    lambda checked=False, i=item: self.approve_item(i)
                )
                right_col.addWidget(approve_btn)

                reject_btn = QPushButton("✕ رد")
                reject_btn.setObjectName("rejectBtn")
                reject_btn.setCursor(Qt.PointingHandCursor)
                reject_btn.clicked.connect(
                    lambda checked=False, i=item: self.reject_item(i)
                )
                right_col.addWidget(reject_btn)

            if status in ("pending", "inProgress", "rejected", "cancelled"):
                del_btn = QPushButton("🗑 حذف")
                del_btn.setObjectName("ownerDeleteBtn")
                del_btn.setCursor(Qt.PointingHandCursor)
                del_btn.clicked.connect(
                    lambda checked=False, i=item: self.owner_delete_item(i)
                )
                right_col.addWidget(del_btn)

        # ═══════════════════════════════════════════════
        # کارمند — دو دکمه با ورک‌فلو
        # ═══════════════════════════════════════════════
        else:
            # دکمه شروع کار
            start_btn = QPushButton("▶  شروع کار")
            start_btn.setObjectName("startBtn")
            start_btn.setCursor(Qt.PointingHandCursor)
            start_btn.setFixedHeight(34)
            start_btn.clicked.connect(
                lambda checked=False, i=item: self.start_item(i)
            )

            # دکمه ثبت نهایی (انجام شد)
            done_btn = QPushButton("✓  ثبت نهایی")
            done_btn.setObjectName("doneBtn")
            done_btn.setCursor(Qt.PointingHandCursor)
            done_btn.setFixedHeight(34)
            done_btn.clicked.connect(
                lambda checked=False, i=item: self.complete_item(i)
            )

            # منطق فعال/غیرفعال بودن
            if status == "pending":
                # فقط شروع فعال، ثبت نهایی غیرفعال
                start_btn.setEnabled(True)
                done_btn.setEnabled(False)
                start_btn.show()
                done_btn.show()
                right_col.addWidget(start_btn)
                right_col.addWidget(done_btn)

            elif status == "inProgress":
                # شروع غیرفعال، ثبت نهایی فعال
                start_btn.setEnabled(False)
                done_btn.setEnabled(True)
                start_btn.show()
                done_btn.show()
                right_col.addWidget(start_btn)
                right_col.addWidget(done_btn)

            # کارمند می‌تونه کار خودش رو لغو کنه
            if status in ("pending", "inProgress"):
                del_btn = QPushButton("🗑 لغو کار")
                del_btn.setObjectName("employeeDeleteBtn")
                del_btn.setCursor(Qt.PointingHandCursor)
                del_btn.setFixedHeight(34)
                del_btn.clicked.connect(
                    lambda checked=False, i=item: self.employee_delete_item(i)
                )
                right_col.addWidget(del_btn)

        right_col.addStretch()
        layout.addLayout(right_col)

        return card

    # =====================================================
    # OWNER: ADD / EDIT
    # =====================================================

    def open_add_job_dialog(self):
        if not self.is_owner:
            return
        if not self.members:
            NiceMessageBox.warning(
                self, "هشدار",
                "کارمندی برای این مجموعه تعریف نشده است."
            )
            return

        dialog = JobDialog(
            self, self.db, self.complex_id, self.user_id, self.members
        )
        if dialog.exec() == QDialog.Accepted:
            self.load_items()

    def open_edit_job_dialog(self, item):
        if not self.is_owner:
            return
        if not self.members:
            NiceMessageBox.warning(
                self, "هشدار",
                "کارمندی برای این مجموعه تعریف نشده است."
            )
            return

        edit_data = {
            "id": item["id"],
            "job_id": item["job_id"],
            "member_id": item["member_id"],
            "title": item["title"],
            "description": item["description"],
            "price": item["price"],
            "quantity": item["quantity"],
            "start_date": item["start_date"],
            "deadline": item["deadline"],
        }

        dialog = JobDialog(
            self, self.db, self.complex_id, self.user_id, self.members,
            edit_data=edit_data
        )
        if dialog.exec() == QDialog.Accepted:
            self.load_items()

    # =====================================================
    # OWNER: APPROVE / REJECT
    # =====================================================

    def approve_item(self, item):
        item_id = item["id"]
        try:
            self.db.execute(
                """
                UPDATE employee_jobs
                SET status = 'approved', completedDate = NOW()
                WHERE employeeJobId = %s
                """,
                (item_id,)
            )
            if self.user_id:
                self.db.execute(
                    """
                    INSERT INTO job_approvals
                    (employeeJobId, approvedBy, status, approvalDate)
                    VALUES (%s, %s, 'approved', NOW())
                    """,
                    (item_id, self.user_id)
                )
            self.load_items()
            signals.data_changed.emit("jobs")
            NiceMessageBox.success(
                self, "تأیید شد",
                f"کار {item.get('employee_name', '')} تأیید شد."
            )
        except Exception as e:
            print("APPROVE ERROR:", e)
            NiceMessageBox.error(self, tr("error"), "تأیید انجام نشد.")

    def reject_item(self, item):
        item_id = item["id"]
        try:
            self.db.execute(
                """
                UPDATE employee_jobs
                SET status = 'rejected'
                WHERE employeeJobId = %s
                """,
                (item_id,)
            )
            if self.user_id:
                self.db.execute(
                    """
                    INSERT INTO job_approvals
                    (employeeJobId, approvedBy, status, approvalDate)
                    VALUES (%s, %s, 'rejected', NOW())
                    """,
                    (item_id, self.user_id)
                )
            self.load_items()
            signals.data_changed.emit("jobs")
            NiceMessageBox.warning(
                self, "رد شد",
                f"کار {item.get('employee_name', '')} رد شد."
            )
        except Exception as e:
            print("REJECT ERROR:", e)
            NiceMessageBox.error(self, tr("error"), "رد انجام نشد.")

    # =====================================================
    # OWNER: DELETE
    # =====================================================

    def owner_delete_item(self, item):
        item_id = item["id"]
        title = item.get("title") or "—"

        confirmed = NiceMessageBox.ask(
            self, "حذف کار",
            f"آیا از حذف کار «{title}» مطمئن هستید؟\nاین عمل قابل بازگشت نیست."
        )
        if not confirmed:
            return

        try:
            self.db.execute(
                "DELETE FROM payments WHERE employeeJobId = %s",
                (item_id,)
            )
            self.db.execute(
                "DELETE FROM job_approvals WHERE employeeJobId = %s",
                (item_id,)
            )
            self.db.execute(
                "DELETE FROM employee_jobs WHERE employeeJobId = %s",
                (item_id,)
            )

            self.load_items()
            signals.data_changed.emit("jobs")
            NiceMessageBox.success(self, "حذف شد", "کار با موفقیت حذف شد.")

        except Exception as e:
            print("OWNER DELETE ERROR:", e)
            NiceMessageBox.error(self, tr("error"), "حذف انجام نشد.")

    # =====================================================
    # EMPLOYEE: START / COMPLETE / DELETE
    # =====================================================

    def start_item(self, item):
        item_id = item["id"]
        try:
            self.db.execute(
                """
                UPDATE employee_jobs
                SET status = 'inProgress'
                WHERE employeeJobId = %s
                """,
                (item_id,)
            )
            self.load_items()
            signals.data_changed.emit("jobs")
            NiceMessageBox.success(
                self, "شروع شد",
                "کار در حال انجام ثبت شد."
            )
        except Exception as e:
            print("START ERROR:", e)
            NiceMessageBox.error(self, tr("error"), "ثبت شروع انجام نشد.")

    def complete_item(self, item):
        item_id = item["id"]
        try:
            self.db.execute(
                """
                UPDATE employee_jobs
                SET status = 'completed', completedDate = NOW()
                WHERE employeeJobId = %s
                """,
                (item_id,)
            )
            self.load_items()
            signals.data_changed.emit("jobs")
            NiceMessageBox.success(
                self, "انجام شد",
                "کار برای تأیید مالک ارسال شد."
            )
        except Exception as e:
            print("COMPLETE ERROR:", e)
            NiceMessageBox.error(self, tr("error"), "ثبت انجام کار ناموفق بود.")

    def employee_delete_item(self, item):
        item_id = item["id"]
        title = item.get("title") or "—"

        confirmed = NiceMessageBox.ask(
            self, "لغو کار",
            f"آیا از لغو کار «{title}» مطمئن هستید؟\n"
            f"بعد از لغو، مالک می‌تواند کار را حذف کند."
        )
        if not confirmed:
            return

        try:
            self.db.execute(
                """
                UPDATE employee_jobs
                SET status = 'cancelled'
                WHERE employeeJobId = %s
                """,
                (item_id,)
            )
            self.load_items()
            signals.data_changed.emit("jobs")
            NiceMessageBox.success(
                self, "لغو شد",
                "کار با موفقیت لغو شد."
            )
        except Exception as e:
            print("EMPLOYEE DELETE ERROR:", e)
            NiceMessageBox.error(self, tr("error"), "لغو انجام نشد.")