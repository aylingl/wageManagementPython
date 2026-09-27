from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QDateEdit,
    QScrollArea,
    QMessageBox
)

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap

import os

class EditProfileWindow(QWidget):

    def __init__(
        self,
        parent_window=None,
        phone_number="09123456789",
        username="دانش رضایی",
        national_code="",
        birth_date=None,
        avatar="men.png"
    ):
        super().__init__()

        self.parent_window = parent_window

        self.phone_number = phone_number
        self.username = username
        self.national_code = national_code
        self.avatar = avatar

        if birth_date is None:
            self.birth_date = QDate(1370, 1, 1)
        elif isinstance(birth_date, QDate):
            self.birth_date = birth_date
        else:
            self.birth_date = QDate(1370, 1, 1)

        self.setWindowTitle("ویرایش پروفایل")
        self.setMinimumSize(700, 650)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

    # =========================================================
    # UI
    # =========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        # =====================================================
        # HEADER
        # =====================================================

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("→")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("ویرایش پروفایل")
        title.setObjectName("title")

        subtitle = QLabel("اطلاعات حساب کاربری خود را ویرایش کنید")
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # =====================================================
        # SCROLL
        # =====================================================

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        content = QWidget()
        content.setObjectName("scrollContent")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 14, 0)
        content_layout.setSpacing(16)

        scroll.setWidget(content)

        # =====================================================
        # PROFILE CARD
        # =====================================================

        profile_box = QFrame()
        profile_box.setObjectName("profileBox")

        profile_layout = QVBoxLayout(profile_box)
        profile_layout.setContentsMargins(20, 20, 20, 20)
        profile_layout.setSpacing(12)

        profile_title = QLabel("پروفایل")
        profile_title.setObjectName("sectionTitle")

        profile_layout.addWidget(profile_title)

        avatar_layout = QVBoxLayout()
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.setSpacing(8)

        self.avatar_label = QLabel()
        self.avatar_label.setObjectName("avatar")

        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setAlignment(Qt.AlignCenter)

        self.load_avatar()

        avatar_layout.addWidget(self.avatar_label)

        change_avatar_button = QPushButton("تغییر تصویر")
        change_avatar_button.setObjectName("changeAvatarButton")
        change_avatar_button.setCursor(Qt.PointingHandCursor)

        avatar_layout.addWidget(
            change_avatar_button,
            alignment=Qt.AlignCenter
        )

        profile_layout.addLayout(avatar_layout)

        content_layout.addWidget(profile_box)

        # =====================================================
        # PERSONAL INFORMATION
        # =====================================================

        information_box = QFrame()
        information_box.setObjectName("profileBox")

        information_layout = QVBoxLayout(information_box)
        information_layout.setContentsMargins(20, 20, 20, 20)
        information_layout.setSpacing(14)

        information_title = QLabel("اطلاعات شخصی")
        information_title.setObjectName("sectionTitle")

        information_layout.addWidget(information_title)

        # -----------------------------------------------------
        # NAME
        # -----------------------------------------------------

        name_label = QLabel("نام و نام خانوادگی")
        name_label.setObjectName("fieldLabel")

        self.name_input = QLineEdit()
        self.name_input.setObjectName("profileInput")
        self.name_input.setText(self.username)
        self.name_input.setPlaceholderText("نام و نام خانوادگی")

        information_layout.addWidget(name_label)
        information_layout.addWidget(self.name_input)

        # -----------------------------------------------------
        # PHONE
        # -----------------------------------------------------

        phone_label = QLabel("شماره موبایل")
        phone_label.setObjectName("fieldLabel")

        phone_button = QPushButton()
        phone_button.setObjectName("phoneButton")
        phone_button.setCursor(Qt.PointingHandCursor)
        phone_button.setMinimumHeight(48)

        phone_layout = QHBoxLayout(phone_button)
        phone_layout.setContentsMargins(14, 8, 14, 8)
        phone_layout.setSpacing(10)

        phone_text_layout = QVBoxLayout()
        phone_text_layout.setSpacing(2)

        self.phone_value = QLabel(self.phone_number)
        self.phone_value.setObjectName("phoneValue")

        phone_hint = QLabel("برای تغییر شماره، تأیید شماره جدید لازم است")
        phone_hint.setObjectName("phoneHint")

        phone_text_layout.addWidget(self.phone_value)
        phone_text_layout.addWidget(phone_hint)

        phone_arrow = QLabel("‹")
        phone_arrow.setObjectName("phoneArrow")
        phone_arrow.setFixedWidth(25)
        phone_arrow.setAlignment(Qt.AlignCenter)

        phone_layout.addLayout(phone_text_layout, 1)
        phone_layout.addWidget(phone_arrow)

        phone_button.clicked.connect(self.change_phone)

        information_layout.addWidget(phone_label)
        information_layout.addWidget(phone_button)

        # -----------------------------------------------------
        # NATIONAL CODE
        # -----------------------------------------------------

        national_label = QLabel("کد ملی")
        national_label.setObjectName("fieldLabel")

        self.national_input = QLineEdit()
        self.national_input.setObjectName("profileInput")
        self.national_input.setText(self.national_code)
        self.national_input.setPlaceholderText("کد ملی")

        information_layout.addWidget(national_label)
        information_layout.addWidget(self.national_input)

        # -----------------------------------------------------
        # BIRTH DATE
        # -----------------------------------------------------

        birth_label = QLabel("تاریخ تولد")
        birth_label.setObjectName("fieldLabel")

        self.birth_date_input = QDateEdit()
        self.birth_date_input.setObjectName("profileDate")
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDisplayFormat("yyyy/MM/dd")
        self.birth_date_input.setDate(self.birth_date)

        information_layout.addWidget(birth_label)
        information_layout.addWidget(self.birth_date_input)

        content_layout.addWidget(information_box)

        content_layout.addStretch()

        main_layout.addWidget(scroll)

        # =====================================================
        # BOTTOM BUTTONS
        # =====================================================

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        cancel_button = QPushButton("انصراف")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.close)

        save_button = QPushButton("ذخیره تغییرات")
        save_button.setObjectName("saveButton")
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.clicked.connect(self.save_profile)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                font-family: Vazirmatn;
            }

            /* ================================================
               HEADER
            ================================================ */

            QLabel#title {
                color: #1E2F43;
                font-size: 24px;
                font-weight: 700;
                background-color: transparent;
                border: none;
            }

            QLabel#subtitle {
                color: #8290A1;
                font-size: 13px;
                background-color: transparent;
                border: none;
            }

            QPushButton#backButton {
                background-color: white;
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

            /* ================================================
               SCROLL
            ================================================ */

            QScrollArea {
                background-color: transparent;
                border: none;
            }

            QScrollArea::viewport {
                background-color: transparent;
                border: none;
            }

            QWidget#scrollContent {
                background-color: transparent;
            }

            /* ================================================
               PROFILE BOX
            ================================================ */

            QFrame#profileBox {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }

            QLabel#sectionTitle {
                color: #1E2F43;
                background-color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
            }

            /* ================================================
               AVATAR
            ================================================ */

            QLabel#avatar {
                background-color: #EAF3FF;
                border: 3px solid #D5E7FA;
                border-radius: 50px;
            }

            QPushButton#changeAvatarButton {
                background-color: #EAF3FF;
                color: #1961C7;
                border: 1px solid #C9DDF5;
                border-radius: 10px;
                padding: 7px 14px;
                font-size: 11px;
                font-weight: 600;
            }

            QPushButton#changeAvatarButton:hover {
                background-color: #DDEEFF;
                border-color: #AFCFF0;
            }

            /* ================================================
               FIELDS
            ================================================ */

            QLabel#fieldLabel {
                color: #526273;
                background-color: white;
                border: none;
                font-size: 12px;
                font-weight: 600;
            }

            QLineEdit#profileInput {
                background-color: #F5F8FC;
                color: #1E2F43;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                padding: 11px 12px;
                font-size: 12px;
            }

            QLineEdit#profileInput:focus {
                background-color: white;
                border-color: #4589E8;
            }

            QDateEdit#profileDate {
                background-color: #F5F8FC;
                color: #1E2F43;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                padding: 10px 12px;
                font-size: 12px;
            }

            QDateEdit#profileDate:focus {
                background-color: white;
                border-color: #4589E8;
            }

            QDateEdit#profileDate::drop-down {
                width: 28px;
                border: none;
            }

            /* ================================================
               PHONE
            ================================================ */

            QPushButton#phoneButton {
                background-color: #F8FBFF;
                color: #1E2F43;
                border: 1px solid #DDE8F3;
                border-radius: 12px;
                text-align: right;
            }

            QPushButton#phoneButton:hover {
                background-color: #EAF3FF;
                border-color: #C9DDF5;
            }

            QLabel#phoneValue {
                color: #1E2F43;
                background-color: transparent;
                border: none;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#phoneHint {
                color: #8290A1;
                background-color: transparent;
                border: none;
                font-size: 10px;
            }

            QLabel#phoneArrow {
                color: #8290A1;
                background-color: transparent;
                border: none;
                font-size: 23px;
            }

            /* ================================================
               BOTTOM BUTTONS
            ================================================ */

            QPushButton#cancelButton {
                background-color: white;
                color: #526273;
                border: 1px solid #E2EAF4;
                border-radius: 12px;
                padding: 12px 22px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#cancelButton:hover {
                background-color: #EAF3FF;
                border-color: #C9DDF5;
            }

            QPushButton#saveButton {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#saveButton:hover {
                background-color: #4589E8;
            }

            /* ================================================
               SCROLLBAR
            ================================================ */

            QScrollBar:vertical {
                width: 9px;
                background: #E8EEF6;
                border-radius: 4px;
                margin: 4px 8px 4px 0px;
            }

            QScrollBar::handle:vertical {
                background: #4589E8;
                border-radius: 4px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #1961C7;
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

    # =========================================================
    # AVATAR
    # =========================================================

    def load_avatar(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        avatar_path = os.path.join(
            base_dir,
            "avatars",
            self.avatar
        )

        if os.path.exists(avatar_path):

            pixmap = QPixmap(avatar_path)

            pixmap = pixmap.scaled(
                94,
                94,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.avatar_label.setPixmap(pixmap)

        else:
            self.avatar_label.setText("👤")

    # =========================================================
    # CHANGE PHONE
    # =========================================================

    def change_phone(self):

        from main import LoginWindow

        self.login_window = LoginWindow(
            change_phone=True,
            parent_profile=self
        )

        self.login_window.resize(self.size())
        self.login_window.move(self.pos())
        self.login_window.show()
        self.login_window.raise_()
        self.login_window.activateWindow()

        self.hide()

    # =========================================================
    # SAVE
    # =========================================================

    def save_profile(self):

        name = self.name_input.text().strip()
        national_code = self.national_input.text().strip()

        if not name:

            QMessageBox.warning(
                self,
                "خطا",
                "لطفاً نام و نام خانوادگی را وارد کنید."
            )

            self.name_input.setFocus()
            return

        self.username = name
        self.national_code = national_code
        self.birth_date = self.birth_date_input.date()

        QMessageBox.information(
            self,
            "ذخیره شد",
            "اطلاعات پروفایل با موفقیت ذخیره شد."
        )