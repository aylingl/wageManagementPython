import sys
import os

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QFrame,
    QVBoxLayout,
    QHBoxLayout
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from verifyWindow import VerifyWindow

class LoginWindow(QWidget):

    CONTENT_WIDTH = 360

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ورود")
        self.resize(900, 700)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

    # ==========================================
    # UI
    # ==========================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        # فقط ۳۰ پیکسل از بالای صفحه
        # فاصله بین آیتم‌ها ۵ پیکسل
        main_layout.setContentsMargins(
            0, 30, 0, 10
        )

        main_layout.setSpacing(2)

        # ==========================================
        # خوش آمدید
        # ==========================================

        welcome = QLabel("خوش آمدید 👋")

        welcome.setObjectName(
            "welcome"
        )

        welcome.setFixedSize(
            self.CONTENT_WIDTH,
            270
        )

        welcome.setAlignment(
            Qt.AlignCenter
        )

        main_layout.addWidget(
            welcome,
            0,
            Qt.AlignHCenter
        )
        

        # ==========================================
        # نحوه ورود
        # ==========================================

        description_box = QWidget()

        description_box.setFixedWidth(
            self.CONTENT_WIDTH
        )

        description_box.setFixedHeight(
            30
        )

        description_layout = QHBoxLayout(
            description_box
        )

        description_layout.setContentsMargins(
            0, 0, 0, 0
        )

        description_layout.setSpacing(0)

        description = QLabel(
            "نحوه ورود خود را انتخاب کنید"
        )

        description.setObjectName(
            "description"
        )

        description.setFixedHeight(
            16
        )

        description_layout.addWidget(
            description
        )

        description_layout.addStretch()

        main_layout.addWidget(
            description_box,
            0,
            Qt.AlignHCenter
        )

        # ==========================================
        # انتخاب شماره موبایل / ایمیل
        # ==========================================

        self.login_type_box = QFrame()

        self.login_type_box.setObjectName(
            "loginTypeBox"
        )

        self.login_type_box.setFixedSize(
            self.CONTENT_WIDTH,
            50
        )

        tabs_layout = QHBoxLayout(
            self.login_type_box
        )

        tabs_layout.setContentsMargins(
            2, 2, 2, 2
        )

        tabs_layout.setSpacing(4)

        self.phone_tab = QPushButton(
            "ورود با شماره تلفن"
        )

        self.phone_tab.setObjectName(
            "phoneTab"
        )

        self.phone_tab.setFixedHeight(
            40
        )

        self.email_tab = QPushButton(
            "ورود با ایمیل"
        )

        self.email_tab.setObjectName(
            "emailTab"
        )

        self.email_tab.setFixedHeight(
            40
        )

        tabs_layout.addWidget(
            self.phone_tab,
            1
        )

        tabs_layout.addWidget(
            self.email_tab,
            1
        )

        self.phone_tab.clicked.connect(
            self.show_phone_form
        )

        self.email_tab.clicked.connect(
            self.show_email_form
        )

        main_layout.addWidget(
            self.login_type_box,
            0,
            Qt.AlignHCenter
        )

        # ==========================================
        # فرم شماره / ایمیل
        # ==========================================

        self.form_frame = QFrame()

        self.form_frame.setObjectName(
            "formFrame"
        )

        self.form_frame.setFixedWidth(
            self.CONTENT_WIDTH
        )

        self.form_layout = QVBoxLayout(
            self.form_frame
        )

        self.form_layout.setContentsMargins(
            0, 0, 0, 0
        )

        self.form_layout.setSpacing(0)

        main_layout.addWidget(
            self.form_frame,
            0,
            Qt.AlignHCenter
        )

        # ==========================================
        # دریافت کد تأیید
        # ==========================================

        self.login_button = QPushButton(
            "دریافت کد تأیید"
        )

        self.login_button.setObjectName(
            "loginButton"
        )

        self.login_button.setFixedSize(
            self.CONTENT_WIDTH,
            44
        )

        self.login_button.clicked.connect(
            self.open_verify
        )

        main_layout.addWidget(
            self.login_button,
            0,
            Qt.AlignHCenter
        )

        # ==========================================
        # ورود با Google
        # ==========================================

        self.google_button = QPushButton(
            "ورود با Google"
        )

        self.google_button.setObjectName(
            "googleButton"
        )

        self.google_button.setFixedSize(
            self.CONTENT_WIDTH,
            44
        )

        main_layout.addWidget(
            self.google_button,
            0,
            Qt.AlignHCenter
        )

        # ==========================================
        # شرایط استفاده
        # ==========================================

        terms_widget = QWidget()

        terms_widget.setFixedWidth(
            self.CONTENT_WIDTH
        )

        terms_layout = QHBoxLayout(
            terms_widget
        )

        terms_layout.setContentsMargins(
            0, 0, 0, 0
        )

        terms_layout.setSpacing(3)

        terms_text = QLabel(
            "با ورود، موافقم با"
        )

        terms_text.setObjectName(
            "termsText"
        )

        terms_button = QPushButton(
            "شرایط استفاده"
        )

        terms_button.setObjectName(
            "termsButton"
        )

        terms_button.setFixedHeight(
            22
        )

        terms_layout.addWidget(
            terms_text
        )

        terms_layout.addWidget(
            terms_button
        )

        terms_layout.addStretch()

        main_layout.addWidget(
            terms_widget,
            0,
            Qt.AlignHCenter
        )

        # ==========================================
        # متن شرایط استفاده
        # ==========================================

        self.terms_details = QLabel()

        self.terms_details.setObjectName(
            "termsDetails"
        )

        self.terms_details.setWordWrap(
            True
        )

        self.terms_details.setFixedWidth(
            self.CONTENT_WIDTH
        )

        self.terms_details.setText(
            "با استفاده از این سامانه، شما با قوانین "
            "و شرایط استفاده از خدمات موافقت می‌کنید."
        )

        self.terms_details.hide()

        main_layout.addWidget(
            self.terms_details,
            0,
            Qt.AlignHCenter
        )

        terms_button.clicked.connect(
            self.toggle_terms
        )

        # ==========================================
        # استایل
        # ==========================================

        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                color: #1D2939;
                font-family: "Vazirmatn";
            }

            /* خوش آمدید */

            #welcome {
                background-color: transparent;
                color: #1D2939;
                font-size: 26px;
                font-weight: 700;
            }

            /* نحوه ورود */

            #description {
                background-color: transparent;
                color: #667085;
                font-size: 14px;
                font-weight: 500;
                padding: 0;
            }

            /* انتخاب نوع ورود */

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

            /* فرم */

            #formFrame {
                background-color: transparent;
                border: none;
            }

            /* کشور */

            #countryBox {
                background-color: white;
                border: 1px solid #D9E2EC;
                border-radius: 11px;
            }

            #countryCombo {
                background-color: white;
                color: #1D2939;
                border: none;
                font-size: 13px;
                padding: 0;
            }

            #countryCombo::drop-down {
                border: none;
                width: 20px;
            }

            #countryCombo QAbstractItemView {
                background-color: white;
                color: #1D2939;
                border: 1px solid #D9E2EC;
                selection-background-color: #EAF3FF;
                selection-color: #1961C7;
            }

            /* شماره موبایل */

            #phoneInput {
                background-color: white;
                color: #1D2939;
                border: none;
                font-size: 13px;
                padding: 0 12px;
            }

            /* ایمیل */

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

            /* دریافت کد */

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

            /* Google */

            #googleButton {
                background-color: white;
                color: #1D2939;
                border: 1px solid #D9E2EC;
                border-radius: 11px;
                font-size: 14px;
            }

            #googleButton:hover {
                background-color: #EAF3FF;
            }

            /* متن شرایط */

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
        """)

        # فرم اولیه
        self.set_tabs(
            True,
            False
        )

        self.show_phone_form()

    # ==========================================
    # تغییر تب‌ها
    # ==========================================

    def set_tabs(
        self,
        phone_selected,
        email_selected
    ):

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
            selected_style
            if phone_selected
            else normal_style
        )

        self.email_tab.setStyleSheet(
            selected_style
            if email_selected
            else normal_style
        )

    # ==========================================
    # فرم شماره موبایل
    # ==========================================

    def show_phone_form(self):

        self.clear_form()

        self.set_tabs(
            True,
            False
        )

        country_selector = (
            self.create_country_selector()
        )

        self.form_layout.addWidget(
            country_selector
        )

        self.login_button.setText(
            "دریافت کد تأیید"
        )

    # ==========================================
    # فرم ایمیل
    # ==========================================

    def show_email_form(self):

        self.clear_form()

        self.set_tabs(
            False,
            True
        )

        self.email_input = QLineEdit()

        self.email_input.setObjectName(
            "emailInput"
        )

        self.email_input.setPlaceholderText(
            "ایمیل خود را وارد کنید"
        )

        self.email_input.setFixedHeight(
            48
        )

        self.email_input.setLayoutDirection(
            Qt.LeftToRight
        )

        self.form_layout.addWidget(
            self.email_input
        )

        self.login_button.setText(
            "ورود"
        )

    # ==========================================
    # پاک کردن فرم
    # ==========================================

    def clear_form(self):

        while self.form_layout.count():

            item = self.form_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    # ==========================================
    # مسیر پرچم
    # ==========================================

    def flag_path(self, filename):

        project_folder = os.path.dirname(
            os.path.abspath(__file__)
        )

        return os.path.join(
            project_folder,
            "flags",
            filename
        )

    # ==========================================
    # انتخاب کشور
    # ==========================================

    def create_country_selector(self):

        country_box = QFrame()

        country_box.setObjectName(
            "countryBox"
        )

        country_box.setFixedHeight(
            48
        )

        country_box.setLayoutDirection(
            Qt.LeftToRight
        )

        layout = QHBoxLayout(
            country_box
        )

        layout.setContentsMargins(
            8, 3, 8, 3
        )

        layout.setSpacing(
            7
        )

        # کشور

        self.country_combo = QComboBox()

        self.country_combo.setObjectName(
            "countryCombo"
        )

        self.country_combo.setFixedWidth(
            95
        )

        self.country_combo.setFixedHeight(
            38
        )

        self.country_combo.setLayoutDirection(
            Qt.LeftToRight
        )

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

            path = self.flag_path(
                flag_file
            )

            pixmap = QPixmap(path)

            if pixmap.isNull():

                print(
                    "پرچم پیدا نشد:",
                    path
                )

                self.country_combo.addItem(
                    code
                )

            else:

                pixmap = pixmap.scaled(
                    28,
                    19,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                self.country_combo.addItem(
                    pixmap,
                    code
                )

        # خط جداکننده

        line = QFrame()

        line.setFixedWidth(
            1
        )

        line.setFixedHeight(
            25
        )

        line.setStyleSheet(
            "background-color: #E4E7EC;"
        )

        # شماره

        self.phone_input = QLineEdit()

        self.phone_input.setObjectName(
            "phoneInput"
        )

        self.phone_input.setPlaceholderText(
            "شماره موبایل"
        )

        self.phone_input.setFixedHeight(
            40
        )

        self.phone_input.setMaxLength(
            15
        )

        self.phone_input.setLayoutDirection(
            Qt.LeftToRight
        )

        layout.addWidget(
            self.country_combo
        )

        layout.addWidget(
            line
        )

        layout.addWidget(
            self.phone_input,
            1
        )

        return country_box

    # ==========================================
    # باز کردن Verify
    # ==========================================

    def open_verify(self):

        if not hasattr(
            self,
            "phone_input"
        ):
            return

        phone_number = (
            self.phone_input
            .text()
            .strip()
        )

        if not phone_number:
            return

        self.verify_window = VerifyWindow(
            phone_number
        )

        self.verify_window.show()

        self.close()

    # ==========================================
    # نمایش / مخفی کردن شرایط
    # ==========================================

    def toggle_terms(self):

        if self.terms_details.isVisible():

            self.terms_details.hide()

        else:

            self.terms_details.show()

# ==========================================
# اجرای برنامه
# ==========================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = LoginWindow()

    window.show()

    sys.exit(
        app.exec()
    )