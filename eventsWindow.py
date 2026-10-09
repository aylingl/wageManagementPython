import os
from datetime import datetime, date

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QGridLayout
)

from PySide6.QtCore import (
    Qt, QTimer, QDate, QPoint, QRectF, Signal
)
from PySide6.QtGui import (
    QPainter, QColor, QRegion, QPainterPath, QGuiApplication
)

from database import Database
from theme import theme_manager
from signals import signals
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

MONTH_NAMES = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]

WEEKDAY_SHORT = ["ش", "ی", "د", "س", "چ", "پ", "ج"]

def jalali_string_from_date(d):
    if isinstance(d, datetime):
        qdate = QDate(d.year, d.month, d.day)
        jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
        return f"{jy:04d}/{jm:02d}/{jd:02d} - {d.strftime('%H:%M')}"
    elif isinstance(d, date):
        jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
        return f"{jy:04d}/{jm:02d}/{jd:02d}"
    return str(d)

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
        path.addRoundedRect(
            QRectF(self.rect()),
            self._radius + self._margin,
            self._radius + self._margin
        )
        polygon = path.toFillPolygon().toPolygon()
        self.setMask(QRegion(polygon))

    def build_ui(self):
        c = theme_manager.colors()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self._margin + 14, self._margin + 14,
            self._margin + 14, self._margin + 14
        )
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

        self.month_label.setText(
            f"{MONTH_NAMES[self.view_month - 1]} {self.view_year}"
        )

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

        self._qdate = (
            initial_qdate if initial_qdate is not None else QDate.currentDate()
        )

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
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geo = screen.availableGeometry()
                if global_pos.x() + self._popup.width() > screen_geo.right():
                    global_pos.setX(
                        screen_geo.right() - self._popup.width() - 8
                    )
                if global_pos.x() < screen_geo.left():
                    global_pos.setX(screen_geo.left() + 8)
                if global_pos.y() + self._popup.height() > screen_geo.bottom():
                    global_pos.setY(
                        self.mapToGlobal(QPoint(0, 0)).y()
                        - self._popup.height() - 4
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
# FILTER POPUP (rounded, for show-records filter)
# =========================================================

class FilterPopup(QWidget):

    filterSelected = Signal(str)

    def __init__(self, parent=None, current_filter="all"):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.setLayoutDirection(Qt.RightToLeft)

        self._radius = 18
        self._margin = 6
        self.setFixedSize(220, 320)

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
            shadow_color = QColor(0, 0, 0, 4 + (6 - i) * 2)
            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)
            painter.drawRoundedRect(
                rect.adjusted(-i, -i + 2, i, i + 2), r + i, r + i
            )

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
        path.addRoundedRect(
            QRectF(self.rect()),
            self._radius + self._margin,
            self._radius + self._margin
        )
        polygon = path.toFillPolygon().toPolygon()
        self.setMask(QRegion(polygon))

    def build_ui(self):
        c = theme_manager.colors()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self._margin + 12, self._margin + 12,
            self._margin + 12, self._margin + 12
        )
        layout.setSpacing(6)

        options = [
            ("all", tr("filter_all")),
            ("payment", tr("filter_payments")),
            ("attendance", tr("filter_attendance")),
            ("leave", tr("filter_leaves")),
            ("loan", tr("filter_loans")),
            ("other", tr("filter_others")),
        ]

        for key, label in options:
            btn = QPushButton(label)
            btn.setObjectName("filterPopupOption")
            btn.setFixedHeight(42)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty(
                "selected",
                "true" if key == self.current_filter else "false"
            )
            btn.clicked.connect(
                lambda checked=False, k=key: self._select(k)
            )
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
# EVENTS WINDOW
# =========================================================

class EventsWindow(QWidget):

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

        self.all_events = []
        self.current_filter = "all"

        # ═══ فیلتر تاریخ ═══
        self.selected_date_filter = None   # None = بدون فیلتر تاریخ

        self.setWindowTitle(tr("events_title"))
        self.setMinimumSize(500, 400)
        self.resize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("eventsWindow")

        self.load_user_id()
        self.setup_ui()
        self.load_events()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)
        signals.data_changed.connect(self.on_data_changed)

    # =====================================================
    # THEME / LANGUAGE / DATA
    # =====================================================

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("events_title"))
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
        self.load_events()

    def on_data_changed(self, kind):
        self.load_events()

    # =====================================================
    # LOAD USER ID + ROLE
    # =====================================================

    def load_user_id(self):
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

        except Exception as e:
            print("LOAD USER ID ERROR:", e)

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        # HEADER
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.go_back)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel(tr("events_title"))
        title.setObjectName("title")

        subtitle = QLabel(tr("events_subtitle"))
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # =========================
        # FILTER BOX (تاریخ + دراپ‌داون فیلتر)
        # =========================
        filter_box = QFrame()
        filter_box.setObjectName("filterBox")
        filter_box.setAttribute(Qt.WA_StyledBackground, True)

        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(10)

        # --- تاریخ ---
        date_lbl = QLabel("تاریخ:")
        date_lbl.setObjectName("filterLabel")
        filter_layout.addWidget(date_lbl)

        self.date_picker = PersianDateButton()
        self.date_picker.dateChanged.connect(self.on_date_changed)
        filter_layout.addWidget(self.date_picker)

        self.clear_date_btn = QPushButton("✕")
        self.clear_date_btn.setObjectName("clearDateBtn")
        self.clear_date_btn.setFixedSize(30, 30)
        self.clear_date_btn.setCursor(Qt.PointingHandCursor)
        self.clear_date_btn.setAttribute(Qt.WA_StyledBackground, True)
        self.clear_date_btn.clicked.connect(self.clear_date_filter)
        self.clear_date_btn.setToolTip("حذف فیلتر تاریخ")
        self.clear_date_btn.hide()
        filter_layout.addWidget(self.clear_date_btn)

        filter_layout.addStretch()

        # --- دراپ‌داون فیلتر ---
        self.filter_label_widget = QLabel(tr("show_records"))
        self.filter_label_widget.setObjectName("filterLabel")
        filter_layout.addWidget(self.filter_label_widget)

        self.filter_dropdown_btn = QPushButton()
        self.filter_dropdown_btn.setObjectName("filterDropdown")
        self.filter_dropdown_btn.setFixedHeight(42)
        self.filter_dropdown_btn.setMinimumWidth(160)
        self.filter_dropdown_btn.setCursor(Qt.PointingHandCursor)
        self.filter_dropdown_btn.setAttribute(Qt.WA_StyledBackground, True)
        self.filter_dropdown_btn.clicked.connect(self.open_filter_popup)
        self._refresh_filter_button_text()
        filter_layout.addWidget(self.filter_dropdown_btn)

        main_layout.addWidget(filter_box)

        # RECORDS BOX
        records_box = QFrame()
        records_box.setObjectName("recordsBox")
        records_box.setAttribute(Qt.WA_StyledBackground, True)

        records_layout = QVBoxLayout(records_box)
        records_layout.setContentsMargins(20, 20, 20, 20)
        records_layout.setSpacing(12)

        records_title = QLabel(tr("records_recorded"))
        records_title.setObjectName("sectionTitle")

        records_layout.addWidget(records_title)

        # SCROLL
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
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(6, 6, 11, 6)

        self.scroll.setWidget(scroll_content)

        records_layout.addWidget(self.scroll)

        main_layout.addWidget(records_box)

        self.apply_stylesheet()

    # =====================================================
    # FILTER BUTTON TEXT
    # =====================================================

    def _filter_label_for(self, key):
        return {
            "all": tr("filter_all"),
            "payment": tr("filter_payments"),
            "attendance": tr("filter_attendance"),
            "leave": tr("filter_leaves"),
            "loan": tr("filter_loans"),
            "other": tr("filter_others"),
        }.get(key, tr("filter_all"))

    def _refresh_filter_button_text(self):
        label = self._filter_label_for(self.current_filter)
        self.filter_dropdown_btn.setText(f"{label}   ▾")

    # =====================================================
    # FILTER POPUP OPEN
    # =====================================================

    def open_filter_popup(self):
        self._popup = FilterPopup(self, self.current_filter)
        self._popup.filterSelected.connect(self.on_filter_selected)

        global_pos = self.filter_dropdown_btn.mapToGlobal(
            QPoint(0, self.filter_dropdown_btn.height() + 4)
        )

        try:
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geo = screen.availableGeometry()
                if global_pos.x() + self._popup.width() > screen_geo.right():
                    global_pos.setX(
                        screen_geo.right() - self._popup.width() - 8
                    )
                if global_pos.x() < screen_geo.left():
                    global_pos.setX(screen_geo.left() + 8)
        except Exception:
            pass

        self._popup.move(global_pos)
        self._popup.show()

    def on_filter_selected(self, key):
        self.current_filter = key
        self._refresh_filter_button_text()
        self.refresh_records()

    # =====================================================
    # DATE FILTER
    # =====================================================

    def on_date_changed(self, qdate):
        self.selected_date_filter = qdate
        self.clear_date_btn.show()
        self.refresh_records()

    def clear_date_filter(self):
        self.selected_date_filter = None
        self.clear_date_btn.hide()
        self.refresh_records()

    def _event_matches_date(self, event, qdate):
        d = event.get("date")
        if isinstance(d, datetime):
            return (
                d.year == qdate.year()
                and d.month == qdate.month()
                and d.day == qdate.day()
            )
        if isinstance(d, date):
            return (
                d.year == qdate.year()
                and d.month == qdate.month()
                and d.day == qdate.day()
            )
        return False

    # =====================================================
    # APPLY STYLESHEET
    # =====================================================

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""

        QWidget#eventsWindow {{
            background-color: {c['bg_main']};
            font-family: "Vazirmatn";
            color: {c['text_main']};
        }}

        QLabel#title {{
            color: {c['text_main']};
            font-size: 21px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#subtitle {{
            color: {c['text_dim']};
            font-size: 11px;
            background: transparent;
        }}

        QPushButton#backButton {{
            background-color: {c['bg_card']};
            color: {c['accent']};
            border: 1px solid {c['border']};
            border-radius: 21px;
            font-size: 22px;
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
            border-radius: 20px;
        }}

        QLabel#filterLabel {{
            color: {c['text_main']};
            font-size: 12px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding-right: 4px;
        }}

        /* ═══ دکمه دراپ‌داون فیلتر ═══ */
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

        /* ═══ دکمه پاک کردن تاریخ ═══ */
        QPushButton#clearDateBtn {{
            background-color: {c['danger_bg']};
            color: {c['danger']};
            border: 1px solid {c['border']};
            border-radius: 15px;
            font-size: 14px;
            font-weight: 800;
            padding: 0px;
        }}

        QPushButton#clearDateBtn:hover {{
            background-color: {c['danger']};
            color: white;
            border-color: {c['danger']};
        }}

        /* ═══ دکمه تقویم (PersianDateButton) ═══ */
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

        QPushButton#persianDateButton:hover {{
            color: {c['accent']};
        }}

        /* ═══ بقیه ═══ */
        QFrame#recordsBox {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 20px;
        }}

        QLabel#sectionTitle {{
            color: {c['text_main']};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            border: none;
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
            border: none;
        }}

        QFrame#recordCard {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 16px;
        }}

        QFrame#recordCard:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['accent']};
        }}

        QFrame#recordCard QLabel {{
            background: transparent;
            border: none;
        }}

        QLabel#recordTitle {{
            color: {c['text_main']};
            font-size: 14px;
            font-weight: 700;
        }}

        QLabel#recordInfo {{
            color: {c['text_dim']};
            font-size: 12px;
        }}

        QLabel#recordDate {{
            color: {c['text_dim']};
            font-size: 11px;
        }}

        QLabel#categoryBadge {{
            color: {c['accent']};
            background-color: {c['accent_light']};
            border: none;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#emptyLabel {{
            color: {c['text_dim']};
            font-size: 14px;
            padding: 40px;
            background: transparent;
        }}

        """)

    # =====================================================
    # LOAD EVENTS FROM DATABASE
    # =====================================================

    def load_events(self):
        self.all_events = []

        if not self.complex_id:
            self.refresh_records()
            return

        is_owner = self.role in ("owner", "both")
        mid = self.member_id

        try:
            # ─── Payments ───
            if is_owner:
                payments = self.db.fetch_all(
                    """
                    SELECT p.paymentId, p.amount, p.paymentType, p.paymentDate,
                           p.description, u.name
                    FROM payments p
                    INNER JOIN complex_members cm ON cm.memberId = p.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s
                    ORDER BY p.paymentDate DESC LIMIT 50
                    """,
                    (self.complex_id,)
                )
            else:
                payments = self.db.fetch_all(
                    """
                    SELECT p.paymentId, p.amount, p.paymentType, p.paymentDate,
                           p.description, u.name
                    FROM payments p
                    INNER JOIN complex_members cm ON cm.memberId = p.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s AND p.memberId = %s
                    ORDER BY p.paymentDate DESC LIMIT 50
                    """,
                    (self.complex_id, mid)
                )

            payment_type_map = {
                "salary": tr("payment_salary"),
                "job": tr("payment_job"),
                "bonus": tr("payment_bonus"),
                "advance": tr("payment_advance"),
                "other": tr("payment_other"),
            }

            for p in payments or []:
                ptype = payment_type_map.get(p["paymentType"], tr("salary_type_pay"))
                desc = p.get("description") or f"{format_money(p['amount'])} {tr('toman')}"
                self.all_events.append({
                    "type": f"{ptype} — {p.get('name') or '—'}",
                    "category": "payment",
                    "description": desc,
                    "date": p["paymentDate"]
                })

            # ─── Attendance ───
            if is_owner:
                attendances = self.db.fetch_all(
                    """
                    SELECT a.attendanceId, a.workDate, a.checkIn, a.checkOut,
                           a.approvalStatus, u.name
                    FROM attendance a
                    INNER JOIN complex_members cm ON cm.memberId = a.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s
                      AND a.approvalStatus IN ('approved', 'rejected')
                    ORDER BY a.workDate DESC LIMIT 50
                    """,
                    (self.complex_id,)
                )
            else:
                attendances = self.db.fetch_all(
                    """
                    SELECT a.attendanceId, a.workDate, a.checkIn, a.checkOut,
                           a.approvalStatus, u.name
                    FROM attendance a
                    INNER JOIN complex_members cm ON cm.memberId = a.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s AND a.memberId = %s
                      AND a.approvalStatus IN ('approved', 'rejected')
                    ORDER BY a.workDate DESC LIMIT 50
                    """,
                    (self.complex_id, mid)
                )

            for a in attendances or []:
                if a["approvalStatus"] == "approved":
                    status_text = tr("approved_msg")
                else:
                    status_text = tr("rejected_msg")

                work_date = a["workDate"]
                date_str = str(work_date) if work_date else "-"

                self.all_events.append({
                    "type": f"{status_text} — {a.get('name') or '—'}",
                    "category": "attendance",
                    "description": f"{tr('date')}: {date_str}",
                    "date": a["workDate"]
                })

            # ─── Leaves ───
            if is_owner:
                leaves = self.db.fetch_all(
                    """
                    SELECT l.leaveId, l.startDate, l.endDate, l.leaveType,
                           l.status, l.reason, u.name
                    FROM leaves l
                    INNER JOIN complex_members cm ON cm.memberId = l.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s
                    ORDER BY l.createdDate DESC LIMIT 50
                    """,
                    (self.complex_id,)
                )
            else:
                leaves = self.db.fetch_all(
                    """
                    SELECT l.leaveId, l.startDate, l.endDate, l.leaveType,
                           l.status, l.reason, u.name
                    FROM leaves l
                    INNER JOIN complex_members cm ON cm.memberId = l.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s AND l.memberId = %s
                    ORDER BY l.createdDate DESC LIMIT 50
                    """,
                    (self.complex_id, mid)
                )

            for l in leaves or []:
                status_text = {
                    "approved": tr("approved"),
                    "rejected": tr("rejected"),
                    "pending": tr("pending"),
                }.get(l["status"], l["status"] or "-")

                desc = f"{l['startDate']} → {l['endDate']}"
                if l.get("reason"):
                    desc += f"\n{l['reason']}"

                self.all_events.append({
                    "type": f"{tr('filter_leaves')} ({status_text}) — {l.get('name') or '—'}",
                    "category": "leave",
                    "description": desc,
                    "date": l["startDate"]
                })

            # ─── Loans ───
            if is_owner:
                loans = self.db.fetch_all(
                    """
                    SELECT lo.loanId, lo.totalAmount, lo.installmentCount,
                           lo.startDate, lo.status, u.name
                    FROM loans lo
                    INNER JOIN complex_members cm ON cm.memberId = lo.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s
                    ORDER BY lo.createdDate DESC LIMIT 50
                    """,
                    (self.complex_id,)
                )
            else:
                loans = self.db.fetch_all(
                    """
                    SELECT lo.loanId, lo.totalAmount, lo.installmentCount,
                           lo.startDate, lo.status, u.name
                    FROM loans lo
                    INNER JOIN complex_members cm ON cm.memberId = lo.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s AND lo.memberId = %s
                    ORDER BY lo.createdDate DESC LIMIT 50
                    """,
                    (self.complex_id, mid)
                )

            for lo in loans or []:
                desc = f"{format_money(lo['totalAmount'])} {tr('toman')} — {lo['installmentCount']}x"
                self.all_events.append({
                    "type": f"{tr('filter_loans')} — {lo.get('name') or '—'}",
                    "category": "loan",
                    "description": desc,
                    "date": lo["startDate"]
                })

            # ─── Bonuses ───
            if is_owner:
                bonuses = self.db.fetch_all(
                    """
                    SELECT b.bonusId, b.amount, b.title, b.bonusDate, u.name
                    FROM bonuses b
                    INNER JOIN complex_members cm ON cm.memberId = b.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s
                    ORDER BY b.bonusDate DESC LIMIT 30
                    """,
                    (self.complex_id,)
                )
            else:
                bonuses = self.db.fetch_all(
                    """
                    SELECT b.bonusId, b.amount, b.title, b.bonusDate, u.name
                    FROM bonuses b
                    INNER JOIN complex_members cm ON cm.memberId = b.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s AND b.memberId = %s
                    ORDER BY b.bonusDate DESC LIMIT 30
                    """,
                    (self.complex_id, mid)
                )

            for b in bonuses or []:
                self.all_events.append({
                    "type": f"{tr('tab_bonuses')} — {b.get('name') or '—'}",
                    "category": "other",
                    "description": f"{b.get('title') or '—'} • {format_money(b['amount'])} {tr('toman')}",
                    "date": b["bonusDate"]
                })

            # ─── Deductions ───
            if is_owner:
                deductions = self.db.fetch_all(
                    """
                    SELECT d.deductionId, d.amount, d.title, d.deductionDate, u.name
                    FROM deductions d
                    INNER JOIN complex_members cm ON cm.memberId = d.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s
                    ORDER BY d.deductionDate DESC LIMIT 30
                    """,
                    (self.complex_id,)
                )
            else:
                deductions = self.db.fetch_all(
                    """
                    SELECT d.deductionId, d.amount, d.title, d.deductionDate, u.name
                    FROM deductions d
                    INNER JOIN complex_members cm ON cm.memberId = d.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s AND d.memberId = %s
                    ORDER BY d.deductionDate DESC LIMIT 30
                    """,
                    (self.complex_id, mid)
                )

            for d in deductions or []:
                self.all_events.append({
                    "type": f"{tr('tab_deductions')} — {d.get('name') or '—'}",
                    "category": "other",
                    "description": f"{d.get('title') or '—'} • {format_money(d['amount'])} {tr('toman')}",
                    "date": d["deductionDate"]
                })

            # ─── Sort ───
            def sort_key(e):
                d = e.get("date")
                if isinstance(d, datetime):
                    return d
                if isinstance(d, date):
                    return datetime(d.year, d.month, d.day)
                return datetime(1900, 1, 1)

            self.all_events.sort(key=sort_key, reverse=True)

        except Exception as e:
            print("LOAD EVENTS ERROR:", e)

        self.refresh_records()

    # =====================================================
    # REFRESH RECORDS
    # =====================================================

    def refresh_records(self):

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        filtered = self.all_events

        # فیلتر دسته‌بندی
        if self.current_filter != "all":
            filtered = [
                e for e in filtered if e["category"] == self.current_filter
            ]

        # فیلتر تاریخ
        if self.selected_date_filter is not None:
            filtered = [
                e for e in filtered
                if self._event_matches_date(e, self.selected_date_filter)
            ]

        if not filtered:
            empty_label = QLabel(tr("no_records"))
            empty_label.setObjectName("emptyLabel")
            empty_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            self.scroll_layout.addStretch()
            return

        for record in filtered:
            self.add_record(record)

        self.scroll_layout.addStretch()

    # =====================================================
    # ADD RECORD
    # =====================================================

    def add_record(self, record):

        card = QFrame()
        card.setObjectName("recordCard")
        card.setAttribute(Qt.WA_StyledBackground, True)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(15)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        title_label = QLabel(record["type"])
        title_label.setObjectName("recordTitle")

        info_label = QLabel(record["description"])
        info_label.setObjectName("recordInfo")
        info_label.setWordWrap(True)

        date_str = jalali_string_from_date(record["date"])
        date_label = QLabel(date_str)
        date_label.setObjectName("recordDate")

        text_layout.addWidget(title_label)
        text_layout.addWidget(info_label)
        text_layout.addWidget(date_label)

        card_layout.addLayout(text_layout)
        card_layout.addStretch()

        cat_map = {
            "payment": tr("filter_payments"),
            "attendance": tr("filter_attendance"),
            "leave": tr("filter_leaves"),
            "loan": tr("filter_loans"),
            "other": tr("filter_others"),
        }
        cat_text = cat_map.get(record["category"], "-")

        badge = QLabel(cat_text)
        badge.setObjectName("categoryBadge")
        badge.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(badge)

        self.scroll_layout.addWidget(card)

    # =====================================================
    # BACK
    # =====================================================

    def go_back(self):
        self.close()
        if self.parent_window:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()