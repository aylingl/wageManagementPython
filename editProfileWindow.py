import os

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QLineEdit, QScrollArea, QScrollBar, QDialog,
    QGridLayout
)

from PySide6.QtCore import (
    Qt, QTimer, QDate, QPoint, QSize, QRectF, Signal
)
from PySide6.QtGui import (
    QPixmap, QPainter, QPainterPath, QColor, QRegion, QGuiApplication
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
        self.setFixedWidth(10)
        self.setStyleSheet("QScrollBar {background: transparent;border: none;margin: 0px;}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = theme_manager.colors()

        track_width = 5
        track_x = (self.width() - track_width) / 2
        track_top = 4
        track_bottom = self.height() - 4
        track_height = track_bottom - track_top

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(c["bg_input"]))
        painter.drawRoundedRect(int(track_x), int(track_top), track_width, int(track_height), track_width/2, track_width/2)

        minimum = self.minimum()
        maximum = self.maximum()
        page_step = self.pageStep()
        if maximum <= minimum:
            return

        groove_top = 4
        groove_bottom = self.height() - 4
        groove_height = groove_bottom - groove_top
        total_range = maximum - minimum + page_step
        handle_height = int(groove_height * page_step / total_range)
        handle_height = max(36, handle_height)
        handle_height = min(handle_height, groove_height)
        available_space = groove_height - handle_height

        if maximum == minimum:
            handle_y = groove_top
        else:
            value_ratio = (self.value() - minimum) / (maximum - minimum)
            handle_y = groove_top + available_space * value_ratio

        handle_width = 7
        handle_x = (self.width() - handle_width) / 2
        painter.setBrush(QColor(c["accent"]))
        painter.drawRoundedRect(int(handle_x), int(handle_y), handle_width, int(handle_height), handle_width/2, handle_width/2)

# =========================================================
# JALALI HELPERS
# =========================================================

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (355666 + (365*gy) + ((gy2+3)//4) - ((gy2+99)//100) + ((gy2+399)//400) + gd + g_d_m[gm-1])
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
    days = (-355668 + (365*jy) + ((jy//33)*8) + (((jy%33)+3)//4) + jd + ((jm-1)*31 if jm<7 else ((jm-7)*30)+186))
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

MONTH_NAMES_FA = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
WEEKDAY_SHORT_FA = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
MONTH_NAMES_EN = ["Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar", "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"]
WEEKDAY_SHORT_EN = ["Sa", "Su", "Mo", "Tu", "We", "Th", "Fr"]
MONTH_NAMES_AR = ["فَروَردین", "اُردیبهشت", "خُرداد", "تیر", "مُرداد", "شهریور", "مِهر", "آبان", "آذَر", "دی", "بَهمَن", "اسفَند"]
WEEKDAY_SHORT_AR = ["س", "ح", "ن", "ث", "ر", "خ", "ج"]

def get_month_names():
    lang = get_language()
    if lang == "en":
        return MONTH_NAMES_EN
    if lang == "ar":
        return MONTH_NAMES_AR
    return MONTH_NAMES_FA

def get_weekdays_short():
    lang = get_language()
    if lang == "en":
        return WEEKDAY_SHORT_EN
    if lang == "ar":
        return WEEKDAY_SHORT_AR
    return WEEKDAY_SHORT_FA

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
        jy, jm, jd = gregorian_to_jalali(current_qdate.year(), current_qdate.month(), current_qdate.day())
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

        self._radius = 16
        self._margin = 6
        self.setFixedSize(280, 340)

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
            shadow_color = QColor(0, 0, 0, 3 + (6 - i) * 2)
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
        path.addRoundedRect(QRectF(self.rect()), self._radius+self._margin, self._radius+self._margin)
        polygon = path.toFillPolygon().toPolygon()
        self.setMask(QRegion(polygon))

    def build_ui(self):
        c = theme_manager.colors()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(self._margin+12, self._margin+12, self._margin+12, self._margin+12)
        layout.setSpacing(6)

        # Year row
        year_row = QHBoxLayout()
        year_row.setSpacing(4)

        prev_year = QPushButton("‹‹")
        prev_year.setObjectName("calNavBtn")
        prev_year.setFixedSize(32, 32)
        prev_year.setCursor(Qt.PointingHandCursor)
        prev_year.clicked.connect(self.go_prev_year)

        self.year_label = QLabel()
        self.year_label.setObjectName("calYearLabel")
        self.year_label.setAlignment(Qt.AlignCenter)

        next_year = QPushButton("››")
        next_year.setObjectName("calNavBtn")
        next_year.setFixedSize(32, 32)
        next_year.setCursor(Qt.PointingHandCursor)
        next_year.clicked.connect(self.go_next_year)

        year_row.addWidget(prev_year)
        year_row.addWidget(self.year_label, 1)
        year_row.addWidget(next_year)
        layout.addLayout(year_row)

        # Month row
        month_row = QHBoxLayout()
        month_row.setSpacing(4)

        prev_month = QPushButton("‹")
        prev_month.setObjectName("calNavBtn")
        prev_month.setFixedSize(32, 32)
        prev_month.setCursor(Qt.PointingHandCursor)
        prev_month.clicked.connect(self.go_prev_month)

        self.month_label = QLabel()
        self.month_label.setObjectName("calMonthLabel")
        self.month_label.setAlignment(Qt.AlignCenter)

        next_month = QPushButton("›")
        next_month.setObjectName("calNavBtn")
        next_month.setFixedSize(32, 32)
        next_month.setCursor(Qt.PointingHandCursor)
        next_month.clicked.connect(self.go_next_month)

        month_row.addWidget(prev_month)
        month_row.addWidget(self.month_label, 1)
        month_row.addWidget(next_month)
        layout.addLayout(month_row)

        # Weekdays
        wd_layout = QHBoxLayout()
        wd_layout.setSpacing(1)
        for name in get_weekdays_short():
            lbl = QLabel(name)
            lbl.setObjectName("calWeekday")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(22)
            wd_layout.addWidget(lbl, 1)
        layout.addLayout(wd_layout)

        # Days grid
        self.days_layout = QGridLayout()
        self.days_layout.setSpacing(2)
        for col in range(7):
            self.days_layout.setColumnStretch(col, 1)
        layout.addLayout(self.days_layout, 1)

        # Today button
        today_btn = QPushButton("●")
        today_btn.setObjectName("calTodayBtn")
        today_btn.setFixedHeight(28)
        today_btn.setCursor(Qt.PointingHandCursor)
        today_btn.clicked.connect(self.pick_today)

        today_row = QHBoxLayout()
        today_row.addStretch()
        today_row.addWidget(today_btn)
        today_row.addStretch()
        layout.addLayout(today_row)

        self.setStyleSheet(f"""
            QLabel#calYearLabel {{color: {c['text_main']};font-size: 14px;font-weight: 800;background: transparent;}}
            QLabel#calMonthLabel {{color: {c['accent']};font-size: 12px;font-weight: 700;background: transparent;}}
            QPushButton#calNavBtn {{background-color: {c['accent_light']};color: {c['accent']};border: 1px solid {c['border_hover']};border-radius: 16px;font-size: 14px;font-weight: 700;padding: 0px;}}
            QPushButton#calNavBtn:hover {{background-color: {c['bg_hover']};}}
            QLabel#calWeekday {{color: {c['text_dim']};font-size: 10px;font-weight: 700;background: transparent;}}
            QPushButton#calDayBtn {{background-color: transparent;color: {c['text_main']};border: none;border-radius: 10px;font-size: 11px;font-weight: 600;min-height: 26px;}}
            QPushButton#calDayBtn:hover {{background-color: {c['bg_hover']};color: {c['accent']};}}
            QPushButton#calDayBtn[today="true"] {{border: 2px solid {c['accent']};color: {c['accent']};}}
            QPushButton#calDayBtn[selected="true"] {{background-color: {c['accent']};color: white;border: none;}}
            QPushButton#calTodayBtn {{background-color: {c['accent_light']};color: {c['accent']};border: 1px solid {c['border_hover']};border-radius: 14px;font-size: 12px;font-weight: 700;padding: 0 22px;}}
            QPushButton#calTodayBtn:hover {{background-color: {c['bg_hover']};}}
        """)

        self.refresh_labels()

    def refresh_labels(self):
        self.year_label.setText(str(self.view_year))
        months = get_month_names()
        self.month_label.setText(months[self.view_month - 1])

    def refresh_grid(self):
        while self.days_layout.count():
            item = self.days_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.refresh_labels()

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

    def go_prev_year(self):
        self.view_year -= 1
        self.refresh_grid()

    def go_next_year(self):
        self.view_year += 1
        self.refresh_grid()

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

    def pick_today(self):
        today = QDate.currentDate()
        jy, jm, jd = gregorian_to_jalali(today.year(), today.month(), today.day())
        self.pick_day(jd)

# =========================================================
# PERSIAN DATE FRAME
# =========================================================

class PersianDateFrame(QFrame):
    dateChanged = Signal(QDate)

    def __init__(self, parent=None, initial_jalali_str="1380/01/01"):
        super().__init__(parent)

        self._jalali_str = initial_jalali_str

        self.setObjectName("persianDateFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(42)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 12, 0)
        layout.setSpacing(6)

        self.icon_label = QLabel("📅")
        self.icon_label.setObjectName("dateIconLabel")
        self.icon_label.setFixedSize(28, 28)
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
        self.date_btn.setText(self._jalali_str)

    def jalali_string(self):
        return self._jalali_str

    def set_jalali_string(self, text):
        self._jalali_str = text
        self._refresh_text()

    def _open_dialog(self):
        current_qdate = QDate.currentDate()
        try:
            parts = self._jalali_str.replace("-", "/").split("/")
            jy = int(parts[0]); jm = int(parts[1]); jd = int(parts[2])
            gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
            current_qdate = QDate(gy, gm, gd)
        except Exception:
            pass

        self._popup = PersianCalendarPopup(self, current_qdate)
        self._popup.dateSelected.connect(self._on_date_selected)

        # ─── محاسبه‌ی موقعیت هوشمند ───
        popup_w = self._popup.width()
        popup_h = self._popup.height()

        # موقعیت پیش‌فرض (زیر فیلد)
        global_pos = self.mapToGlobal(QPoint(0, self.height() + 4))

        # صفحه‌ای که پنجره توشه
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            # اگه پایین صفحه جا نمیشه، بالا باز کن
            if global_pos.y() + popup_h > screen_geo.bottom():
                global_pos.setY(self.mapToGlobal(QPoint(0, 0)).y() - popup_h - 4)
            # اگه چپ یا راست صفحه میزنه بیرون، تنظیم کن
            if global_pos.x() + popup_w > screen_geo.right():
                global_pos.setX(screen_geo.right() - popup_w - 8)
            if global_pos.x() < screen_geo.left():
                global_pos.setX(screen_geo.left() + 8)

        self._popup.move(global_pos)
        self._popup.show()

    def _on_date_selected(self, qdate):
        jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
        new_str = f"{jy:04d}/{jm:02d}/{jd:02d}"
        if new_str == self._jalali_str:
            return
        self._jalali_str = new_str
        self._refresh_text()
        self.dateChanged.emit(qdate)

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
# EDIT PROFILE WINDOW
# =========================================================

class EditProfileWindow(QWidget):

    def __init__(self, parent_window=None, phone_number=None, username="", national_code="", birth_date=None, avatar="men.png"):
        super().__init__()

        self.parent_window = parent_window
        self.phone_number = phone_number
        self.username = username
        self.national_code = national_code
        self.avatar = avatar

        self.user_id = None
        self.birth_date_string = "1380/01/01"

        self.load_user_information()

        self.setWindowTitle(tr("edit_profile_title"))
        self.setMinimumSize(450, 400)
        self.resize(750, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("editProfileWindow")

        self.setup_ui()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("edit_profile_title"))
        QTimer.singleShot(0, self._rebuild)

    def _rebuild(self):
        current_values = {
            "name": self.name_input.text() if hasattr(self, "name_input") else self.username,
            "national": self.national_input.text() if hasattr(self, "national_input") else self.national_code,
            "birth": self.birth_date_frame.jalali_string() if hasattr(self, "birth_date_frame") else self.birth_date_string,
        }

        old = self.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

        self.setup_ui()

        if hasattr(self, "name_input"):
            self.name_input.setText(current_values["name"])
        if hasattr(self, "national_input"):
            self.national_input.setText(current_values["national"])
        if hasattr(self, "birth_date_frame"):
            self.birth_date_frame.set_jalali_string(current_values["birth"])

    def load_user_information(self):
        try:
            db = Database()
            user = db.fetch_one(
                "SELECT userId, name, nationalId, birthDate, imageBase64 FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if user:
                self.user_id = user["userId"]
                if user.get("name"):
                    self.username = user["name"]
                if user.get("nationalId") is not None:
                    self.national_code = str(user["nationalId"])
                if user.get("birthDate"):
                    self.birth_date_string = str(user["birthDate"])
                if user.get("imageBase64"):
                    self.avatar = user["imageBase64"]
        except Exception as e:
            print("Error loading user information:", e)

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 18, 22, 18)
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

        title = QLabel(tr("edit_profile_title"))
        title.setObjectName("title")

        subtitle = QLabel(tr("edit_profile_subtitle"))
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

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
        content_layout.setContentsMargins(0, 0, 10, 0)
        content_layout.setSpacing(12)

        scroll.setWidget(content)

        # PROFILE CARD
        profile_box = QFrame()
        profile_box.setObjectName("profileBox")
        profile_box.setAttribute(Qt.WA_StyledBackground, True)

        profile_layout = QVBoxLayout(profile_box)
        profile_layout.setContentsMargins(16, 14, 16, 14)
        profile_layout.setSpacing(10)

        profile_title = QLabel(tr("edit_profile_card"))
        profile_title.setObjectName("sectionTitle")
        profile_layout.addWidget(profile_title)

        avatar_layout = QHBoxLayout()
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.setSpacing(12)

        self.avatar_label = QLabel()
        self.avatar_label.setObjectName("avatar")
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.load_avatar()

        avatar_layout.addWidget(self.avatar_label)

        change_avatar_button = QPushButton(tr("edit_change_avatar"))
        change_avatar_button.setObjectName("changeAvatarButton")
        change_avatar_button.setCursor(Qt.PointingHandCursor)
        change_avatar_button.setAttribute(Qt.WA_StyledBackground, True)
        change_avatar_button.setFixedHeight(36)
        change_avatar_button.clicked.connect(self.change_avatar)

        avatar_layout.addWidget(change_avatar_button)
        avatar_layout.addStretch()

        profile_layout.addLayout(avatar_layout)
        content_layout.addWidget(profile_box)

        # INFO CARD
        information_box = QFrame()
        information_box.setObjectName("profileBox")
        information_box.setAttribute(Qt.WA_StyledBackground, True)

        information_layout = QVBoxLayout(information_box)
        information_layout.setContentsMargins(16, 14, 16, 14)
        information_layout.setSpacing(6)

        information_title = QLabel(tr("edit_personal_info"))
        information_title.setObjectName("sectionTitle")
        information_layout.addWidget(information_title)
        information_layout.addSpacing(4)

        # NAME
        name_label = QLabel(tr("edit_name_label"))
        name_label.setObjectName("fieldLabel")

        self.name_input = QLineEdit()
        self.name_input.setObjectName("profileInput")
        self.name_input.setText(self.username)
        self.name_input.setPlaceholderText(tr("edit_name_ph"))
        self.name_input.setFixedHeight(40)
        self.name_input.textChanged.connect(lambda: self.clear_field_error(self.name_error))

        information_layout.addWidget(name_label)
        information_layout.addWidget(self.name_input)

        self.name_error = QLabel()
        self.name_error.setObjectName("fieldError")
        self.name_error.setAlignment(Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter)
        self.name_error.setFixedHeight(16)
        self.name_error.hide()
        information_layout.addWidget(self.name_error)

        # PHONE
        phone_label = QLabel(tr("edit_phone_section"))
        phone_label.setObjectName("fieldLabel")

        phone_button = QPushButton()
        phone_button.setObjectName("phoneButton")
        phone_button.setCursor(Qt.PointingHandCursor)
        phone_button.setAttribute(Qt.WA_StyledBackground, True)
        phone_button.setFixedHeight(50)

        phone_layout = QHBoxLayout(phone_button)
        phone_layout.setContentsMargins(12, 6, 12, 6)
        phone_layout.setSpacing(8)

        phone_text_layout = QVBoxLayout()
        phone_text_layout.setSpacing(1)

        self.phone_value = QLabel(self.phone_number or "—")
        self.phone_value.setObjectName("phoneValue")

        phone_hint = QLabel(tr("edit_phone_hint"))
        phone_hint.setObjectName("phoneHint")

        phone_text_layout.addWidget(self.phone_value)
        phone_text_layout.addWidget(phone_hint)

        phone_arrow = QLabel("‹")
        phone_arrow.setObjectName("phoneArrow")
        phone_arrow.setFixedWidth(20)
        phone_arrow.setAlignment(Qt.AlignCenter)

        phone_layout.addLayout(phone_text_layout, 1)
        phone_layout.addWidget(phone_arrow)

        phone_button.clicked.connect(self.change_phone)

        information_layout.addWidget(phone_label)
        information_layout.addWidget(phone_button)

        # NATIONAL
        national_label = QLabel(tr("edit_national_label"))
        national_label.setObjectName("fieldLabel")

        self.national_input = QLineEdit()
        self.national_input.setObjectName("profileInput")
        self.national_input.setText(self.national_code)
        self.national_input.setPlaceholderText(tr("edit_national_ph"))
        self.national_input.setFixedHeight(40)
        self.national_input.setMaxLength(10)
        self.national_input.setLayoutDirection(Qt.LeftToRight)
        self.national_input.textChanged.connect(lambda: self.clear_field_error(self.national_error))

        information_layout.addWidget(national_label)
        information_layout.addWidget(self.national_input)

        self.national_error = QLabel()
        self.national_error.setObjectName("fieldError")
        self.national_error.setAlignment(Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter)
        self.national_error.setFixedHeight(16)
        self.national_error.hide()
        information_layout.addWidget(self.national_error)

        # BIRTH
        birth_label = QLabel(tr("edit_birth_label"))
        birth_label.setObjectName("fieldLabel")

        self.birth_date_frame = PersianDateFrame(initial_jalali_str=self.birth_date_string)

        information_layout.addWidget(birth_label)
        information_layout.addWidget(self.birth_date_frame)

        content_layout.addWidget(information_box)
        content_layout.addStretch()

        main_layout.addWidget(scroll, 1)

        # BUTTONS
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        cancel_button = QPushButton(tr("cancel"))
        cancel_button.setObjectName("cancelButton")
        cancel_button.setFixedHeight(44)
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setAttribute(Qt.WA_StyledBackground, True)
        cancel_button.clicked.connect(self.close)

        save_button = QPushButton(tr("edit_save_changes"))
        save_button.setObjectName("saveButton")
        save_button.setFixedHeight(44)
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setAttribute(Qt.WA_StyledBackground, True)
        save_button.clicked.connect(self.save_profile)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

        self.apply_stylesheet()

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""
        QWidget#editProfileWindow {{
            background-color: {c['bg_main']};
            font-family: Vazirmatn;
            color: {c['text_main']};
        }}
        QLabel#title {{
            color: {c['text_main']};
            font-size: 18px;
            font-weight: 700;
            background: transparent;
            border: none;
        }}
        QLabel#subtitle {{
            color: {c['text_dim']};
            font-size: 10px;
            background: transparent;
            border: none;
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
        QScrollArea {{
            background: transparent;
            border: none;
        }}
        QScrollArea::viewport {{
            background: transparent;
            border: none;
        }}
        QWidget#scrollContent {{
            background: transparent;
        }}
        QFrame#profileBox {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}
        QLabel#sectionTitle {{
            color: {c['text_main']};
            background-color: transparent;
            border: none;
            font-size: 13px;
            font-weight: 700;
        }}
        QLabel#avatar {{
            background-color: {c['accent_light']};
            border: 3px solid {c['border_hover']};
            border-radius: 40px;
        }}
        QPushButton#changeAvatarButton {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border: 1px solid {c['border_hover']};
            border-radius: 18px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 600;
        }}
        QPushButton#changeAvatarButton:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['accent']};
        }}
        QLabel#fieldLabel {{
            color: {c['text_dim']};
            background-color: transparent;
            border: none;
            font-size: 11px;
            font-weight: 600;
            padding: 4px 0px 2px 0px;
        }}
        QLabel#fieldError {{
            color: {c['danger']};
            background-color: transparent;
            border: none;
            font-size: 10px;
            font-weight: 600;
            padding: 0px;
            margin: 0px;
        }}
        QLineEdit#profileInput {{
            background-color: {c['bg_input']};
            color: {c['text_main']};
            border: 1px solid {c['border']};
            border-radius: 20px;
            padding: 0 14px;
            font-size: 12px;
            min-height: 40px;
        }}
        QLineEdit#profileInput:hover {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border_hover']};
        }}
        QLineEdit#profileInput:focus {{
            background-color: {c['bg_card']};
            border: 2px solid {c['accent']};
        }}
        QFrame#persianDateFrame {{
            background-color: {c['bg_input']};
            border: 1px solid {c['border']};
            border-radius: 20px;
        }}
        QFrame#persianDateFrame:hover {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border_hover']};
        }}
        QLabel#dateIconLabel {{
            background-color: {c['accent_light']};
            border: none;
            border-radius: 10px;
            font-size: 14px;
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
        QPushButton#phoneButton {{
            background-color: {c['bg_input']};
            color: {c['text_main']};
            border: 1px solid {c['border']};
            border-radius: 20px;
            text-align: right;
        }}
        QPushButton#phoneButton:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['border_hover']};
        }}
        QLabel#phoneValue {{
            color: {c['text_main']};
            background: transparent;
            border: none;
            font-size: 12px;
            font-weight: 600;
        }}
        QLabel#phoneHint {{
            color: {c['text_dim']};
            background: transparent;
            border: none;
            font-size: 9px;
        }}
        QLabel#phoneArrow {{
            color: {c['text_dim']};
            background: transparent;
            border: none;
            font-size: 20px;
        }}
        QPushButton#cancelButton {{
            background-color: {c['bg_card']};
            color: {c['text_dim']};
            border: 1px solid {c['border']};
            border-radius: 22px;
            padding: 10px 22px;
            font-size: 12px;
            font-weight: 600;
            min-height: 44px;
        }}
        QPushButton#cancelButton:hover {{
            background-color: {c['bg_hover']};
            color: {c['accent']};
            border-color: {c['border_hover']};
        }}
        QPushButton#saveButton {{
            background-color: {c['accent']};
            color: white;
            border: none;
            border-radius: 22px;
            padding: 10px 26px;
            font-size: 12px;
            font-weight: 700;
            min-height: 44px;
        }}
        QPushButton#saveButton:hover {{
            background-color: {c['accent_hover']};
        }}
        """)

    def show_field_error(self, label, message):
        label.setText(message)
        label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter)
        label.show()

    def clear_field_error(self, label):
        label.clear()
        label.hide()

    def is_valid_national_id(self, national_id):
        if len(national_id) != 10:
            return False
        if not national_id.isdigit():
            return False
        if len(set(national_id)) == 1:
            return False
        digits = [int(d) for d in national_id]
        first_nine = digits[:9]
        control_digit = digits[9]
        total = 0
        for i in range(9):
            total += first_nine[i] * (10 - i)
        remainder = total % 11
        calculated = remainder if remainder < 2 else 11 - remainder
        return control_digit == calculated

    def load_avatar(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        avatar_path = os.path.join(base_dir, "avatars", self.avatar)
        if os.path.exists(avatar_path):
            pixmap = QPixmap(avatar_path)
            pixmap = pixmap.scaled(74, 74, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.avatar_label.setPixmap(pixmap)
        else:
            self.avatar_label.setText("👤")

    def change_avatar(self):
        from profileSetupWindow import ProfileSetupWindow
        self.profile_setup_window = ProfileSetupWindow(self.phone_number)
        self.profile_setup_window.resize(self.size())
        self.profile_setup_window.move(self.pos())
        self.profile_setup_window.show()
        self.profile_setup_window.raise_()
        self.profile_setup_window.activateWindow()
        self.hide()

    def change_phone(self):
        from main import LoginWindow
        self.login_window = LoginWindow(change_phone=True, parent_profile=self)
        self.login_window.resize(self.size())
        self.login_window.move(self.pos())
        self.login_window.show()
        self.login_window.raise_()
        self.login_window.activateWindow()
        self.hide()

    def save_profile(self):
        name = self.name_input.text().strip()
        national_code = self.national_input.text().strip()
        birth_date_string = self.birth_date_frame.jalali_string()

        if not name:
            self.show_field_error(self.name_error, tr("edit_name_empty"))
            self.name_input.setFocus()
            return
        for character in name:
            if character.isdigit():
                self.show_field_error(self.name_error, tr("edit_name_digit_err"))
                self.name_input.setFocus()
                return
        self.clear_field_error(self.name_error)

        if not national_code:
            self.show_field_error(self.national_error, tr("edit_national_empty"))
            self.national_input.setFocus()
            return
        if not national_code.isdigit():
            self.show_field_error(self.national_error, tr("edit_national_digit"))
            self.national_input.setFocus()
            return
        if len(national_code) != 10:
            self.show_field_error(self.national_error, tr("edit_national_10_digit"))
            self.national_input.setFocus()
            return
        if not self.is_valid_national_id(national_code):
            self.show_field_error(self.national_error, tr("national_invalid"))
            self.national_input.setFocus()
            return
        self.clear_field_error(self.national_error)

        try:
            db = Database()
            current_user = db.fetch_one("SELECT userId FROM users WHERE phoneNumber = %s LIMIT 1", (self.phone_number,))
            if not current_user:
                NiceMessageBox.warning(self, tr("error"), tr("edit_user_not_found"))
                return

            user_id = current_user["userId"]
            existing_user = db.fetch_one(
                "SELECT userId FROM users WHERE nationalId = %s AND userId <> %s LIMIT 1",
                (national_code, user_id)
            )
            if existing_user:
                self.show_field_error(self.national_error, tr("edit_national_taken"))
                self.national_input.setFocus()
                return

            db.execute(
                "UPDATE users SET name = %s, nationalId = %s, birthDate = %s WHERE userId = %s",
                (name, national_code, birth_date_string, user_id)
            )

            self.username = name
            self.national_code = national_code
            self.birth_date_string = birth_date_string

            NiceMessageBox.success(self, tr("profile_updated"), tr("profile_updated_msg"))

        except Exception as e:
            print("Error saving profile:", e)
            NiceMessageBox.error(self, tr("error"), tr("edit_error_msg"))