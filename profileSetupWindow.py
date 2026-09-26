import os

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox,
    QGraphicsDropShadowEffect
)

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QColor

from homeWindow import HomeWindow

# ======================================================
# دکمه با Hover
# ======================================================

class HoverButton(QPushButton):

    def enterEvent(self, event):

        self.setStyleSheet("""
            QPushButton {
                background-color: #E8F1FB;
                color: #3478C9;
                border: 1px solid #3478C9;
                border-radius: 14px;
                font-family: "Vazirmatn";
                font-size: 14px;
                font-weight: 700;
            }
        """)

        super().enterEvent(event)

    def leaveEvent(self, event):

        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #3478C9;
                border: 1px solid #3478C9;
                border-radius: 14px;
                font-family: "Vazirmatn";
                font-size: 14px;
                font-weight: 700;
            }
        """)

        super().leaveEvent(event)

class ProfileSetupWindow(QWidget):

    def __init__(self, phone_number):
        super().__init__()

        self.phone_number = phone_number
        self.selected_avatar = None

        self.setWindowTitle("ساخت پروفایل")
        self.resize(1200, 750)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setObjectName("profileWindow")

        self.setup_ui()
        self.setStyleSheet(STYLE)

    def setup_ui(self):

        # ==========================================
        # صفحه اصلی
        # ==========================================

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            30,
            28,
            30,
            25
        )

        main_layout.setSpacing(0)

        # ==========================================
        # عنوان
        # ==========================================

        title = QLabel(
            "پروفایلت رو بساز ✨"
        )

        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(45)

        main_layout.addWidget(title)

        # ==========================================
        # توضیحات
        # ==========================================

        description = QLabel(
            "یک نام کاربری و آواتار برای خودت انتخاب کن"
        )

        description.setObjectName("description")
        description.setAlignment(Qt.AlignCenter)
        description.setFixedHeight(30)

        main_layout.addWidget(description)

        # ==========================================
        # فاصله
        # ==========================================

        top_space = QWidget()

        top_space.setFixedHeight(15)

        top_space.setStyleSheet(
            "background-color: transparent;"
        )

        main_layout.addWidget(top_space)

        # ==========================================
        # کارت اطلاعات پروفایل
        # ==========================================

        card = QFrame()

        card.setObjectName("card")

        card.setFixedSize(
            470,
            520
        )

        # سایه کارت
        shadow = QGraphicsDropShadowEffect()

        shadow.setBlurRadius(35)
        shadow.setOffset(0, 10)

        shadow.setColor(
            QColor(
                30,
                60,
                90,
                35
            )
        )

        card.setGraphicsEffect(shadow)

        # ==========================================
        # عنوان کارت
        # ==========================================

        profile_title = QLabel(
            "اطلاعات پروفایل",
            card
        )

        profile_title.setObjectName(
            "profileTitle"
        )

        profile_title.setGeometry(
            38,
            25,
            394,
            28
        )

        # ==========================================
        # عنوان نام کاربری
        # ==========================================

        username_label = QLabel(
            "نام کاربری",
            card
        )

        username_label.setObjectName(
            "fieldTitle"
        )

        username_label.setGeometry(
            38,
            65,
            394,
            22
        )

        # ==========================================
        # نام کاربری
        # ==========================================

        self.username_input = QLineEdit(
            card
        )

        self.username_input.setObjectName(
            "usernameInput"
        )

        self.username_input.setPlaceholderText(
            "مثلاً: Danesh"
        )

        self.username_input.setGeometry(
            38,
            93,
            394,
            50
        )

        self.username_input.setLayoutDirection(
            Qt.LeftToRight
        )

        # ==========================================
        # عنوان آواتار
        # ==========================================

        avatar_label = QLabel(
            "آواتار خودت رو انتخاب کن",
            card
        )

        avatar_label.setObjectName(
            "fieldTitle"
        )

        avatar_label.setGeometry(
            38,
            160,
            394,
            22
        )

        # ==========================================
        # آواتارها
        # ==========================================

        avatars_widget = QWidget(card)

        avatars_widget.setGeometry(
            38,
            188,
            394,
            90
        )

        avatars_widget.setStyleSheet(
            "background-color: transparent;"
        )

        avatars_layout = QHBoxLayout(
            avatars_widget
        )

        avatars_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        avatars_layout.setSpacing(
            35
        )

        avatars_layout.setAlignment(
            Qt.AlignCenter
        )

        self.avatar_buttons = []

        for filename in [
            "men.png",
            "woman.png"
        ]:

            button = QPushButton()

            button.setObjectName(
                "avatarButton"
            )

            button.setFixedSize(
                90,
                90
            )

            path = self.avatar_path(
                filename
            )

            pixmap = QPixmap(path)

            if not pixmap.isNull():

                pixmap = pixmap.scaled(
                    74,
                    74,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                button.setIcon(
                    QIcon(pixmap)
                )

                button.setIconSize(
                    QSize(74, 74)
                )

            else:

                print(
                    "عکس پیدا نشد:",
                    path
                )

            button.clicked.connect(
                lambda checked=False,
                       f=filename:
                self.select_avatar(f)
            )

            avatars_layout.addWidget(
                button
            )

            self.avatar_buttons.append(
                (
                    filename,
                    button
                )
            )

        # ==========================================
        # دکمه ادامه
        # ==========================================

        self.continue_button = HoverButton(
            "ادامه و ورود به سامانه  →",
            card
        )

        self.continue_button.setObjectName(
            "continueButton"
        )

        self.continue_button.setGeometry(
            38,
            400,
            394,
            56
        )

        self.continue_button.clicked.connect(
            self.finish_profile
        )

        self.continue_button.raise_()

        # ==========================================
        # کارت وسط صفحه
        # ==========================================

        card_container = QWidget()

        card_container.setStyleSheet(
            "background-color: transparent;"
        )

        card_container_layout = QHBoxLayout(
            card_container
        )

        card_container_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        card_container_layout.setAlignment(
            Qt.AlignHCenter
        )

        card_container_layout.addWidget(
            card
        )

        main_layout.addWidget(
            card_container
        )

    # ==========================================
    # مسیر آواتار
    # ==========================================

    def avatar_path(self, filename):

        project_folder = os.path.dirname(
            os.path.abspath(__file__)
        )

        return os.path.join(
            project_folder,
            "avatars",
            filename
        )

    # ==========================================
    # انتخاب آواتار
    # ==========================================

    def select_avatar(self, filename):

        self.selected_avatar = filename

        for avatar_filename, button in self.avatar_buttons:

            button.setProperty(
                "selected",
                avatar_filename == filename
            )

            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    # ==========================================
    # ادامه
    # ==========================================

    def finish_profile(self):

        username = (
            self.username_input
            .text()
            .strip()
        )

        if not username:

            QMessageBox.warning(
                self,
                "نام کاربری",
                "لطفاً نام کاربری خودت را وارد کن."
            )

            self.username_input.setFocus()

            return

        if self.selected_avatar is None:

            QMessageBox.warning(
                self,
                "انتخاب آواتار",
                "لطفاً یکی از آواتارها را انتخاب کن."
            )

            return

        self.home_window = HomeWindow(
            self.phone_number,
            username,
            self.selected_avatar
        )

        self.home_window.show()

        self.close()

# ======================================================
# STYLE
# ======================================================

STYLE = """

/* ==========================================
   تنظیمات کلی
   ========================================== */

QWidget {
    font-family: "Vazirmatn";
    color: #243447;
}

/* ==========================================
   پس زمینه کل صفحه
   ========================================== */

QWidget#profileWindow {
    background-color: #FFFFFF;
}

/* ==========================================
   عنوان اصلی
   ========================================== */

QLabel#title {
    background-color: transparent;
    color: #173B67;
    font-size: 30px;
    font-weight: 800;
}

/* ==========================================
   توضیحات
   ========================================== */

QLabel#description {
    background-color: transparent;
    color: #7A8999;
    font-size: 14px;
}

/* ==========================================
   کارت اطلاعات پروفایل
   ========================================== */

QFrame#card {
    background-color: #F8FBFF;
    border: 1px solid #DCE8F5;
    border-radius: 26px;
}

/* ==========================================
   عنوان اطلاعات پروفایل
   ========================================== */

QLabel#profileTitle {
    background-color: transparent;
    color: #183B61;
    font-size: 17px;
    font-weight: 800;
}

/* ==========================================
   عنوان فیلدها
   ========================================== */

QLabel#fieldTitle {
    background-color: transparent;
    color: #536779;
    font-size: 13px;
    font-weight: 600;
}

/* ==========================================
   کادر نام کاربری
   ========================================== */

QLineEdit#usernameInput {
    background-color: #FFFFFF;
    color: #243B53;
    border: 1px solid #C9D5E2;
    border-radius: 13px;
    padding: 0 17px;
    font-size: 13px;
}

QLineEdit#usernameInput:hover {
    background-color: #F9FBFD;
    border: 1px solid #91A8BF;
}

QLineEdit#usernameInput:focus {
    background-color: #FFFFFF;
    border: 2px solid #4B82C3;
}

/* ==========================================
   آواتار
   ========================================== */

QPushButton#avatarButton {
    background-color: #FFFFFF;
    border: 2px solid #D5DEE8;
    border-radius: 45px;
    padding: 5px;
}

QPushButton#avatarButton:hover {
    background-color: #F1F6FB;
    border: 2px solid #8DA8C2;
}

QPushButton#avatarButton[selected="true"] {
    background-color: #E8F1FB;
    border: 3px solid #3978B9;
}

/* ==========================================
   دکمه ادامه
   ========================================== */

QPushButton#continueButton {
    background-color: #FFFFFF;
    color: #3478C9;
    border: 1px solid #3478C9;
    border-radius: 14px;
    font-family: "Vazirmatn";
    font-size: 14px;
    font-weight: 700;
    padding: 0px;
}

"""