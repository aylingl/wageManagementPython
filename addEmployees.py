import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QTimeEdit,
    QScrollArea,
    QScrollBar,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QGraphicsDropShadowEffect
)

from PySide6.QtCore import Qt, QTime, QPoint, QSize
from PySide6.QtGui import QPainter, QColor

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
# ROUNDED COMBO BOX — popup کاملاً گرد
# =========================================================

class RoundedComboBox(QComboBox):
    """
    کومبو باکس با popup گرد، سفید، تمیز — بدون هیچ گوشه‌ی تیز
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self._popup = None
        self._list = None

    def showPopup(self):

        if self._popup is not None:
            self.hidePopup()
            return

        # ─── popup frameless ───
        self._popup = QFrame(None)
        self._popup.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self._popup.setAttribute(Qt.WA_TranslucentBackground, True)

        # ─── layout بیرونی (حاشیه برای سایه) ───
        outer = QVBoxLayout(self._popup)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        # ─── کارت سفید گرد ───
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

        # ─── لیست ───
        self._list = QListWidget()
        self._list.setFrameShape(QFrame.NoFrame)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._list.setFocusPolicy(Qt.NoFocus)
        self._list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
                padding: 6px;
                color: #17324D;
                font-family: "Vazirmatn";
                font-size: 13px;
            }
            QListWidget::item {
                background: transparent;
                color: #17324D;
                border-radius: 10px;
                padding: 10px 16px;
                margin: 2px 4px;
                min-height: 20px;
            }
            QListWidget::item:hover {
                background-color: #EAF3FF;
                color: #1961C7;
            }
            QListWidget::item:selected {
                background-color: #1961C7;
                color: white;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                border: none;
                margin: 6px 2px;
            }
            QScrollBar::handle:vertical {
                background: #4589E8;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        # ─── آیتم‌ها ───
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

        # ─── استایل کارت ───
        self._popup.setStyleSheet("""
            QFrame#comboCard {
                background-color: #FFFFFF;
                border: 1px solid #DCE6F2;
                border-radius: 18px;
            }
        """)

        # ─── اندازه ───
        count = max(self.count(), 1)
        item_h = 42
        list_padding = 12
        margins = 20

        content_h = count * item_h + list_padding + margins
        popup_w = max(self.width(), 220)
        popup_h = min(content_h, 340)

        self._popup.setFixedWidth(popup_w)
        self._popup.setFixedHeight(popup_h)

        # ─── موقعیت ───
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
# ADD EMPLOYEES WINDOW
# =========================================================

class AddEmployees(QWidget):

    def __init__(self, parent_window=None, complex_id=None):
        super().__init__(parent_window)

        self.parent_window = parent_window
        self.complex_id = complex_id

        if self.complex_id is None and self.parent_window is not None:
            self.complex_id = getattr(self.parent_window, "complex_id", None)

        self.db = Database()

        self.complex_name = "—"

        self.setWindowTitle("افزودن کارمند")
        self.resize(600, 820)
        self.setMinimumSize(520, 720)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("addEmployeesWindow")

        self.load_complex_name()
        self.setup_ui()

    # =========================================================
    # LOAD COMPLEX NAME
    # =========================================================

    def load_complex_name(self):

        if not self.complex_id:
            return

        try:
            row = self.db.fetch_one(
                """
                SELECT name
                FROM complexes
                WHERE complexId = %s
                LIMIT 1
                """,
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
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("افزودن کارمند")
        title.setObjectName("pageTitle")

        subtitle = QLabel(f"افزودن کارمند به مجموعه: {self.complex_name}")
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

        # NAME
        name_label = QLabel("نام و نام خانوادگی")
        name_label.setObjectName("fieldLabel")

        self.name_input = QLineEdit()
        self.name_input.setObjectName("formInput")
        self.name_input.setPlaceholderText("مثلاً: علی رضایی")
        self.name_input.setFixedHeight(44)
        self.name_input.textChanged.connect(self.clear_name_error)

        self.name_error = QLabel()
        self.name_error.setObjectName("fieldError")
        self.name_error.setFixedHeight(16)
        self.name_error.hide()

        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.name_error)

        # PHONE
        phone_label = QLabel("شماره تلفن")
        phone_label.setObjectName("fieldLabel")

        self.phone_input = QLineEdit()
        self.phone_input.setObjectName("formInput")
        self.phone_input.setPlaceholderText("مثلاً: 09123456789")
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

        # ROLE
        role_label = QLabel(f"نقش در مجموعه «{self.complex_name}»")
        role_label.setObjectName("fieldLabel")

        self.role_input = QLineEdit()
        self.role_input.setObjectName("formInput")
        self.role_input.setPlaceholderText("مثلاً: حسابدار، فروشنده، سرپرست")
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

        # EMPLOYMENT TYPE
        emp_type_label = QLabel("نوع همکاری")
        emp_type_label.setObjectName("fieldLabel")

        self.emp_type_combo = RoundedComboBox()
        self.emp_type_combo.setObjectName("formInput")
        self.emp_type_combo.setFixedHeight(44)
        self.emp_type_combo.setCursor(Qt.PointingHandCursor)
        self.emp_type_combo.setLayoutDirection(Qt.RightToLeft)

        self.emp_type_combo.addItem("تمام‌وقت", "fullTime")
        self.emp_type_combo.addItem("پاره‌وقت", "partTime")

        form_layout.addWidget(emp_type_label)
        form_layout.addWidget(self.emp_type_combo)

        # DIVIDER
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #EEF3FA; border: none;")

        form_layout.addSpacing(6)
        form_layout.addWidget(divider)
        form_layout.addSpacing(6)

        section_title = QLabel("💰  اطلاعات حقوق و کار")
        section_title.setObjectName("sectionTitle")

        form_layout.addWidget(section_title)
        form_layout.addSpacing(4)

        # SALARY TYPE
        salary_type_label = QLabel("نوع حقوق")
        salary_type_label.setObjectName("fieldLabel")

        self.salary_type_combo = RoundedComboBox()
        self.salary_type_combo.setObjectName("formInput")
        self.salary_type_combo.setFixedHeight(44)
        self.salary_type_combo.setCursor(Qt.PointingHandCursor)
        self.salary_type_combo.setLayoutDirection(Qt.RightToLeft)

        self.salary_type_combo.addItem("ماهانه", "monthly")
        self.salary_type_combo.addItem("روزانه", "daily")
        self.salary_type_combo.addItem("ساعتی", "hourly")

        form_layout.addWidget(salary_type_label)
        form_layout.addWidget(self.salary_type_combo)

        # BASE SALARY
        salary_label = QLabel("حقوق پایه (تومان)")
        salary_label.setObjectName("fieldLabel")

        self.salary_input = QLineEdit()
        self.salary_input.setObjectName("formInput")
        self.salary_input.setPlaceholderText("مثلاً: 20000000")
        self.salary_input.setFixedHeight(44)
        self.salary_input.setLayoutDirection(Qt.LeftToRight)
        self.salary_input.textChanged.connect(self.clear_salary_error)

        self.salary_error = QLabel()
        self.salary_error.setObjectName("fieldError")
        self.salary_error.setFixedHeight(16)
        self.salary_error.hide()

        form_layout.addWidget(salary_label)
        form_layout.addWidget(self.salary_input)
        form_layout.addWidget(self.salary_error)

        # DAYS + HOURS
        days_hours_row = QHBoxLayout()
        days_hours_row.setSpacing(10)

        days_col = QVBoxLayout()
        days_col.setSpacing(4)
        days_label = QLabel("روز کاری در ماه")
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
        hours_label = QLabel("ساعت روزانه")
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

        # TIMES
        time_row = QHBoxLayout()
        time_row.setSpacing(10)

        start_col = QVBoxLayout()
        start_col.setSpacing(4)
        start_label = QLabel("ساعت شروع کار")
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
        end_label = QLabel("ساعت پایان کار")
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

        # CHECKBOXES
        self.overtime_checkbox = QCheckBox("اجازه دارد اضافه‌کار بگیرد؟")
        self.overtime_checkbox.setObjectName("formCheckbox")
        self.overtime_checkbox.setChecked(True)
        self.overtime_checkbox.setCursor(Qt.PointingHandCursor)

        self.permission_checkbox = QCheckBox("این کارمند اجازه دارد بقیه کارمندان را ببیند")
        self.permission_checkbox.setObjectName("formCheckbox")
        self.permission_checkbox.setChecked(True)
        self.permission_checkbox.setCursor(Qt.PointingHandCursor)

        form_layout.addSpacing(4)
        form_layout.addWidget(self.overtime_checkbox)
        form_layout.addWidget(self.permission_checkbox)

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

        cancel_button = QPushButton("انصراف")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setFixedHeight(50)
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.close)

        save_button = QPushButton("ذخیره کارمند")
        save_button.setObjectName("saveButton")
        save_button.setFixedHeight(50)
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.clicked.connect(self.save_employee)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

        # STYLE
        self.setStyleSheet("""

            QWidget#addEmployeesWindow {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }

            QWidget#addEmployeesWindow QLabel {
                background: transparent;
            }

            QWidget#addEmployeesWindow QFrame {
                background: transparent;
            }

            QLabel#pageTitle {
                background: transparent;
                color: #17324D;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                background: transparent;
                color: #4589E8;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#sectionTitle {
                background: transparent;
                color: #1961C7;
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#fieldLabel {
                background: transparent;
                color: #526273;
                font-size: 12px;
                font-weight: 600;
                padding: 0px;
            }

            QLabel#fieldError {
                background: transparent;
                color: #D93025;
                font-size: 11px;
                font-weight: 600;
                padding: 0px;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
            }

            QPushButton#backButton {
                background-color: #FFFFFF;
                color: #1961C7;
                border: 1px solid #E2EAF4;
                border-radius: 14px;
                font-size: 20px;
                font-weight: 600;
            }

            QPushButton#backButton:hover {
                background-color: #EAF3FF;
                border-color: #C9DDF5;
            }

            QFrame#formBox {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QLineEdit#formInput,
            QComboBox#formInput,
            QTimeEdit#formInput {
                background: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 12px;
                padding: 0 14px;
                color: #17324D;
                font-size: 13px;
            }

            QLineEdit#formInput:hover,
            QComboBox#formInput:hover,
            QTimeEdit#formInput:hover {
                background: #FFFFFF;
                border: 1px solid #C9DDF5;
            }

            QLineEdit#formInput:focus,
            QComboBox#formInput:focus,
            QTimeEdit#formInput:focus {
                background: #FFFFFF;
                border: 2px solid #4589E8;
            }

            QComboBox#formInput::drop-down {
                width: 32px;
                border: none;
                background: transparent;
            }

            QComboBox#formInput::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #4589E8;
                margin-left: 12px;
            }

            QTimeEdit#formInput::up-button,
            QTimeEdit#formInput::down-button {
                width: 20px;
                border: none;
                background: transparent;
            }

            QCheckBox#formCheckbox {
                background: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 12px;
                padding: 12px 14px;
                color: #17324D;
                font-size: 12px;
                font-weight: 600;
                spacing: 12px;
            }

            QCheckBox#formCheckbox:hover {
                background: #FFFFFF;
                border: 1px solid #C9DDF5;
            }

            QCheckBox#formCheckbox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid #C9D5E2;
                background: #FFFFFF;
            }

            QCheckBox#formCheckbox::indicator:checked {
                background: #1961C7;
                border: 2px solid #1961C7;
                image: none;
            }

            QCheckBox#formCheckbox::indicator:hover {
                border: 2px solid #4589E8;
            }

            QPushButton#saveButton {
                background: #1961C7;
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 700;
                padding: 0 28px;
            }

            QPushButton#saveButton:hover {
                background: #4589E8;
            }

            QPushButton#saveButton:pressed {
                background: #1453AA;
            }

            QPushButton#cancelButton {
                background: #FFFFFF;
                color: #526273;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 28px;
            }

            QPushButton#cancelButton:hover {
                background: #EAF3FF;
                color: #1961C7;
                border-color: #C9DDF5;
            }

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

        can_see = "1" if self.permission_checkbox.isChecked() else "0"
        allow_ot = "1" if self.overtime_checkbox.isChecked() else "0"

        # NAME
        self.clear_error(self.name_error)

        if not name:
            self.show_error(self.name_error, "لطفاً نام و نام خانوادگی را وارد کنید.")
            self.name_input.setFocus()
            return

        if self.contains_digit(name):
            self.show_error(self.name_error, "نام نباید شامل عدد باشد.")
            self.name_input.setFocus()
            return

        # PHONE
        self.clear_error(self.phone_error)

        if not phone:
            self.show_error(self.phone_error, "لطفاً شماره تلفن را وارد کنید.")
            self.phone_input.setFocus()
            return

        if not phone.isdigit() or len(phone) != 11 or not phone.startswith("09"):
            self.show_error(self.phone_error, "شماره تلفن باید ۱۱ رقم و با ۰۹ شروع شود.")
            self.phone_input.setFocus()
            return

        # ROLE
        self.clear_error(self.role_error)

        if not role:
            self.show_error(self.role_error, "لطفاً نقش کارمند را وارد کنید.")
            self.role_input.setFocus()
            return

        if self.contains_digit(role):
            self.show_error(self.role_error, "نقش نباید شامل عدد باشد.")
            self.role_input.setFocus()
            return

        # SALARY
        self.clear_error(self.salary_error)

        if not salary_text:
            self.show_error(self.salary_error, "لطفاً حقوق پایه را وارد کنید.")
            self.salary_input.setFocus()
            return

        try:
            salary = float(salary_text.replace(",", "").replace("٬", ""))
        except ValueError:
            self.show_error(self.salary_error, "حقوق پایه باید عدد باشد.")
            self.salary_input.setFocus()
            return

        if salary <= 0:
            self.show_error(self.salary_error, "حقوق پایه باید بیشتر از صفر باشد.")
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
            NiceMessageBox.warning(self, "خطا", "مجموعه فعلی مشخص نیست.")
            return

        # FIND OR CREATE USER
        user = self.db.fetch_one(
            """
            SELECT userId
            FROM users
            WHERE phoneNumber = %s
            LIMIT 1
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
                VALUES (
                    %s, 'unknown', '+98', %s,
                    NOW(), 0, NULL, '0', '1'
                )
                """,
                (name, phone)
            )

            if not user_id:
                NiceMessageBox.error(self, "خطا", "ساخت کاربر جدید انجام نشد.")
                return

        # CHECK EXISTING
        existing_member = self.db.fetch_one(
            """
            SELECT memberId
            FROM complex_members
            WHERE complexId = %s
              AND userId = %s
            LIMIT 1
            """,
            (self.complex_id, user_id)
        )

        if existing_member:
            NiceMessageBox.warning(
                self,
                "قبلاً عضو است",
                "این کاربر قبلاً در این مجموعه اضافه شده است."
            )
            return

        # INSERT MEMBER
        member_id = self.db.execute(
            """
            INSERT INTO complex_members (
                complexId, userId, role, joinedDate, isActive
            )
            VALUES (%s, %s, 'employee', %s, '1')
            """,
            (self.complex_id, user_id, datetime.now())
        )

        if not member_id:
            NiceMessageBox.error(self, "خطا", "افزودن کارمند به مجموعه انجام نشد.")
            return

        # INSERT PROFILE
        profile_id = self.db.execute(
            """
            INSERT INTO employee_profiles (
                memberId, jobTitle, employmentType, salaryType,
                baseSalary, workDays, workHours,
                workStartTime, workEndTime, description,
                canSeeEmployees, allowOvertime, createdDate
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, NULL,
                %s, %s, NOW()
            )
            """,
            (
                member_id,
                role,
                employment_type,
                salary_type,
                salary,
                work_days,
                work_hours,
                start_time,
                end_time,
                can_see,
                allow_ot
            )
        )

        if not profile_id:
            self.db.execute(
                "DELETE FROM complex_members WHERE memberId = %s",
                (member_id,)
            )
            NiceMessageBox.error(self, "خطا", "اطلاعات پروفایل کارمند ذخیره نشد.")
            return

        # REFRESH PARENT
        if self.parent_window is not None:
            if hasattr(self.parent_window, "load_employees_from_database"):
                self.parent_window.load_employees_from_database()

        # SIGNAL
        signals.employee_added.emit(self.complex_id)

        NiceMessageBox.success(
            self,
            "ثبت موفق",
            f"{name} با موفقیت به مجموعه «{self.complex_name}» اضافه شد."
        )

        self.close()