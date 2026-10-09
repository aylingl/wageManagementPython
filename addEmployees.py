import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QLineEdit, QCheckBox, QComboBox, QTimeEdit,
    QScrollArea, QScrollBar, QDialog, QListWidget, QListWidgetItem,
    QGraphicsDropShadowEffect
)

from PySide6.QtCore import Qt, QTime, QPoint, QSize, QTimer
from PySide6.QtGui import QPainter, QColor, QPolygon

from database import Database
from signals import signals
from theme import theme_manager
from i18n import tr, set_language, get_language

from hierarchy import (
    role_to_level, set_supervisor_and_level
)

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

        self.setLayoutDirection(Qt.RightToLeft)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditable(False)

        self.setStyleSheet("""
            QComboBox {
                background: transparent;
                border: none;
                color: transparent;
                padding: 0px;
            }
            QComboBox::drop-down {
                width: 0px;
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = theme_manager.colors()

        rect = self.rect().adjusted(1, 1, -1, -1)

        painter.setPen(QColor(c["border"]))
        painter.setBrush(QColor(c["bg_input"]))
        painter.drawRoundedRect(rect, 22, 22)

        idx = self.currentIndex()
        text = self.itemText(idx) if idx >= 0 else ""

        painter.setPen(QColor(c["text_main"]))
        font = painter.font()
        font.setFamily("Vazirmatn")
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)

        text_rect = rect.adjusted(20, 0, -50, 0)
        painter.drawText(
            text_rect,
            Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter,
            text
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(c["accent"]))
        cx = rect.left() + 22
        cy = rect.center().y()
        triangle = QPolygon([
            QPoint(cx - 5, cy - 2),
            QPoint(cx + 5, cy - 2),
            QPoint(cx,     cy + 4),
        ])
        painter.drawPolygon(triangle)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._popup is None:
                self.showPopup()
            else:
                self.hidePopup()
            event.accept()
            return
        super().mousePressEvent(event)

    def showPopup(self):
        self._popup = QFrame(None)
        self._popup.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self._popup.setAttribute(Qt.WA_TranslucentBackground, True)
        self._popup.setLayoutDirection(Qt.RightToLeft)

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
        self._list.setLayoutDirection(Qt.RightToLeft)

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
            item.setTextAlignment(
                Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter
            )
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
        popup_w = max(self.width(), 200)
        popup_h = min(content_h, 280)

        self._popup.setFixedWidth(popup_w)
        self._popup.setFixedHeight(popup_h)

        pos = self.mapToGlobal(QPoint(self.width() - popup_w, self.height() + 4))
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
# ADD EMPLOYEES WINDOW
# =========================================================

class AddEmployees(QWidget):

    def __init__(self, parent_window=None, complex_id=None):
        super().__init__(parent_window)

        # ═══ FramelessWindowHint + Window ═══
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        self.parent_window = parent_window
        self.complex_id = complex_id

        if self.complex_id is None and self.parent_window is not None:
            self.complex_id = getattr(self.parent_window, "complex_id", None)

        self.db = Database()

        self.complex_name = "—"

        self.setWindowTitle(tr("add_employee"))
        self.setMinimumSize(200, 200)

        self.setLayoutDirection(Qt.RightToLeft)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("addEmployeesWindow")

        self.load_complex_name()
        self.setup_ui()

        self.apply_parent_geometry()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)

    # =========================================================
    # GEOMETRY
    # =========================================================

    def apply_parent_geometry(self):
        if self.parent_window is None:
            return
        try:
            pg = self.parent_window.frameGeometry()
            self.setGeometry(pg.x(), pg.y(), pg.width(), pg.height())
        except Exception as e:
            print("APPLY GEOMETRY ERROR:", e)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.apply_parent_geometry)
        QTimer.singleShot(50, self.apply_parent_geometry)
        QTimer.singleShot(150, self.apply_parent_geometry)

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("add_employee"))
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

    # =========================================================
    # LOAD COMPLEX NAME
    # =========================================================

    def load_complex_name(self):
        if not self.complex_id:
            return
        try:
            row = self.db.fetch_one(
                "SELECT name FROM complexes WHERE complexId = %s LIMIT 1",
                (self.complex_id,)
            )
            if row and row.get("name"):
                self.complex_name = row["name"]
        except Exception as e:
            print("LOAD COMPLEX NAME ERROR:", e)

    # =========================================================
    # UI
    # =========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(14)

        # HEADER
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel(tr("add_employee"))
        title.setObjectName("pageTitle")

        subtitle = QLabel(f"{tr('add_employee')} → {self.complex_name}")
        subtitle.setObjectName("pageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # FORM BOX
        form_box = QFrame()
        form_box.setObjectName("formBox")
        form_box.setAttribute(Qt.WA_StyledBackground, True)

        form_layout = QVBoxLayout(form_box)
        form_layout.setContentsMargins(24, 20, 24, 20)
        form_layout.setSpacing(6)

        # ═══ NAME ═══
        name_label = QLabel(tr("username_label"))
        name_label.setObjectName("fieldLabel")

        self.name_input = QLineEdit()
        self.name_input.setObjectName("formInput")
        self.name_input.setPlaceholderText(tr("username_ph"))
        self.name_input.setFixedHeight(44)
        self.name_input.textChanged.connect(self.clear_name_error)

        self.name_error = QLabel()
        self.name_error.setObjectName("fieldError")
        self.name_error.setFixedHeight(16)
        self.name_error.hide()

        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.name_error)

        # ═══ PHONE ═══
        phone_label = QLabel(tr("phone_label"))
        phone_label.setObjectName("fieldLabel")

        self.phone_input = QLineEdit()
        self.phone_input.setObjectName("formInput")
        self.phone_input.setPlaceholderText(tr("phone_ph"))
        self.phone_input.setFixedHeight(44)
        self.phone_input.setLayoutDirection(Qt.LeftToRight)
        self.phone_input.setMaxLength(11)
        self.phone_input.textChanged.connect(self.clear_phone_error)

        self.phone_error = QLabel()
        self.phone_error.setObjectName("fieldError")
        self.phone_error.setFixedHeight(16)
        self.phone_error.hide()

        form_layout.addWidget(phone_label)
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(self.phone_error)

        form_layout.addSpacing(4)

        # ═══ HIERARCHY ROLE ═══
        hierarchy_label = QLabel("نقش کلی")
        hierarchy_label.setObjectName("fieldLabel")

        self.hierarchy_role_combo = RoundedComboBox()
        self.hierarchy_role_combo.setObjectName("formInput")
        self.hierarchy_role_combo.setFixedHeight(44)

        self.hierarchy_role_combo.addItem("👤  کارمند",  "employee")
        self.hierarchy_role_combo.addItem("🎯  سرپرست", "supervisor")
        self.hierarchy_role_combo.addItem("📋  مدیر",   "manager")

        self.hierarchy_role_combo.currentIndexChanged.connect(
            self.on_hierarchy_role_changed
        )

        form_layout.addWidget(hierarchy_label)
        form_layout.addWidget(self.hierarchy_role_combo)

        form_layout.addSpacing(4)

        # ═══ ROLE IN GROUP ═══
        role_label = QLabel(f"{tr('role_in_group')} — {self.complex_name}")
        role_label.setObjectName("fieldLabel")

        self.role_input = QLineEdit()
        self.role_input.setObjectName("formInput")
        self.role_input.setFixedHeight(44)
        self.role_input.textChanged.connect(self.clear_role_error)

        self.role_error = QLabel()
        self.role_error.setObjectName("fieldError")
        self.role_error.setFixedHeight(16)
        self.role_error.hide()

        form_layout.addWidget(role_label)
        form_layout.addWidget(self.role_input)
        form_layout.addWidget(self.role_error)

        form_layout.addSpacing(4)

        # ═══ EMPLOYMENT TYPE ═══
        emp_type_label = QLabel(tr("employment_type"))
        emp_type_label.setObjectName("fieldLabel")

        self.emp_type_combo = RoundedComboBox()
        self.emp_type_combo.setObjectName("formInput")
        self.emp_type_combo.setFixedHeight(44)
        self.emp_type_combo.addItem(tr("full_time"), "fullTime")
        self.emp_type_combo.addItem(tr("part_time"), "partTime")

        form_layout.addWidget(emp_type_label)
        form_layout.addWidget(self.emp_type_combo)

        # DIVIDER
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setObjectName("divider")
        form_layout.addSpacing(6)
        form_layout.addWidget(divider)
        form_layout.addSpacing(6)

        section_title = QLabel(f"💰  {tr('salary_details_section')}")
        section_title.setObjectName("sectionTitle")
        form_layout.addWidget(section_title)
        form_layout.addSpacing(4)

        # ═══ SALARY TYPE ═══
        salary_type_label = QLabel(tr("salary_type"))
        salary_type_label.setObjectName("fieldLabel")

        self.salary_type_combo = RoundedComboBox()
        self.salary_type_combo.setObjectName("formInput")
        self.salary_type_combo.setFixedHeight(44)
        self.salary_type_combo.addItem(tr("monthly"), "monthly")
        self.salary_type_combo.addItem(tr("daily"), "daily")
        self.salary_type_combo.addItem(tr("hourly"), "hourly")

        form_layout.addWidget(salary_type_label)
        form_layout.addWidget(self.salary_type_combo)

        # ═══ BASE SALARY ═══
        salary_label = QLabel(tr("amount_label"))
        salary_label.setObjectName("fieldLabel")

        self.salary_input = QLineEdit()
        self.salary_input.setObjectName("formInput")
        self.salary_input.setPlaceholderText(tr("amount_ph"))
        self.salary_input.setFixedHeight(44)
        self.salary_input.setLayoutDirection(Qt.LeftToRight)
        self.salary_input.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.salary_input.textChanged.connect(self.clear_salary_error)
        self.salary_input.textChanged.connect(self.format_salary_live)

        self.salary_error = QLabel()
        self.salary_error.setObjectName("fieldError")
        self.salary_error.setFixedHeight(16)
        self.salary_error.hide()

        form_layout.addWidget(salary_label)
        form_layout.addWidget(self.salary_input)
        form_layout.addWidget(self.salary_error)

        # ═══ DAYS + HOURS ═══
        days_hours_row = QHBoxLayout()
        days_hours_row.setSpacing(10)

        days_col = QVBoxLayout()
        days_col.setSpacing(4)
        days_label = QLabel(tr("days_per_month"))
        days_label.setObjectName("fieldLabel")
        self.days_input = QLineEdit()
        self.days_input.setObjectName("formInput")
        self.days_input.setPlaceholderText("26")
        self.days_input.setFixedHeight(44)
        self.days_input.setLayoutDirection(Qt.LeftToRight)
        self.days_input.setText("26")
        days_col.addWidget(days_label)
        days_col.addWidget(self.days_input)

        hours_col = QVBoxLayout()
        hours_col.setSpacing(4)
        hours_label = QLabel(tr("hours_per_day"))
        hours_label.setObjectName("fieldLabel")
        self.hours_input = QLineEdit()
        self.hours_input.setObjectName("formInput")
        self.hours_input.setPlaceholderText("8")
        self.hours_input.setFixedHeight(44)
        self.hours_input.setLayoutDirection(Qt.LeftToRight)
        self.hours_input.setText("8")
        hours_col.addWidget(hours_label)
        hours_col.addWidget(self.hours_input)

        days_hours_row.addLayout(days_col, 1)
        days_hours_row.addLayout(hours_col, 1)
        form_layout.addLayout(days_hours_row)

        # ═══ TIMES ═══
        time_row = QHBoxLayout()
        time_row.setSpacing(10)

        start_col = QVBoxLayout()
        start_col.setSpacing(4)
        start_label = QLabel(tr("start_time"))
        start_label.setObjectName("fieldLabel")
        self.start_time = QTimeEdit()
        self.start_time.setObjectName("formInput")
        self.start_time.setDisplayFormat("HH:mm")
        self.start_time.setFixedHeight(44)
        self.start_time.setTime(QTime(8, 0))
        start_col.addWidget(start_label)
        start_col.addWidget(self.start_time)

        end_col = QVBoxLayout()
        end_col.setSpacing(4)
        end_label = QLabel(tr("end_time"))
        end_label.setObjectName("fieldLabel")
        self.end_time = QTimeEdit()
        self.end_time.setObjectName("formInput")
        self.end_time.setDisplayFormat("HH:mm")
        self.end_time.setFixedHeight(44)
        self.end_time.setTime(QTime(16, 0))
        end_col.addWidget(end_label)
        end_col.addWidget(self.end_time)

        time_row.addLayout(start_col, 1)
        time_row.addLayout(end_col, 1)
        form_layout.addLayout(time_row)

        # ═══ CHECKBOX ═══
        self.overtime_checkbox = QCheckBox(tr("allow_overtime_check"))
        self.overtime_checkbox.setObjectName("formCheckbox")
        self.overtime_checkbox.setChecked(True)
        self.overtime_checkbox.setCursor(Qt.PointingHandCursor)

        form_layout.addSpacing(4)
        form_layout.addWidget(self.overtime_checkbox)

        form_layout.addStretch()

        # SCROLL
        scroll = QScrollArea()
        scroll.setObjectName("formScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea#formScroll {
                background: transparent;
                border: none;
                border-radius: 28px;
            }
            QScrollArea#formScroll::viewport {
                background: transparent;
                border: none;
                border-radius: 28px;
            }
        """)

        round_bar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(round_bar)
        scroll.setWidget(form_box)

        main_layout.addWidget(scroll, 1)

        # BUTTONS
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        cancel_button = QPushButton(tr("cancel"))
        cancel_button.setObjectName("cancelButton")
        cancel_button.setFixedHeight(50)
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setAttribute(Qt.WA_StyledBackground, True)
        cancel_button.clicked.connect(self.close)

        save_button = QPushButton(tr("save"))
        save_button.setObjectName("saveButton")
        save_button.setFixedHeight(50)
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setAttribute(Qt.WA_StyledBackground, True)
        save_button.clicked.connect(self.save_employee)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

        self.on_hierarchy_role_changed()

        self.apply_stylesheet()

    # =========================================================
    # FORMAT SALARY LIVE
    # =========================================================

    def format_salary_live(self, text):
        digits = "".join(ch for ch in text if ch.isdigit())
        if not digits:
            return
        try:
            num = int(digits)
            formatted = f"{num:,}"
            if text != formatted:
                self.salary_input.blockSignals(True)
                self.salary_input.setText(formatted)
                self.salary_input.setCursorPosition(len(formatted))
                self.salary_input.blockSignals(False)
        except ValueError:
            pass

    # =========================================================
    # HIERARCHY ROLE CHANGE
    # =========================================================

    def on_hierarchy_role_changed(self):
        role = self.hierarchy_role_combo.currentData()

        role_titles = {
            "employee":   "کارمند",
            "supervisor": "سرپرست",
            "manager":    "مدیر",
        }
        all_prefixes = ["کارمند", "سرپرست", "مدیر"]

        base = role_titles.get(role, "کارمند")
        current = self.role_input.text() if hasattr(self, "role_input") else ""

        stripped = current.strip()
        for p in all_prefixes:
            if stripped.startswith(p):
                stripped = stripped[len(p):].strip()
                break

        if stripped:
            new_text = f"{base} {stripped}"
        else:
            new_text = base

        if hasattr(self, "role_input"):
            if self.role_input.text() != new_text:
                self.role_input.blockSignals(True)
                self.role_input.setText(new_text)
                self.role_input.setCursorPosition(len(new_text))
                self.role_input.blockSignals(False)

    # =========================================================
    # APPLY STYLESHEET
    # =========================================================

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""

            QWidget#addEmployeesWindow {{
                background-color: {c['bg_main']};
                font-family: "Vazirmatn";
                color: {c['text_main']};
            }}

            QWidget#addEmployeesWindow QLabel {{
                background: transparent;
            }}

            QWidget#addEmployeesWindow QFrame {{
                background: transparent;
            }}

            QLabel#pageTitle {{
                background: transparent;
                color: {c['text_main']};
                font-size: 22px;
                font-weight: 700;
            }}

            QLabel#pageSubtitle {{
                background: transparent;
                color: {c['accent']};
                font-size: 12px;
                font-weight: 600;
            }}

            QLabel#sectionTitle {{
                background: transparent;
                color: {c['accent']};
                font-size: 13px;
                font-weight: 700;
            }}

            QLabel#fieldLabel {{
                background: transparent;
                color: {c['text_dim']};
                font-size: 12px;
                font-weight: 600;
                padding: 0px;
            }}

            QLabel#fieldError {{
                background: transparent;
                color: #D93025;
                font-size: 11px;
                font-weight: 600;
                padding: 0px;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
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

            QFrame#formBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 28px;
            }}

            QFrame#divider {{
                background-color: {c['border']};
                border: none;
            }}

            QLineEdit#formInput,
            QTimeEdit#formInput {{
                background: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
                padding: 0 18px;
                color: {c['text_main']};
                font-size: 13px;
                min-height: 44px;
            }}

            QLineEdit#formInput:hover,
            QTimeEdit#formInput:hover {{
                background: {c['bg_card']};
                border: 1px solid {c['border_hover']};
            }}

            QLineEdit#formInput:focus,
            QTimeEdit#formInput:focus {{
                background: {c['bg_card']};
                border: 2px solid {c['accent']};
            }}

            QTimeEdit#formInput::up-button,
            QTimeEdit#formInput::down-button {{
                width: 20px;
                border: none;
                background: transparent;
            }}

            QCheckBox#formCheckbox {{
                background: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 14px;
                padding: 12px 14px;
                color: {c['text_main']};
                font-size: 12px;
                font-weight: 600;
                spacing: 12px;
            }}

            QCheckBox#formCheckbox:hover {{
                background: {c['bg_card']};
                border: 1px solid {c['border_hover']};
            }}

            QCheckBox#formCheckbox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid {c['border_hover']};
                background: {c['bg_card']};
            }}

            QCheckBox#formCheckbox::indicator:checked {{
                background: {c['accent']};
                border: 2px solid {c['accent']};
                image: none;
            }}

            QCheckBox#formCheckbox::indicator:hover {{
                border: 2px solid {c['accent']};
            }}

            QPushButton#saveButton {{
                background: {c['accent']};
                color: white;
                border: none;
                border-radius: 23px;
                font-size: 14px;
                font-weight: 700;
                padding: 0 28px;
            }}

            QPushButton#saveButton:hover {{
                background: {c['accent_hover']};
            }}

            QPushButton#saveButton:pressed {{
                background: #1453AA;
            }}

            QPushButton#cancelButton {{
                background: {c['bg_card']};
                color: {c['text_dim']};
                border: 1px solid {c['border']};
                border-radius: 23px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 28px;
            }}

            QPushButton#cancelButton:hover {{
                background: {c['bg_hover']};
                color: {c['accent']};
                border-color: {c['border_hover']};
            }}

        """)

    # =========================================================
    # ERROR HELPERS
    # =========================================================

    def show_error(self, label, message):
        label.setText(message)
        label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter)
        label.show()

    def clear_error(self, label):
        label.clear()
        label.hide()

    def clear_name_error(self):
        self.clear_error(self.name_error)

    def clear_phone_error(self):
        self.clear_error(self.phone_error)

    def clear_role_error(self):
        self.clear_error(self.role_error)

    def clear_salary_error(self):
        self.clear_error(self.salary_error)

    def contains_digit(self, text):
        for c in text:
            if c.isdigit():
                return True
        return False

    # =========================================================
    # OWNER MEMBER ID
    # =========================================================

    def get_owner_member_id(self):
        try:
            row = self.db.fetch_one(
                """
                SELECT memberId FROM complex_members
                WHERE complexId = %s
                  AND role IN ('owner', 'both')
                  AND isActive = '1'
                ORDER BY memberId ASC
                LIMIT 1
                """,
                (self.complex_id,)
            )
            if row:
                return row["memberId"]
        except Exception as e:
            print("GET OWNER MEMBER ID ERROR:", e)
        return None

    # =========================================================
    # SAVE
    # =========================================================

    def save_employee(self):

        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        role = self.role_input.text().strip()
        salary_text = self.salary_input.text().strip()
        days_text = self.days_input.text().strip()
        hours_text = self.hours_input.text().strip()

        employment_type = self.emp_type_combo.currentData()
        salary_type = self.salary_type_combo.currentData()

        hierarchy_role = self.hierarchy_role_combo.currentData() or "employee"

        allow_ot = "1" if self.overtime_checkbox.isChecked() else "0"
        can_see = "1"

        # ═══ NAME ═══
        self.clear_error(self.name_error)
        if not name:
            self.show_error(self.name_error, "لطفاً نام را وارد کنید.")
            self.name_input.setFocus()
            return

        if self.contains_digit(name):
            self.show_error(self.name_error, "نام نباید شامل عدد باشد.")
            self.name_input.setFocus()
            return

        # ═══ PHONE ═══
        self.clear_error(self.phone_error)
        if not phone:
            self.show_error(self.phone_error, "لطفاً شماره موبایل را وارد کنید.")
            self.phone_input.setFocus()
            return

        if not phone.isdigit() or len(phone) != 11 or not phone.startswith("09"):
            self.show_error(self.phone_error, "شماره باید ۱۱ رقم و با ۰۹ شروع شود.")
            self.phone_input.setFocus()
            return

        # ═══ ROLE ═══
        self.clear_error(self.role_error)
        if not role:
            self.show_error(self.role_error, "لطفاً نقش در مجموعه را وارد کنید.")
            self.role_input.setFocus()
            return

        # ═══ SALARY ═══
        self.clear_error(self.salary_error)
        if not salary_text:
            self.show_error(self.salary_error, "لطفاً حقوق را وارد کنید.")
            self.salary_input.setFocus()
            return

        try:
            salary = float(salary_text.replace(",", "").replace("٬", ""))
        except ValueError:
            self.show_error(self.salary_error, "حقوق باید عدد باشد.")
            self.salary_input.setFocus()
            return

        if salary <= 0:
            self.show_error(self.salary_error, "حقوق باید بزرگ‌تر از صفر باشد.")
            self.salary_input.setFocus()
            return

        try:
            work_days = float(days_text or 26)
        except ValueError:
            work_days = 26

        try:
            work_hours = float(hours_text or 8)
        except ValueError:
            work_hours = 8

        if work_days <= 0:
            work_days = 26
        if work_hours <= 0:
            work_hours = 8

        start_time = self.start_time.time().toString("HH:mm:ss")
        end_time = self.end_time.time().toString("HH:mm:ss")

        if not self.complex_id:
            NiceMessageBox.error(self, tr("error"), "مجتمعی انتخاب نشده.")
            return

        # ═══ FIND OR CREATE USER ═══
        user = self.db.fetch_one(
            """
            SELECT userId FROM users
            WHERE phoneNumber = %s LIMIT 1
            """,
            (phone,)
        )

        if user:
            user_id = user["userId"]
        else:
            user_id = self.db.execute(
                """
                INSERT INTO users (
                    name, profession, countryCode, phoneNumber,
                    createdDate, sentOtp, otpSentDateTime,
                    otpUsed, isActive
                )
                VALUES (%s, 'unknown', '+98', %s, NOW(), 0, NULL, '0', '1')
                """,
                (name, phone)
            )

            if not user_id:
                NiceMessageBox.error(self, tr("error"), "ساخت کاربر ناموفق بود.")
                return

        # ═══ CHECK EXISTING ═══
        existing_member = self.db.fetch_one(
            """
            SELECT memberId FROM complex_members
            WHERE complexId = %s AND userId = %s LIMIT 1
            """,
            (self.complex_id, user_id)
        )

        if existing_member:
            NiceMessageBox.error(self, tr("error"), "این کاربر قبلاً در این مجتمع عضو است.")
            return

        # ═══ INSERT MEMBER ═══
        member_id = self.db.execute(
            """
            INSERT INTO complex_members (complexId, userId, role, joinedDate, isActive)
            VALUES (%s, %s, %s, %s, '1')
            """,
            (self.complex_id, user_id, hierarchy_role, datetime.now())
        )

        if not member_id:
            NiceMessageBox.error(self, tr("error"), "افزودن عضو ناموفق بود.")
            return

        # ═══ INSERT PROFILE ═══
        profile_id = self.db.execute(
            """
            INSERT INTO employee_profiles (
                memberId, jobTitle, employmentType, salaryType,
                baseSalary, workDays, workHours,
                workStartTime, workEndTime, description,
                canSeeEmployees, allowOvertime, createdDate
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s, NOW())
            """,
            (
                member_id, role, employment_type, salary_type,
                salary, work_days, work_hours,
                start_time, end_time, can_see, allow_ot
            )
        )

        if not profile_id:
            self.db.execute(
                "DELETE FROM complex_members WHERE memberId = %s",
                (member_id,)
            )
            NiceMessageBox.error(self, tr("error"), "ذخیره پروفایل ناموفق بود.")
            return

        # ═══ INSERT HIERARCHY (سرپرست = مالک) ═══
        supervisor_id = self.get_owner_member_id()
        level = role_to_level(hierarchy_role)

        ok_hierarchy = set_supervisor_and_level(
            self.db,
            self.complex_id,
            member_id,
            supervisor_id,
            level
        )

        if not ok_hierarchy:
            print("WARNING: hierarchy row not created for memberId:", member_id)

        # ═══ REFRESH PARENT ═══
        if self.parent_window is not None:
            if hasattr(self.parent_window, "load_employees_from_database"):
                self.parent_window.load_employees_from_database()

        signals.employee_added.emit(self.complex_id)
        signals.data_changed.emit("jobs")

        NiceMessageBox.success(
            self,
            tr("added"),
            f"{name} → {self.complex_name}"
        )

        self.close()