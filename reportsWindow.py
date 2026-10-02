import os
from datetime import datetime, date, timedelta

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QDialog, QGridLayout,
    QComboBox, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect
)

from PySide6.QtCore import (
    Qt, QTimer, QDate, QPoint, QSize
)
from PySide6.QtGui import QPainter, QColor

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

        # Date range filter
        self.date_range = "this_month"

        # Summary data
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

    # =====================================================
    # THEME / LANGUAGE
    # =====================================================

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

    # =====================================================
    # LOAD USER
    # =====================================================

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
    # DATE RANGE
    # =====================================================

    def get_date_range_gregorian(self):
        today = date.today()

        if self.date_range == "today":
            return today, today

        if self.date_range == "this_week":
            start = today - timedelta(days=today.weekday())
            return start, today

        if self.date_range == "this_month":
            start = today.replace(day=1)
            return start, today

        if self.date_range == "last_3_months":
            start = today - timedelta(days=90)
            return start, today

        return today, today

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

        # FILTER BOX
        filter_box = QFrame()
        filter_box.setObjectName("filterBox")
        filter_box.setAttribute(Qt.WA_StyledBackground, True)

        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setContentsMargins(14, 10, 14, 10)
        filter_layout.setSpacing(10)

        filter_lbl = QLabel(tr("filter_report"))
        filter_lbl.setObjectName("filterLabel")

        self.date_combo = RoundedComboBox()
        self.date_combo.setObjectName("filterCombo")
        self.date_combo.setFixedHeight(36)
        self.date_combo.setMinimumWidth(160)
        self.date_combo.setCursor(Qt.PointingHandCursor)
        self.date_combo.addItem(tr("today"), "today")
        self.date_combo.addItem(tr("this_week"), "this_week")
        self.date_combo.addItem(tr("this_month"), "this_month")
        self.date_combo.addItem(tr("last_3_months"), "last_3_months")

        # Set current
        for i in range(self.date_combo.count()):
            if self.date_combo.itemData(i) == self.date_range:
                self.date_combo.setCurrentIndex(i)
                break

        self.date_combo.currentIndexChanged.connect(self.on_date_changed)

        apply_btn = QPushButton(tr("apply_filter"))
        apply_btn.setObjectName("applyBtn")
        apply_btn.setFixedHeight(36)
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setAttribute(Qt.WA_StyledBackground, True)
        apply_btn.clicked.connect(self.calculate_reports)

        filter_layout.addWidget(filter_lbl)
        filter_layout.addWidget(self.date_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(apply_btn)

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

        # ── Summary title ──
        summary_title = QLabel(tr("report_summary"))
        summary_title.setObjectName("sectionTitle")
        content_layout.addWidget(summary_title)

        # ── Summary cards ──
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

        # ── Available reports title ──
        available_title = QLabel(tr("available_reports"))
        available_title.setObjectName("sectionTitle")
        content_layout.addWidget(available_title)

        # ── Report cards ──
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

    # =====================================================
    # SUMMARY CARD
    # =====================================================

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

    # =====================================================
    # REPORT CARD
    # =====================================================

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

    # =====================================================
    # APPLY STYLESHEET
    # =====================================================

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
            font-size: 12px;
            font-weight: 600;
            background: transparent;
            border: none;
        }}

        QComboBox#filterCombo {{
            background-color: {c['bg_input']};
            color: {c['text_main']};
            border: 1px solid {c['border']};
            border-radius: 18px;
            padding: 0 14px;
            font-size: 12px;
            font-weight: 600;
        }}

        QComboBox#filterCombo:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['border_hover']};
        }}

        QComboBox#filterCombo::drop-down {{
            border: none;
            width: 24px;
        }}

        QComboBox#filterCombo::down-arrow {{
            image: none;
            width: 0px;
            height: 0px;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {c['accent']};
            margin-right: 8px;
        }}

        QPushButton#applyBtn {{
            background-color: {c['accent']};
            color: white;
            border: none;
            border-radius: 18px;
            padding: 0 18px;
            font-size: 12px;
            font-weight: 700;
        }}

        QPushButton#applyBtn:hover {{
            background-color: {c['accent_hover']};
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

    # =====================================================
    # DATE CHANGED
    # =====================================================

    def on_date_changed(self, index):
        self.date_range = self.date_combo.itemData(index) or "this_month"
        self.calculate_reports()

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate_reports(self):
        if not self.complex_id:
            return

        start_date, end_date = self.get_date_range_gregorian()

        try:
            # ── Employees ──
            emp = self.db.fetch_one(
                """
                SELECT COUNT(*) AS cnt FROM complex_members
                WHERE complexId = %s AND role IN ('employee', 'both') AND isActive = '1'
                """,
                (self.complex_id,)
            )
            emp_count = int(emp["cnt"]) if emp else 0

            # ── Working hours ──
            hours_row = self.db.fetch_one(
                """
                SELECT COALESCE(SUM(a.workedMinutes), 0) AS total
                FROM attendance a
                INNER JOIN complex_members cm ON cm.memberId = a.memberId
                WHERE cm.complexId = %s
                  AND a.workDate BETWEEN %s AND %s
                  AND a.approvalStatus = 'approved'
                """,
                (self.complex_id, start_date, end_date)
            )
            total_minutes = int(hours_row["total"]) if hours_row else 0
            total_hours = total_minutes // 60

            # ── Payments ──
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

            # ── Tasks done ──
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

            # ── Update UI ──
            self.emp_value.setText(str(emp_count))
            self.hours_value.setText(f"{total_hours} {tr('hours_text')}")
            self.pay_value.setText(f"{format_money(total_payments)} {tr('toman')}")
            self.tasks_value.setText(str(tasks_done))

        except Exception as e:
            print("REPORTS CALC ERROR:", e)

    # =====================================================
    # OPEN REPORT
    # =====================================================

    def open_report(self, report_type):
        if not self.complex_id:
            return

        start_date, end_date = self.get_date_range_gregorian()
        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(500)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        title_map = {
            "attendance": tr("report_attendance"),
            "finance": tr("report_finance"),
            "employees": tr("report_employees"),
            "tasks": tr("report_tasks"),
        }
        dialog.setWindowTitle(title_map.get(report_type, tr("reports_title")))

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet(f"background-color: {c['bg_card']}; border-bottom: 1px solid {c['border']};")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.setSpacing(4)

        h_title = QLabel(title_map.get(report_type, tr("reports_title")))
        h_title.setStyleSheet(f"color: {c['text_main']}; font-size: 16px; font-weight: 800; background: transparent;")

        range_text = f"{start_date} → {end_date}"
        h_sub = QLabel(range_text)
        h_sub.setStyleSheet(f"color: {c['accent']}; font-size: 11px; font-weight: 600; background: transparent;")

        h_layout.addWidget(h_title)
        h_layout.addWidget(h_sub)
        main_layout.addWidget(header)

        # Scroll
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
        content_layout.setContentsMargins(18, 18, 18, 18)
        content_layout.setSpacing(10)

        rows = self.get_report_rows(report_type, start_date, end_date)

        if not rows:
            empty = QLabel(tr("no_records"))
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color: {c['text_dim']}; font-size: 13px; padding: 40px; background: transparent;")
            content_layout.addWidget(empty)
        else:
            for r in rows:
                card = QFrame()
                card.setObjectName("repRow")
                card.setAttribute(Qt.WA_StyledBackground, True)
                card.setStyleSheet(f"""
                    QFrame#repRow {{
                        background-color: {c['bg_card']};
                        border: 1px solid {c['border']};
                        border-radius: 14px;
                    }}
                """)

                rl = QHBoxLayout(card)
                rl.setContentsMargins(14, 10, 14, 10)
                rl.setSpacing(10)

                for key in ["col1", "col2", "col3", "col4"]:
                    if key in r:
                        lbl = QLabel(str(r[key]))
                        if key == "col1":
                            lbl.setStyleSheet(f"color: {c['text_main']}; font-size: 12px; font-weight: 700; background: transparent;")
                        elif key == "col4":
                            lbl.setStyleSheet(f"color: {c['accent']}; font-size: 12px; font-weight: 700; background: transparent;")
                        else:
                            lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 11px; background: transparent;")
                        rl.addWidget(lbl, 1)
                    else:
                        rl.addStretch(1)

                content_layout.addWidget(card)

        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        # Bottom
        bottom = QFrame()
        bottom.setStyleSheet(f"background-color: {c['bg_card']}; border-top: 1px solid {c['border']};")
        b_layout = QHBoxLayout(bottom)
        b_layout.setContentsMargins(20, 12, 20, 12)

        close_btn = QPushButton(tr("close"))
        close_btn.setFixedHeight(40)
        close_btn.setMinimumWidth(130)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 22px;
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

        dialog.setStyleSheet(f"QDialog {{ background-color: {c['bg_main']}; font-family: 'Vazirmatn'; }}")
        dialog.exec()

    # =====================================================
    # GET REPORT ROWS
    # =====================================================

    def get_report_rows(self, report_type, start_date, end_date):
        rows = []

        try:
            if report_type == "attendance":
                data = self.db.fetch_all(
                    """
                    SELECT u.name, a.workDate, a.checkIn, a.checkOut,
                           a.workedMinutes, a.overtimeMinutes
                    FROM attendance a
                    INNER JOIN complex_members cm ON cm.memberId = a.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s
                      AND a.workDate BETWEEN %s AND %s
                      AND a.approvalStatus = 'approved'
                    ORDER BY a.workDate DESC
                    LIMIT 200
                    """,
                    (self.complex_id, start_date, end_date)
                )
                for d in data or []:
                    wm = int(d.get("workedMinutes") or 0)
                    h = wm // 60
                    m = wm % 60
                    ot = int(d.get("overtimeMinutes") or 0)
                    ot_h = ot // 60
                    ot_m = ot % 60
                    rows.append({
                        "col1": d.get("name") or "—",
                        "col2": str(d.get("workDate") or "-"),
                        "col3": f"{h}{tr('hour_short')} {m}{tr('min_short')}",
                        "col4": f"OT {ot_h}{tr('hour_short')} {ot_m}{tr('min_short')}" if ot > 0 else "-",
                    })

            elif report_type == "finance":
                data = self.db.fetch_all(
                    """
                    SELECT u.name, p.amount, p.paymentType, p.paymentDate, p.description
                    FROM payments p
                    INNER JOIN complex_members cm ON cm.memberId = p.memberId
                    INNER JOIN users u ON u.userId = cm.userId
                    WHERE cm.complexId = %s
                      AND DATE(p.paymentDate) BETWEEN %s AND %s
                    ORDER BY p.paymentDate DESC
                    LIMIT 200
                    """,
                    (self.complex_id, start_date, end_date)
                )
                type_map = {
                    "salary": tr("payment_salary"),
                    "job": tr("payment_job"),
                    "bonus": tr("payment_bonus"),
                    "advance": tr("payment_advance"),
                    "other": tr("payment_other"),
                }
                for d in data or []:
                    rows.append({
                        "col1": d.get("name") or "—",
                        "col2": type_map.get(d.get("paymentType"), "-"),
                        "col3": str(d.get("paymentDate") or "-")[:16],
                        "col4": f"{format_money(d.get('amount') or 0)} {tr('toman')}",
                    })

            elif report_type == "employees":
                data = self.db.fetch_all(
                    """
                    SELECT u.name, cm.role, ep.jobTitle, ep.baseSalary
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
                for d in data or []:
                    rows.append({
                        "col1": d.get("name") or "—",
                        "col2": d.get("jobTitle") or tr("no_job"),
                        "col3": tr("employee_role"),
                        "col4": f"{format_money(d.get('baseSalary') or 0)} {tr('toman')}",
                    })

            elif report_type == "tasks":
                data = self.db.fetch_all(
                    """
                    SELECT u.name, j.jobTitle, ej.status, ej.price, ej.assignedDate
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
                status_map = {
                    "pending": tr("cartable_pending"),
                    "inProgress": tr("cartable_in_progress"),
                    "completed": tr("cartable_completed"),
                    "rejected": tr("cartable_rejected"),
                    "cancelled": tr("cartable_cancelled"),
                }
                for d in data or []:
                    rows.append({
                        "col1": d.get("name") or "—",
                        "col2": d.get("jobTitle") or tr("job_no_desc"),
                        "col3": status_map.get(d.get("status"), "-"),
                        "col4": f"{format_money(d.get('price') or 0)} {tr('toman')}",
                    })

        except Exception as e:
            print("GET REPORT ROWS ERROR:", e)

        return rows