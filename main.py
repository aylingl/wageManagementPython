import sys
import os
import re
import random
import hashlib

from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QListView,
    QScrollArea
)

from PySide6.QtCore import (
    Qt,
    QSize,
    QPoint
)

from PySide6.QtGui import QPixmap

from verifyWindow import VerifyWindow
from database import Database

# =========================================================
# HASH PASSWORD
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# =========================================================
# EMAIL VALIDATION
# =========================================================

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# =========================================================
# FLAG COMBO BOX
# =========================================================

class FlagComboBox(QComboBox):

    def __init__(self):
        super().__init__()

        self.setIconSize(QSize(30, 20))
        self.popup_menu = None

    def showPopup(self):

        if self.popup_menu is not None:
            self.popup_menu.close()
            self.popup_menu.deleteLater()
            self.popup_menu = None
            return

        parent_window = self.window()

        menu = QFrame(parent_window)
        menu.setObjectName("flagPopup")
        menu.setFixedSize(155, 225)

        menu.setStyleSheet("""
            QFrame#flagPopup {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 22px;
            }
            QFrame#flagOption {
                background-color: #F7F9FC;
                border: 1px solid #E7EDF5;
                border-radius: 12px;
            }
            QFrame#flagOption:hover {
                background-color: #EAF3FF;
                border: 1px solid #C8DDF5;
            }
            QLabel {
                background-color: transparent;
                border: none;
                color: #1D2939;
                font-size: 13px;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 16px;
                margin: 4px 0px 4px 0px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #C8DDF5;
                min-height: 45px;
                max-width: 10px;
                margin: 0px 3px 0px 3px;
                border: none;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4589E8;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                width: 0px;
                background: transparent;
                border: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
            }
        """)

        popup_layout = QVBoxLayout(menu)
        popup_layout.setContentsMargins(10, 10, 10, 10)
        popup_layout.setSpacing(4)

        scroll_area = QScrollArea(menu)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setLayoutDirection(Qt.LeftToRight)

        scroll_content = QFrame()
        scroll_content.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)

        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)

        for index in range(self.count()):

            option = QFrame(scroll_content)
            option.setObjectName("flagOption")
            option.setFixedHeight(30)
            option.setCursor(Qt.PointingHandCursor)

            option_layout = QHBoxLayout(option)
            option_layout.setContentsMargins(8, 0, 8, 0)
            option_layout.setSpacing(8)
            option_layout.setDirection(QHBoxLayout.LeftToRight)

            flag_label = QLabel()
            flag_label.setFixedSize(30, 20)
            flag_label.setAlignment(Qt.AlignCenter)

            icon = self.itemIcon(index)

            if not icon.isNull():
                pixmap = icon.pixmap(QSize(30, 20))
                flag_label.setPixmap(pixmap)

            code_label = QLabel(self.itemText(index))
            code_label.setAlignment(Qt.AlignCenter)

            option_layout.addWidget(flag_label)
            option_layout.addWidget(code_label)
            option_layout.addStretch()

            option.mousePressEvent = (
                lambda event, selected_index=index:
                self.select_country(selected_index)
            )

            content_layout.addWidget(option)

        content_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        popup_layout.addWidget(scroll_area)

        self.popup_menu = menu

        global_pos = self.mapToGlobal(
            QPoint(self.width() - menu.width(), self.height() + 8)
        )

        local_pos = parent_window.mapFromGlobal(global_pos)

        menu.move(local_pos)
        menu.show()
        menu.raise_()

    def select_country(self, index):

        self.setCurrentIndex(index)

        if self.popup_menu is not None:
            self.popup_menu.close()
            self.popup_menu.deleteLater()
            self.popup_menu = None

    def hidePopup(self):

        if self.popup_menu is not None:
            self.popup_menu.close()
            self.popup_menu.deleteLater()
            self.popup_menu = None

# =========================================================
# PASSWORD WINDOW
# =========================================================

class PasswordWindow(QWidget):

    CONTENT_WIDTH = 360

    def __init__(self, email, parent_login=None):

        super().__init__()

        self.email = email
        self.parent_login = parent_login

        self.db = Database()

        self.setWindowTitle("ورود با رمز عبور")
        self.resize(900, 700)
        self.setMinimumSize(600, 500)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 30, 0, 20)
        main_layout.setSpacing(6)

        # BACK BUTTON
        back_row = QHBoxLayout()
        back_row.setContentsMargins(30, 0, 30, 0)

        back_button = QPushButton("→")
        back_button.setFixedSize(40, 40)
        back_button.setLayoutDirection(Qt.LeftToRight)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.go_back)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #D9E2EC;
                border-radius: 20px;
                padding: 0px;
                margin: 0px;
                color: #1D2939;
                font-size: 22px;
            }
            QPushButton:hover {
                background-color: #EAF3FF;
                border: 1px solid #BFD5EE;
                color: #1961C7;
            }
        """)

        back_row.addWidget(back_button, 0, Qt.AlignRight)
        back_row.addStretch()
        main_layout.addLayout(back_row)
        main_layout.addSpacing(30)

        # TITLE
        title = QLabel("رمز عبور خود را وارد کنید")
        title.setObjectName("pwdTitle")
        title.setFixedWidth(self.CONTENT_WIDTH)
        title.setFixedHeight(40)
        main_layout.addWidget(title, 0, Qt.AlignHCenter)

        # SUBTITLE
        subtitle = QLabel(f"ورود با حساب {self.email}")
        subtitle.setObjectName("pwdSubtitle")
        subtitle.setFixedWidth(self.CONTENT_WIDTH)
        subtitle.setFixedHeight(30)
        subtitle.setWordWrap(True)
        main_layout.addWidget(subtitle, 0, Qt.AlignHCenter)

        main_layout.addSpacing(24)

        # PASSWORD LABEL
        password_label = QLabel("رمز عبور")
        password_label.setObjectName("fieldLabel")
        password_label.setFixedWidth(self.CONTENT_WIDTH)
        password_label.setFixedHeight(22)
        main_layout.addWidget(password_label, 0, Qt.AlignHCenter)

        main_layout.addSpacing(4)

        # PASSWORD INPUT
        self.password_input = QLineEdit()
        self.password_input.setObjectName("passwordInput")
        self.password_input.setPlaceholderText("رمز عبور را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedSize(self.CONTENT_WIDTH, 48)
        self.password_input.setLayoutDirection(Qt.RightToLeft)
        self.password_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        self.password_input.textChanged.connect(self.clear_error)
        self.password_input.returnPressed.connect(self.check_password)
        main_layout.addWidget(self.password_input, 0, Qt.AlignHCenter)

        main_layout.addSpacing(6)

        # ERROR
        self.password_error = QLabel()
        self.password_error.setObjectName("passwordError")
        self.password_error.setFixedWidth(self.CONTENT_WIDTH)
        self.password_error.setFixedHeight(50)
        self.password_error.setWordWrap(True)
        self.password_error.hide()
        main_layout.addWidget(self.password_error, 0, Qt.AlignHCenter)

        main_layout.addSpacing(12)

        # BUTTON
        continue_button = QPushButton("ادامه")
        continue_button.setObjectName("loginButton")
        continue_button.setFixedSize(self.CONTENT_WIDTH, 44)
        continue_button.setCursor(Qt.PointingHandCursor)
        continue_button.clicked.connect(self.check_password)
        main_layout.addWidget(continue_button, 0, Qt.AlignHCenter)

        main_layout.addStretch()

        # STYLE
        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                color: #1D2939;
                font-family: "Vazirmatn";
            }

            #pwdTitle {
                background-color: transparent;
                color: #1D2939;
                font-size: 22px;
                font-weight: 700;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
            }

            #pwdSubtitle {
                background-color: transparent;
                color: #667085;
                font-size: 13px;
                font-weight: 500;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
            }

            #fieldLabel {
                background-color: transparent;
                color: #475467;
                font-size: 12px;
                font-weight: 600;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
            }

            #passwordInput {
                background-color: white;
                color: #1D2939;
                border: 1px solid #D9E2EC;
                border-radius: 11px;
                font-size: 13px;
                padding: 0 15px;
            }

            #passwordInput:focus {
                border: 1px solid #4589E8;
            }

            #passwordError {
                background-color: transparent;
                color: #D92D20;
                font-size: 11px;
                font-weight: 500;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignTop';
            }

            #loginButton {
                background-color: #4589E8;
                color: white;
                border: none;
                border-radius: 11px;
                font-size: 14px;
                font-weight: 600;
            }

            #loginButton:hover {
                background-color: #3479D8;
            }
        """)

    def clear_error(self):
        self.password_error.clear()
        self.password_error.hide()

    def check_password(self):

        password = self.password_input.text().strip()
        self.clear_error()

        if not password:
            self.password_error.setText("لطفاً رمز عبور را وارد کنید.")
            self.password_error.show()
            self.password_input.setFocus()
            return

        if len(password) < 6:
            self.password_error.setText("رمز عبور باید حداقل ۶ کاراکتر باشد.")
            self.password_error.show()
            self.password_input.setFocus()
            return

        # پیدا کردن کاربر با ایمیل
        user = self.db.fetch_one(
            """
            SELECT userId, name, imageBase64, phoneNumber, passwordHash
            FROM users
            WHERE email = %s
            LIMIT 1
            """,
            (self.email,)
        )

        # کاربر جدید → برو به ProfileSetupWindow
        if user is None:
            from profileSetupWindow import ProfileSetupWindow

            self.profile_window = ProfileSetupWindow(
                phone_number=None,
                email=self.email,
                password=password,
                mode="email"
            )
            self.profile_window.show()
            self.close()

            if self.parent_login is not None:
                self.parent_login.close()
            return

        # کاربر قدیمی بدون رمز
        saved_hash = user.get("passwordHash")

        if not saved_hash:
            self.password_error.setText(
                "این حساب رمز عبور ندارد.\n"
                "لطفاً با شماره تلفن وارد شو."
            )
            self.password_error.show()
            return

        # بررسی رمز
        if hash_password(password) != saved_hash:
            self.password_error.setText("رمز عبور اشتباه است.")
            self.password_error.show()
            self.password_input.setFocus()
            return

        # ورود موفق
        from homeWindow import HomeWindow

        self.home_window = HomeWindow(
            phone_number=user.get("phoneNumber"),
            username=user.get("name") or "کاربر",
            avatar=user.get("imageBase64") or "",
            email=self.email
        )
        self.home_window.show()
        self.close()

        if self.parent_login is not None:
            self.parent_login.close()

    def go_back(self):

        if self.parent_login is not None:
            self.parent_login.show()
            self.parent_login.raise_()
            self.parent_login.activateWindow()

        self.close()

# =========================================================
# GOOGLE LOGIN WINDOW
# =========================================================

class GoogleLoginWindow(QWidget):

    def __init__(self, parent_window=None):

        super().__init__()

        self.parent_window = parent_window

        self.setWindowTitle("ورود با Google")
        self.resize(500, 600)
        self.setMinimumSize(400, 450)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_google_ui()

    def image_path(self, filename):

        project_folder = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(project_folder, filename)

    def setup_google_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(45, 40, 45, 40)
        main_layout.setSpacing(0)

        back_layout = QHBoxLayout()
        back_layout.setContentsMargins(0, 0, 0, 0)
        back_layout.setSpacing(0)
        back_layout.setDirection(QHBoxLayout.LeftToRight)

        back_button = QPushButton("→")
        back_button.setFixedSize(40, 40)
        back_button.setLayoutDirection(Qt.LeftToRight)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.back_to_login)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #D9E2EC;
                border-radius: 20px;
                padding: 0px;
                margin: 0px;
                color: #1D2939;
                font-size: 22px;
            }
            QPushButton:hover {
                background-color: #EAF3FF;
                border: 1px solid #BFD5EE;
                color: #1961C7;
            }
        """)

        back_layout.addWidget(back_button, 0, Qt.AlignRight)

        main_layout.addLayout(back_layout)
        main_layout.addSpacing(5)

        google_logo = QLabel()
        google_logo.setFixedHeight(55)
        google_logo.setAlignment(Qt.AlignCenter)

        google_path = self.image_path("google.png")
        google_pixmap = QPixmap(google_path)

        if not google_pixmap.isNull():
            google_pixmap = google_pixmap.scaled(
                45, 45,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            google_logo.setPixmap(google_pixmap)

        main_layout.addWidget(google_logo)
        main_layout.addSpacing(18)

        title = QLabel("انتخاب حساب")
        title.setObjectName("googleTitle")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        main_layout.addSpacing(8)

        subtitle = QLabel("برای ادامه، یک حساب انتخاب کنید")
        subtitle.setObjectName("googleSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(28)

        self.create_account_button(
            main_layout,
            "دانش رضایی",
            "danesh@example.com"
        )

        main_layout.addSpacing(10)

        self.create_account_button(
            main_layout,
            "سارا محمدی",
            "sara@example.com"
        )

        main_layout.addSpacing(15)

        another_account = QPushButton("استفاده از حساب دیگر")
        another_account.setObjectName("anotherAccount")
        another_account.setFixedHeight(48)
        another_account.clicked.connect(self.open_other_account)
        main_layout.addWidget(another_account)

        main_layout.addStretch()

        bottom_text = QLabel(
            "با ادامه، اطلاعات حساب شما برای ورود به سامانه استفاده می‌شود."
        )
        bottom_text.setObjectName("googleBottom")
        bottom_text.setWordWrap(True)
        bottom_text.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(bottom_text)

        self.setStyleSheet("""

            QWidget {
                background-color: white;
                color: #202124;
                font-family: "Vazirmatn";
            }

            #googleTitle {
                color: #202124;
                font-size: 24px;
                font-weight: 600;
            }

            #googleSubtitle {
                color: #5F6368;
                font-size: 13px;
            }

            #accountButton {
                background-color: white;
                border: 1px solid #DADCE0;
                border-radius: 14px;
                padding: 0px;
            }

            #accountButton:hover {
                background-color: #F8FAFD;
                border: 1px solid #C7D7EA;
                border-radius: 14px;
            }

            #accountName {
                color: #202124;
                font-size: 14px;
                font-weight: 600;
                background-color: transparent;
            }

            #accountEmail {
                color: #5F6368;
                font-size: 12px;
                background-color: transparent;
            }

            #anotherAccount {
                background-color: white;
                color: #1961C7;
                border: 1px solid #D9E2EC;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
            }

            #anotherAccount:hover {
                background-color: #EAF3FF;
            }

            #googleBottom {
                background-color: transparent;
                color: #80868B;
                font-size: 10px;
            }
        """)

    def create_account_button(self, main_layout, name, email):

        account_button = QPushButton()
        account_button.setObjectName("accountButton")
        account_button.setFixedHeight(72)
        account_button.setLayoutDirection(Qt.LeftToRight)

        account_layout = QHBoxLayout(account_button)
        account_layout.setContentsMargins(12, 8, 3, 8)
        account_layout.setSpacing(10)
        account_layout.setDirection(QHBoxLayout.LeftToRight)

        avatar = QLabel()
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setText(name[0])
        avatar.setStyleSheet("""
            QLabel {
                background-color: #E8F0FE;
                color: #1961C7;
                border-radius: 22px;
                font-size: 17px;
                font-weight: 600;
            }
        """)

        account_layout.addWidget(avatar)

        account_info = QVBoxLayout()
        account_info.setContentsMargins(0, 0, 0, 0)
        account_info.setSpacing(2)
        account_info.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        name_label = QLabel(name)
        name_label.setObjectName("accountName")
        name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        email_label = QLabel(email)
        email_label.setObjectName("accountEmail")
        email_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        account_info.addWidget(name_label, 0, Qt.AlignRight)
        account_info.addWidget(email_label, 0, Qt.AlignRight)

        account_layout.addLayout(account_info, 1)

        account_button.clicked.connect(
            lambda checked=False, selected_email=email:
            self.select_account(selected_email)
        )

        main_layout.addWidget(account_button)

    def back_to_login(self):

        if self.parent_window is not None:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()

        self.close()

    def select_account(self, email):

        self.password_window = PasswordWindow(email, self.parent_window)
        self.password_window.show()
        self.password_window.raise_()
        self.password_window.activateWindow()

        self.close()

        if self.parent_window is not None:
            self.parent_window.hide()

    def open_other_account(self):

        self.other_account_window = OtherGoogleWindow(self)
        self.other_account_window.show()
        self.close()

# =========================================================
# OTHER GOOGLE ACCOUNT WINDOW
# =========================================================

class OtherGoogleWindow(QWidget):

    def __init__(self, parent_google=None):

        super().__init__()

        self.parent_google = parent_google

        self.setWindowTitle("ورود با Google")
        self.resize(500, 500)
        self.setMinimumSize(400, 400)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 40)
        layout.setSpacing(14)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        top_layout.setDirection(QHBoxLayout.LeftToRight)

        back_button = QPushButton("→")
        back_button.setFixedSize(40, 40)
        back_button.setLayoutDirection(Qt.LeftToRight)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.back_to_accounts)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #D9E2EC;
                border-radius: 20px;
                padding: 0px;
                margin: 0px;
                color: #1D2939;
                font-size: 22px;
            }
            QPushButton:hover {
                background-color: #EAF3FF;
                border: 1px solid #BFD5EE;
                color: #1961C7;
            }
        """)

        top_layout.addWidget(back_button, 0, Qt.AlignRight)
        layout.addLayout(top_layout)

        logo = QLabel()
        logo.setFixedHeight(50)
        logo.setAlignment(Qt.AlignCenter)

        project_folder = os.path.dirname(os.path.abspath(__file__))
        google_path = os.path.join(project_folder, "google.png")

        pixmap = QPixmap(google_path)

        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                42, 42,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            logo.setPixmap(pixmap)

        layout.addWidget(logo)

        title = QLabel("ورود با Google")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #202124;
            font-size: 23px;
            font-weight: 600;
        """)
        layout.addWidget(title)

        subtitle = QLabel("ایمیل خود را وارد کنید")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            color: #5F6368;
            font-size: 13px;
        """)
        layout.addWidget(subtitle)

        layout.addSpacing(15)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ایمیل")
        self.email_input.setFixedHeight(50)
        self.email_input.setLayoutDirection(Qt.LeftToRight)
        layout.addWidget(self.email_input)

        self.email_error = QLabel()
        self.email_error.setObjectName("emailError")
        self.email_error.setFixedHeight(22)
        self.email_error.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.email_error.setLayoutDirection(Qt.RightToLeft)
        self.email_error.hide()
        layout.addWidget(self.email_error)

        continue_button = QPushButton("ادامه")
        continue_button.setFixedHeight(48)
        continue_button.setStyleSheet("""
            QPushButton {
                background-color: #1A73E8;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1765CC;
            }
        """)

        continue_button.clicked.connect(self.continue_login)
        layout.addWidget(continue_button)

        layout.addStretch()

        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: "Vazirmatn";
            }
            QLineEdit {
                background-color: white;
                color: #202124;
                border: 1px solid #DADCE0;
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #1A73E8;
            }
            #emailError {
                background-color: transparent;
                color: #D92D20;
                font-size: 11px;
                font-weight: 500;
            }
        """)

    def continue_login(self):

        email = self.email_input.text().strip()

        self.email_error.clear()
        self.email_error.hide()

        if not email:
            self.email_error.setText("لطفاً ایمیل خود را وارد کنید.")
            self.email_error.show()
            return

        if not is_valid_email(email):
            self.email_error.setText("ایمیل واردشده معتبر نیست.")
            self.email_error.show()
            return

        self.password_window = PasswordWindow(
            email,
            self.parent_google.parent_window
        )
        self.password_window.show()
        self.password_window.raise_()
        self.password_window.activateWindow()

        self.close()

        if self.parent_google is not None:
            self.parent_google.hide()

    def back_to_accounts(self):

        if self.parent_google is not None:
            self.parent_google.show()
            self.parent_google.raise_()
            self.parent_google.activateWindow()

        self.close()

# =========================================================
# LOGIN WINDOW
# =========================================================

class LoginWindow(QWidget):

    CONTENT_WIDTH = 360

    def __init__(self, change_phone=False, parent_profile=None):

        super().__init__()

        self.change_phone_mode = change_phone
        self.parent_profile = parent_profile

        self.db = Database()

        self.setWindowTitle("ورود")
        self.resize(900, 700)
        self.setMinimumSize(500, 550)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 30, 0, 10)
        main_layout.setSpacing(2)

        welcome = QLabel("خوش آمدید 👋")
        welcome.setObjectName("welcome")
        welcome.setFixedSize(self.CONTENT_WIDTH, 270)
        welcome.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(welcome, 0, Qt.AlignHCenter)

        description_box = QWidget()
        description_box.setFixedWidth(self.CONTENT_WIDTH)
        description_box.setFixedHeight(30)

        description_layout = QHBoxLayout(description_box)
        description_layout.setContentsMargins(0, 0, 0, 0)
        description_layout.setSpacing(0)

        description = QLabel("نحوه ورود خود را انتخاب کنید")
        description.setObjectName("description")
        description.setFixedHeight(16)

        description_layout.addWidget(description)
        description_layout.addStretch()

        main_layout.addWidget(description_box, 0, Qt.AlignHCenter)

        self.login_type_box = QFrame()
        self.login_type_box.setObjectName("loginTypeBox")
        self.login_type_box.setFixedSize(self.CONTENT_WIDTH, 50)

        tabs_layout = QHBoxLayout(self.login_type_box)
        tabs_layout.setContentsMargins(2, 2, 2, 2)
        tabs_layout.setSpacing(4)

        self.phone_tab = QPushButton("ورود با شماره تلفن")
        self.phone_tab.setObjectName("phoneTab")
        self.phone_tab.setFixedHeight(40)

        self.email_tab = QPushButton("ورود با ایمیل")
        self.email_tab.setObjectName("emailTab")
        self.email_tab.setFixedHeight(40)

        tabs_layout.addWidget(self.phone_tab, 1)
        tabs_layout.addWidget(self.email_tab, 1)

        self.phone_tab.clicked.connect(self.show_phone_form)
        self.email_tab.clicked.connect(self.show_email_form)

        main_layout.addWidget(self.login_type_box, 0, Qt.AlignHCenter)

        self.form_frame = QFrame()
        self.form_frame.setObjectName("formFrame")
        self.form_frame.setFixedWidth(self.CONTENT_WIDTH)

        self.form_layout = QVBoxLayout(self.form_frame)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(0)

        main_layout.addWidget(self.form_frame, 0, Qt.AlignHCenter)

        self.login_button = QPushButton("دریافت کد تأیید")
        self.login_button.setObjectName("loginButton")
        self.login_button.setFixedSize(self.CONTENT_WIDTH, 44)
        self.login_button.clicked.connect(self.open_login)
        main_layout.addWidget(self.login_button, 0, Qt.AlignHCenter)

        self.google_button = QPushButton()
        self.google_button.setObjectName("googleButton")
        self.google_button.setFixedSize(self.CONTENT_WIDTH, 44)

        google_layout = QHBoxLayout(self.google_button)
        google_layout.setContentsMargins(10, 0, 10, 0)
        google_layout.setSpacing(8)
        google_layout.addStretch()

        google_text = QLabel("ورود با Google")
        google_text.setObjectName("googleText")
        google_text.setAttribute(Qt.WA_TransparentForMouseEvents)

        google_icon = QLabel()
        google_icon.setFixedSize(22, 22)
        google_icon.setAttribute(Qt.WA_TransparentForMouseEvents)

        google_pixmap = QPixmap(self.image_path("google.png"))

        if not google_pixmap.isNull():
            google_pixmap = google_pixmap.scaled(
                20, 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            google_icon.setPixmap(google_pixmap)

        google_icon.setAlignment(Qt.AlignCenter)

        google_layout.addWidget(google_text)
        google_layout.addWidget(google_icon)
        google_layout.addStretch()

        self.google_button.clicked.connect(self.open_google)
        main_layout.addWidget(self.google_button, 0, Qt.AlignHCenter)

        terms_widget = QWidget()
        terms_widget.setFixedWidth(self.CONTENT_WIDTH)

        terms_layout = QHBoxLayout(terms_widget)
        terms_layout.setContentsMargins(0, 0, 0, 0)
        terms_layout.setSpacing(3)

        terms_text = QLabel("با ورود، موافقم با")
        terms_text.setObjectName("termsText")

        terms_button = QPushButton("شرایط استفاده")
        terms_button.setObjectName("termsButton")
        terms_button.setFixedHeight(22)

        terms_layout.addWidget(terms_text)
        terms_layout.addWidget(terms_button)
        terms_layout.addStretch()

        main_layout.addWidget(terms_widget, 0, Qt.AlignHCenter)

        self.terms_details = QLabel()
        self.terms_details.setObjectName("termsDetails")
        self.terms_details.setWordWrap(True)
        self.terms_details.setFixedWidth(self.CONTENT_WIDTH)
        self.terms_details.setText(
            "با استفاده از این سامانه، شما با قوانین "
            "و شرایط استفاده از خدمات موافقت می‌کنید."
        )
        self.terms_details.hide()

        main_layout.addWidget(self.terms_details, 0, Qt.AlignHCenter)

        terms_button.clicked.connect(self.toggle_terms)

        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                color: #1D2939;
                font-family: "Vazirmatn";
            }

            #welcome {
                background-color: transparent;
                color: #1D2939;
                font-size: 26px;
                font-weight: 700;
            }

            #description {
                background-color: transparent;
                color: #667085;
                font-size: 14px;
                font-weight: 500;
                padding: 0;
            }

            #loginTypeBox {
                background-color: white;
                border: 1px solid #DCE6F2;
                border-radius: 13px;
            }

            #phoneTab,
            #emailTab {
                border: none;
                border-radius: 9px;
                padding: 0;
            }

            #formFrame {
                background-color: transparent;
                border: none;
            }

            #countryBox {
                background-color: white;
                border: 1px solid #D9E2EC;
                border-radius: 13px;
            }

            #countryCombo {
                background-color: white;
                color: #1D2939;
                border: none;
                border-radius: 10px;
                font-size: 20px;
                padding: 0 5px;
            }

            #countryCombo:focus {
                border: none;
                background-color: #F8FAFD;
            }

            #countryCombo:hover {
                background-color: #F8FAFD;
            }

            #countryCombo::drop-down {
                width: 22px;
                border: none;
                background-color: transparent;
            }

            #phoneInput {
                background-color: white;
                color: #1D2939;
                border: none;
                font-size: 13px;
                padding: 0 12px;
            }

            #emailInput {
                background-color: white;
                color: #1D2939;
                border: 1px solid #D9E2EC;
                border-radius: 11px;
                font-size: 13px;
                padding: 0 15px;
            }

            #emailInput:focus {
                border: 1px solid #4589E8;
            }

            #loginButton {
                background-color: #4589E8;
                color: white;
                border: none;
                border-radius: 11px;
                font-size: 14px;
                font-weight: 600;
            }

            #loginButton:hover {
                background-color: #3479D8;
            }

            #googleButton {
                background-color: white;
                color: #1D2939;
                border: 1px solid #D9E2EC;
                border-radius: 11px;
            }

            #googleButton:hover {
                background-color: #EAF3FF;
                border: 1px solid #C8DDF5;
            }

            #googleText {
                background-color: transparent;
                color: #1D2939;
                font-size: 14px;
                font-weight: 500;
            }

            #termsText {
                background-color: transparent;
                color: #98A2B3;
                font-size: 11px;
            }

            #termsButton {
                background-color: transparent;
                color: #4589E8;
                border: none;
                font-size: 11px;
            }

            #termsButton:hover {
                color: #1961C7;
            }

            #termsDetails {
                background-color: transparent;
                color: #667085;
                font-size: 11px;
                padding: 0;
            }

            #phoneError {
                background-color: transparent;
                color: #D92D20;
                font-size: 11px;
                font-weight: 500;
                padding: 0px;
                text-align: right;
            }

            #emailError {
                background-color: transparent;
                color: #D92D20;
                font-size: 11px;
                font-weight: 500;
                padding: 0px;
                text-align: right;
            }
        """)

        self.set_tabs(True, False)
        self.show_phone_form()

    def image_path(self, filename):

        project_folder = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(project_folder, filename)

    def set_tabs(self, phone_selected, email_selected):

        self.phone_tab.setProperty("selected", phone_selected)
        self.email_tab.setProperty("selected", email_selected)

        selected_style = """
            QPushButton {
                background-color: #4589E8;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3479D8;
            }
        """

        normal_style = """
            QPushButton {
                background-color: white;
                color: #667085;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #EAF3FF;
                color: #1961C7;
            }
        """

        self.phone_tab.setStyleSheet(
            selected_style if phone_selected else normal_style
        )
        self.email_tab.setStyleSheet(
            selected_style if email_selected else normal_style
        )

    def show_phone_form(self):

        self.clear_form()
        self.set_tabs(True, False)

        country_selector = self.create_country_selector()
        self.form_layout.addWidget(country_selector, 0, Qt.AlignHCenter)

        self.phone_error = QLabel()
        self.phone_error.setObjectName("phoneError")
        self.phone_error.setWordWrap(True)
        self.phone_error.setLayoutDirection(Qt.RightToLeft)
        self.phone_error.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.phone_error.setFixedWidth(self.CONTENT_WIDTH)
        self.phone_error.setFixedHeight(29)
        self.phone_error.hide()

        self.form_layout.addWidget(self.phone_error, 0, Qt.AlignRight)

        self.login_button.setText("دریافت کد تأیید")

    def show_email_form(self):

        self.clear_form()
        self.set_tabs(False, True)

        self.email_input = QLineEdit()
        self.email_input.setObjectName("emailInput")
        self.email_input.setPlaceholderText("ایمیل خود را وارد کنید")
        self.email_input.setFixedHeight(48)
        self.email_input.setLayoutDirection(Qt.LeftToRight)
        self.email_input.textChanged.connect(self.clear_email_error)
        self.form_layout.addWidget(self.email_input)

        self.email_error = QLabel()
        self.email_error.setObjectName("emailError")
        self.email_error.setWordWrap(True)
        self.email_error.setLayoutDirection(Qt.RightToLeft)
        self.email_error.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.email_error.setFixedWidth(self.CONTENT_WIDTH)
        self.email_error.setFixedHeight(29)
        self.email_error.hide()

        self.form_layout.addWidget(self.email_error, 0, Qt.AlignRight)

        self.login_button.setText("ورود")

    def clear_form(self):

        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if hasattr(self, "email_input"):
            self.email_input = None

        if hasattr(self, "email_error"):
            self.email_error = None

    def show_email_error(self, message):

        if hasattr(self, "email_error"):
            if self.email_error is not None:
                self.email_error.setText(f'<div align="right">{message}</div>')
                self.email_error.show()

    def clear_email_error(self):

        if hasattr(self, "email_error"):
            if self.email_error is not None:
                self.email_error.clear()
                self.email_error.hide()

    def flag_path(self, filename):

        project_folder = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(project_folder, "flags", filename)

    def create_country_selector(self):

        country_box = QFrame()
        country_box.setObjectName("countryBox")
        country_box.setFixedSize(360, 60)
        country_box.setLayoutDirection(Qt.LeftToRight)

        layout = QVBoxLayout(country_box)
        layout.setContentsMargins(0, 3, 0, 0)
        layout.setSpacing(0)

        phone_row = QFrame()
        phone_row.setFixedHeight(60)
        phone_row.setStyleSheet("background-color: transparent; border: none;")

        phone_layout = QHBoxLayout(phone_row)
        phone_layout.setContentsMargins(8, 3, 8, 3)
        phone_layout.setSpacing(0)

        self.country_combo = FlagComboBox()
        self.country_combo.setObjectName("countryCombo")
        self.country_combo.setFixedWidth(114)
        self.country_combo.setFixedHeight(40)
        self.country_combo.setLayoutDirection(Qt.LeftToRight)

        countries = [
            ("iran.png", "+98"),
            ("azerbaijan.png", "+994"),
            ("turkey.png", "+90"),
            ("uae.png", "+971"),
            ("uk.png", "+44"),
            ("usa.png", "+1"),
            ("germany.png", "+49")
        ]

        for flag_file, code in countries:

            path = self.flag_path(flag_file)
            pixmap = QPixmap(path)

            if pixmap.isNull():
                self.country_combo.addItem(code)
            else:
                pixmap = pixmap.scaled(
                    30, 20,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.country_combo.addItem(pixmap, code)

        line = QFrame()
        line.setFixedWidth(1)
        line.setFixedHeight(25)
        line.setStyleSheet("background-color: #E4E7EC;")

        self.phone_input = QLineEdit()
        self.phone_input.setObjectName("phoneInput")
        self.phone_input.setPlaceholderText("شماره موبایل")
        self.phone_input.setFixedHeight(40)
        self.phone_input.setMaxLength(15)
        self.phone_input.setLayoutDirection(Qt.LeftToRight)

        phone_layout.addWidget(self.country_combo)
        phone_layout.addWidget(line)
        phone_layout.addWidget(self.phone_input, 1)

        layout.addWidget(phone_row)

        return country_box

    def show_phone_error(self, message):

        if hasattr(self, "phone_error"):
            self.phone_error.setText(f'<div align="right">{message}</div>')
            self.phone_error.show()

    def clear_phone_error(self):

        if hasattr(self, "phone_error"):
            self.phone_error.clear()
            self.phone_error.hide()

    def open_login(self):

        if self.email_tab.property("selected") == True:

            if not hasattr(self, "email_input"):
                return

            if self.email_input is None:
                return

            email = self.email_input.text().strip()

            self.clear_email_error()

            if not email:
                self.show_email_error("لطفاً ایمیل خود را وارد کنید.")
                self.email_input.setFocus()
                return

            if not is_valid_email(email):
                self.show_email_error("ایمیل واردشده معتبر نیست.")
                self.email_input.setFocus()
                return

            self.password_window = PasswordWindow(email, self)
            self.password_window.show()
            self.password_window.raise_()
            self.password_window.activateWindow()

            self.hide()
            return

        if self.phone_tab.property("selected") == True:
            self.open_verify()
            return

    def open_verify(self):

        if not hasattr(self, "phone_input"):
            return

        self.clear_phone_error()

        phone_number = self.phone_input.text().strip()

        if not phone_number:
            self.show_phone_error("لطفاً شماره موبایل را وارد کنید.")
            self.phone_input.setFocus()
            return

        if " " in phone_number:
            self.show_phone_error("شماره موبایل نباید شامل فاصله باشد.")
            self.phone_input.setFocus()
            return

        if "+" in phone_number or "-" in phone_number:
            self.show_phone_error("شماره موبایل را فقط با اعداد وارد کنید.")
            self.phone_input.setFocus()
            return

        if not phone_number.isdigit():
            self.show_phone_error("شماره موبایل باید فقط شامل اعداد باشد.")
            self.phone_input.setFocus()
            return

        if len(phone_number) != 11:
            self.show_phone_error("شماره موبایل باید دقیقاً ۱۱ رقم باشد.")
            self.phone_input.setFocus()
            return

        if not phone_number.startswith("0"):
            self.show_phone_error("شماره موبایل باید با ۰ شروع شود.")
            self.phone_input.setFocus()
            return

        if not phone_number.startswith("09"):
            self.show_phone_error("شماره موبایل واردشده معتبر نیست.")
            self.phone_input.setFocus()
            return

        if phone_number == "00000000000":
            self.show_phone_error("شماره موبایل واردشده معتبر نیست.")
            self.phone_input.setFocus()
            return

        country_code = self.country_combo.currentText().strip()

        if not country_code:
            self.show_phone_error("لطفاً کشور را انتخاب کنید.")
            return

        valid_country_codes = [
            "+98", "+994", "+90", "+971", "+44", "+1", "+49"
        ]

        if country_code not in valid_country_codes:
            self.show_phone_error("کد کشور معتبر نیست.")
            return

        otp_code = random.randint(100000, 999999)
        created_date = datetime.now()
        expires_date = created_date + timedelta(seconds=45)

        otp_id = self.db.execute(
            """
            INSERT INTO pending_otps (
                countryCode,
                phoneNumber,
                otpCode,
                createdDate,
                expiresDate,
                used
            )
            VALUES (%s, %s, %s, %s, %s, '0')
            """,
            (
                country_code,
                phone_number,
                otp_code,
                created_date,
                expires_date
            )
        )

        if otp_id is None:
            self.show_phone_error(
                "خطایی در ثبت کد تأیید رخ داد. دوباره تلاش کنید."
            )
            return

        print("OTP:", otp_code)

        self.verify_window = VerifyWindow(
            phone_number,
            change_phone=self.change_phone_mode,
            parent_profile=self.parent_profile
        )
        self.verify_window.show()
        self.close()

    def open_google(self):

        self.google_window = GoogleLoginWindow(self)
        self.google_window.show()
        self.google_window.raise_()
        self.google_window.activateWindow()

    def toggle_terms(self):

        if self.terms_details.isVisible():
            self.terms_details.hide()
        else:
            self.terms_details.show()

# =========================================================
# MAIN
# =========================================================

