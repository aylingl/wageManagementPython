from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QCheckBox
)
from PySide6.QtCore import Qt

class SettingsWindow(QWidget):

    def __init__(self, parent_window=None):
        super().__init__()

        self.parent_window = parent_window

        self.setWindowTitle("تنظیمات")
        self.setMinimumSize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        # =========================================================
        # HEADER
        # =========================================================

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

        title = QLabel("تنظیمات")
        title.setObjectName("title")

        subtitle = QLabel("مدیریت تنظیمات حساب و برنامه")
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # =========================================================
        # SCROLL
        # =========================================================

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("scrollContent")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 12, 0)
        content_layout.setSpacing(14)

        scroll.setWidget(content)

        # =========================================================
        # ACCOUNT
        # =========================================================

        account_box = QFrame()
        account_box.setObjectName("settingsBox")

        account_layout = QVBoxLayout(account_box)
        account_layout.setContentsMargins(16, 16, 16, 16)
        account_layout.setSpacing(10)

        account_title = QLabel("حساب کاربری")
        account_title.setObjectName("sectionTitle")

        account_layout.addWidget(account_title)

        # اطلاعات پروفایل
        profile_button = QPushButton()
        profile_button.setObjectName("settingItem")
        profile_button.setMinimumHeight(70)
        profile_button.setCursor(Qt.PointingHandCursor)

        profile_layout = QHBoxLayout(profile_button)
        profile_layout.setContentsMargins(14, 10, 14, 10)
        profile_layout.setSpacing(12)

        profile_icon = QLabel("👤")
        profile_icon.setObjectName("settingIcon")
        profile_icon.setFixedSize(42, 42)
        profile_icon.setAlignment(Qt.AlignCenter)

        profile_text_layout = QVBoxLayout()
        profile_text_layout.setSpacing(3)

        profile_title = QLabel("اطلاعات پروفایل")
        profile_title.setObjectName("itemTitle")

        profile_description = QLabel(
            "نام، شماره تماس و اطلاعات شخصی"
        )
        profile_description.setObjectName("itemDescription")

        profile_text_layout.addWidget(profile_title)
        profile_text_layout.addWidget(profile_description)

        profile_arrow = QLabel("‹")
        profile_arrow.setObjectName("itemArrow")
        profile_arrow.setAlignment(Qt.AlignCenter)
        profile_arrow.setFixedWidth(25)

        profile_layout.addWidget(profile_icon)
        profile_layout.addLayout(profile_text_layout, 1)
        profile_layout.addWidget(profile_arrow)

        account_layout.addWidget(profile_button)

        # امنیت حساب
        password_button = QPushButton()
        password_button.setObjectName("settingItem")
        password_button.setMinimumHeight(70)
        password_button.setCursor(Qt.PointingHandCursor)

        password_layout = QHBoxLayout(password_button)
        password_layout.setContentsMargins(14, 10, 14, 10)
        password_layout.setSpacing(12)

        password_icon = QLabel("🔒")
        password_icon.setObjectName("settingIcon")
        password_icon.setFixedSize(42, 42)
        password_icon.setAlignment(Qt.AlignCenter)

        password_text_layout = QVBoxLayout()
        password_text_layout.setSpacing(3)

        password_title = QLabel("امنیت حساب")
        password_title.setObjectName("itemTitle")

        password_description = QLabel(
            "مدیریت رمز عبور و امنیت حساب"
        )
        password_description.setObjectName("itemDescription")

        password_text_layout.addWidget(password_title)
        password_text_layout.addWidget(password_description)

        password_arrow = QLabel("‹")
        password_arrow.setObjectName("itemArrow")
        password_arrow.setAlignment(Qt.AlignCenter)
        password_arrow.setFixedWidth(25)

        password_layout.addWidget(password_icon)
        password_layout.addLayout(password_text_layout, 1)
        password_layout.addWidget(password_arrow)

        account_layout.addWidget(password_button)

        content_layout.addWidget(account_box)

        # =========================================================
        # NOTIFICATIONS
        # =========================================================

        notification_box = QFrame()
        notification_box.setObjectName("settingsBox")

        notification_layout = QVBoxLayout(notification_box)
        notification_layout.setContentsMargins(16, 16, 16, 16)
        notification_layout.setSpacing(10)

        notification_title = QLabel("اعلان‌ها")
        notification_title.setObjectName("sectionTitle")

        notification_layout.addWidget(notification_title)

        # اعلان‌های برنامه
        notification_row = QFrame()
        notification_row.setObjectName("settingRow")

        notification_row_layout = QHBoxLayout(notification_row)
        notification_row_layout.setContentsMargins(14, 10, 14, 10)
        notification_row_layout.setSpacing(12)

        notification_icon = QLabel("🔔")
        notification_icon.setObjectName("settingIcon")
        notification_icon.setFixedSize(42, 42)
        notification_icon.setAlignment(Qt.AlignCenter)

        notification_text_layout = QVBoxLayout()
        notification_text_layout.setSpacing(3)

        notification_item_title = QLabel("اعلان‌های برنامه")
        notification_item_title.setObjectName("itemTitle")

        notification_description = QLabel(
            "دریافت پیام‌ها و اطلاع‌رسانی‌های برنامه"
        )
        notification_description.setObjectName("itemDescription")

        notification_text_layout.addWidget(notification_item_title)
        notification_text_layout.addWidget(notification_description)

        self.notification_check = QCheckBox()
        self.notification_check.setObjectName("settingCheck")
        self.notification_check.setChecked(True)

        notification_row_layout.addWidget(notification_icon)
        notification_row_layout.addLayout(notification_text_layout, 1)
        notification_row_layout.addWidget(self.notification_check)

        notification_layout.addWidget(notification_row)

        # پیام‌های جدید
        message_row = QFrame()
        message_row.setObjectName("settingRow")

        message_row_layout = QHBoxLayout(message_row)
        message_row_layout.setContentsMargins(14, 10, 14, 10)
        message_row_layout.setSpacing(12)

        message_icon = QLabel("✉")
        message_icon.setObjectName("settingIcon")
        message_icon.setFixedSize(42, 42)
        message_icon.setAlignment(Qt.AlignCenter)

        message_text_layout = QVBoxLayout()
        message_text_layout.setSpacing(3)

        message_item_title = QLabel("پیام‌های جدید")
        message_item_title.setObjectName("itemTitle")

        message_description = QLabel(
            "اعلان هنگام دریافت پیام جدید"
        )
        message_description.setObjectName("itemDescription")

        message_text_layout.addWidget(message_item_title)
        message_text_layout.addWidget(message_description)

        self.message_check = QCheckBox()
        self.message_check.setObjectName("settingCheck")
        self.message_check.setChecked(True)

        message_row_layout.addWidget(message_icon)
        message_row_layout.addLayout(message_text_layout, 1)
        message_row_layout.addWidget(self.message_check)

        notification_layout.addWidget(message_row)

        content_layout.addWidget(notification_box)

        # =========================================================
        # APPEARANCE
        # =========================================================

        appearance_box = QFrame()
        appearance_box.setObjectName("settingsBox")

        appearance_layout = QVBoxLayout(appearance_box)
        appearance_layout.setContentsMargins(16, 16, 16, 16)
        appearance_layout.setSpacing(10)

        appearance_title = QLabel("ظاهر برنامه")
        appearance_title.setObjectName("sectionTitle")

        appearance_layout.addWidget(appearance_title)

        # تم برنامه
        theme_row = QFrame()
        theme_row.setObjectName("settingRow")

        theme_layout = QHBoxLayout(theme_row)
        theme_layout.setContentsMargins(14, 10, 14, 10)
        theme_layout.setSpacing(12)

        theme_icon = QLabel("🎨")
        theme_icon.setObjectName("settingIcon")
        theme_icon.setFixedSize(42, 42)
        theme_icon.setAlignment(Qt.AlignCenter)

        theme_text_layout = QVBoxLayout()
        theme_text_layout.setSpacing(3)

        theme_item_title = QLabel("تم برنامه")
        theme_item_title.setObjectName("itemTitle")

        theme_description = QLabel(
            "انتخاب حالت نمایش برنامه"
        )
        theme_description.setObjectName("itemDescription")

        theme_text_layout.addWidget(theme_item_title)
        theme_text_layout.addWidget(theme_description)

        theme_value = QLabel("روشن")
        theme_value.setObjectName("valueLabel")

        theme_layout.addWidget(theme_icon)
        theme_layout.addLayout(theme_text_layout, 1)
        theme_layout.addWidget(theme_value)

        appearance_layout.addWidget(theme_row)

        # زبان
        language_row = QFrame()
        language_row.setObjectName("settingRow")

        language_layout = QHBoxLayout(language_row)
        language_layout.setContentsMargins(14, 10, 14, 10)
        language_layout.setSpacing(12)

        language_icon = QLabel("文")
        language_icon.setObjectName("settingIcon")
        language_icon.setFixedSize(42, 42)
        language_icon.setAlignment(Qt.AlignCenter)

        language_text_layout = QVBoxLayout()
        language_text_layout.setSpacing(3)

        language_item_title = QLabel("زبان")
        language_item_title.setObjectName("itemTitle")

        language_description = QLabel(
            "زبان نمایش برنامه"
        )
        language_description.setObjectName("itemDescription")

        language_text_layout.addWidget(language_item_title)
        language_text_layout.addWidget(language_description)

        language_value = QLabel("فارسی")
        language_value.setObjectName("valueLabel")

        language_layout.addWidget(language_icon)
        language_layout.addLayout(language_text_layout, 1)
        language_layout.addWidget(language_value)

        appearance_layout.addWidget(language_row)

        content_layout.addWidget(appearance_box)

        # =========================================================
        # SECURITY
        # =========================================================

        security_box = QFrame()
        security_box.setObjectName("settingsBox")

        security_layout = QVBoxLayout(security_box)
        security_layout.setContentsMargins(16, 16, 16, 16)
        security_layout.setSpacing(10)

        security_title = QLabel("امنیت")
        security_title.setObjectName("sectionTitle")

        security_layout.addWidget(security_title)

        login_button = QPushButton()
        login_button.setObjectName("settingItem")
        login_button.setMinimumHeight(70)
        login_button.setCursor(Qt.PointingHandCursor)

        login_layout = QHBoxLayout(login_button)
        login_layout.setContentsMargins(14, 10, 14, 10)
        login_layout.setSpacing(12)

        login_icon = QLabel("🛡")
        login_icon.setObjectName("settingIcon")
        login_icon.setFixedSize(42, 42)
        login_icon.setAlignment(Qt.AlignCenter)

        login_text_layout = QVBoxLayout()
        login_text_layout.setSpacing(3)

        login_item_title = QLabel("امنیت ورود")
        login_item_title.setObjectName("itemTitle")

        login_description = QLabel(
            "مدیریت روش‌های ورود و تأیید حساب"
        )
        login_description.setObjectName("itemDescription")

        login_text_layout.addWidget(login_item_title)
        login_text_layout.addWidget(login_description)

        login_arrow = QLabel("‹")
        login_arrow.setObjectName("itemArrow")
        login_arrow.setAlignment(Qt.AlignCenter)
        login_arrow.setFixedWidth(25)

        login_layout.addWidget(login_icon)
        login_layout.addLayout(login_text_layout, 1)
        login_layout.addWidget(login_arrow)

        security_layout.addWidget(login_button)

        content_layout.addWidget(security_box)

        # =========================================================
        # LOGOUT
        # =========================================================

        logout_button = QPushButton("خروج از حساب")
        logout_button.setObjectName("logoutButton")
        logout_button.setCursor(Qt.PointingHandCursor)

        content_layout.addWidget(logout_button)

        content_layout.addStretch()

        main_layout.addWidget(scroll)

        # =========================================================
        # STYLE
        # =========================================================

        self.setStyleSheet("""
            QWidget {
                background-color: #F5F8FC;
                font-family: Vazirmatn;
            }

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

            QFrame#settingsBox {
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
                padding-bottom: 4px;
            }

            QPushButton#settingItem {
                background-color: white;
                color: #1E2F43;
                border: 1px solid #E8EEF5;
                border-radius: 14px;
                text-align: right;
            }

            QPushButton#settingItem:hover {
                background-color: #EAF3FF;
                border-color: #C9DDF5;
            }

            QFrame#settingRow {
                background-color: white;
                border: 1px solid #E8EEF5;
                border-radius: 14px;
            }

            QFrame#settingRow:hover {
                background-color: #F8FBFF;
                border-color: #D7E5F4;
            }

            QLabel#settingIcon {
                background-color: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 12px;
                font-size: 17px;
            }

            QLabel#itemTitle {
                color: #1E2F43;
                background-color: transparent;
                border: none;
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#itemDescription {
                color: #8290A1;
                background-color: transparent;
                border: none;
                font-size: 11px;
            }

            QLabel#itemArrow {
                color: #8290A1;
                background-color: transparent;
                border: none;
                font-size: 23px;
            }

            QLabel#valueLabel {
                color: #1961C7;
                background-color: #EAF3FF;
                border: 1px solid #D5E7FA;
                border-radius: 9px;
                padding: 5px 10px;
                font-size: 11px;
                font-weight: 600;
            }

            QCheckBox#settingCheck {
                spacing: 0px;
            }

            QCheckBox#settingCheck::indicator {
                width: 42px;
                height: 22px;
                border-radius: 11px;
                background-color: #DCE5EF;
                border: none;
            }

            QCheckBox#settingCheck::indicator:checked {
                background-color: #4589E8;
            }

            QPushButton#logoutButton {
                background-color: white;
                color: #D94B4B;
                border: 1px solid #F0CCCC;
                border-radius: 14px;
                padding: 13px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#logoutButton:hover {
                background-color: #FFF5F5;
                border-color: #E8AFAF;
            }

            QScrollBar:vertical {
                width: 10px;
                background: #E8EEF6;
                border-radius: 4px;
                margin: 0px 4px px 0px;
            }

            QScrollBar::handle:vertical {
                background: #4589E8;
                border-radius: 3px;
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