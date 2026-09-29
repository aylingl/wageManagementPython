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
    QMessageBox,
    QScrollBar
)

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QPainter, QColor

import os

from database import Database

# =========================================================
# ROUND SCROLL BAR
# =========================================================

class RoundScrollBar(QScrollBar):

    def __init__(self, orientation=Qt.Vertical, parent=None):
        super().__init__(orientation, parent)

        self.setFixedWidth(14)

        self.setStyleSheet("""
            QScrollBar {
                background: transparent;
                border: none;
            }
        """)

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.Antialiasing
        )

        # -------------------------------------------------
        # Track
        # -------------------------------------------------

        track_width = 6

        track_x = (
            self.width() - track_width
        ) / 2

        track_top = 5
        track_bottom = self.height() - 5

        track_height = (
            track_bottom - track_top
        )

        painter.setPen(Qt.NoPen)

        painter.setBrush(
            QColor("#E5ECF5")
        )

        painter.drawRoundedRect(
            int(track_x),
            int(track_top),
            track_width,
            int(track_height),
            track_width / 2,
            track_width / 2
        )

        # -------------------------------------------------
        # Calculate handle
        # -------------------------------------------------

        minimum = self.minimum()
        maximum = self.maximum()
        page_step = self.pageStep()

        if maximum <= minimum:
            return

        groove_top = 5
        groove_bottom = self.height() - 5
        groove_height = (
            groove_bottom - groove_top
        )

        total_range = (
            maximum - minimum + page_step
        )

        handle_height = int(
            groove_height *
            page_step /
            total_range
        )

        handle_height = max(
            42,
            handle_height
        )

        handle_height = min(
            handle_height,
            groove_height
        )

        available_space = (
            groove_height - handle_height
        )

        if maximum == minimum:
            handle_y = groove_top

        else:
            value_ratio = (
                self.value() - minimum
            ) / (
                maximum - minimum
            )

            handle_y = (
                groove_top +
                available_space *
                value_ratio
            )

        # -------------------------------------------------
        # Round Handle
        # -------------------------------------------------

        handle_width = 10

        handle_x = (
            self.width() - handle_width
        ) / 2

        painter.setBrush(
            QColor("#4589E8")
        )

        painter.drawRoundedRect(
            int(handle_x),
            int(handle_y),
            handle_width,
            int(handle_height),
            handle_width / 2,
            handle_width / 2
        )

# =========================================================
# EDIT PROFILE WINDOW
# =========================================================

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

        # =================================================
        # LOAD USER INFORMATION FROM DATABASE
        # =================================================

        self.birth_date_string = None

        self.load_user_information()

        if self.birth_date_string:

            parts = self.birth_date_string.split("/")

            if len(parts) == 3:

                try:

                    self.birth_date = QDate(
                        int(parts[0]),
                        int(parts[1]),
                        int(parts[2])
                    )

                except Exception:

                    self.birth_date = QDate(
                        1370,
                        1,
                        1
                    )

            else:

                self.birth_date = QDate(
                    1370,
                    1,
                    1
                )

        elif birth_date is None:

            self.birth_date = QDate(
                1370,
                1,
                1
            )

        elif isinstance(
            birth_date,
            QDate
        ):

            self.birth_date = birth_date

        else:

            self.birth_date = QDate(
                1370,
                1,
                1
            )

        self.setWindowTitle(
            "ویرایش پروفایل"
        )

        self.resize(900, 700)

        self.setMinimumSize(
            500,
            450
        )

        self.setLayoutDirection(
            Qt.RightToLeft
        )

        self.setup_ui()

    # =====================================================
    # LOAD USER INFORMATION
    # =====================================================

    def load_user_information(self):

        try:

            db = Database()

            user = db.fetch_one(
                """
                SELECT
                    userId,
                    name,
                    nationalId,
                    birthDate,
                    imageBase64
                FROM users
                WHERE phoneNumber = %s
                LIMIT 1
                """,
                (self.phone_number,)
            )

            db.close()

            if user:

                # -------------------------------
                # Name
                # -------------------------------

                if user.get("name"):
                    self.username = user["name"]

                # -------------------------------
                # National ID
                # -------------------------------

                if user.get("nationalId") is not None:
                    self.national_code = str(
                        user["nationalId"]
                    )

                # -------------------------------
                # Birth Date
                # -------------------------------

                if user.get("birthDate"):

                    self.birth_date_string = str(
                        user["birthDate"]
                    )

                # -------------------------------
                # Avatar
                # -------------------------------

                if user.get("imageBase64"):
                    self.avatar = user["imageBase64"]

        except Exception as e:

            print(
                "Error loading user information:",
                e
            )

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        main_layout.setSpacing(18)

        # =================================================
        # HEADER
        # =================================================

        header_layout = QHBoxLayout()

        header_layout.setSpacing(12)

        back_button = QPushButton("›")

        back_button.setObjectName(
            "backButton"
        )

        back_button.setFixedSize(
            42,
            42
        )

        back_button.setCursor(
            Qt.PointingHandCursor
        )

        back_button.clicked.connect(
            self.close
        )

        header_layout.addWidget(
            back_button
        )

        title_layout = QVBoxLayout()

        title_layout.setSpacing(3)

        title = QLabel(
            "ویرایش پروفایل"
        )

        title.setObjectName(
            "title"
        )

        subtitle = QLabel(
            "اطلاعات حساب کاربری خود را ویرایش کنید"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        header_layout.addLayout(
            title_layout
        )

        header_layout.addStretch()

        main_layout.addLayout(
            header_layout
        )

        # =================================================
        # SCROLL AREA
        # =================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        scroll_bar = RoundScrollBar(
            Qt.Vertical
        )

        scroll.setVerticalScrollBar(
            scroll_bar
        )

        content = QWidget()

        content.setObjectName(
            "scrollContent"
        )

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            0,
            0,
            12,
            0
        )

        content_layout.setSpacing(
            16
        )

        scroll.setWidget(
            content
        )

        # =================================================
        # PROFILE CARD
        # =================================================

        profile_box = QFrame()

        profile_box.setObjectName(
            "profileBox"
        )

        profile_layout = QVBoxLayout(
            profile_box
        )

        profile_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        profile_layout.setSpacing(
            12
        )

        profile_title = QLabel(
            "پروفایل"
        )

        profile_title.setObjectName(
            "sectionTitle"
        )

        profile_layout.addWidget(
            profile_title
        )

        avatar_layout = QVBoxLayout()

        avatar_layout.setAlignment(
            Qt.AlignCenter
        )

        avatar_layout.setSpacing(
            8
        )

        self.avatar_label = QLabel()

        self.avatar_label.setObjectName(
            "avatar"
        )

        self.avatar_label.setFixedSize(
            100,
            100
        )

        self.avatar_label.setAlignment(
            Qt.AlignCenter
        )

        self.load_avatar()

        avatar_layout.addWidget(
            self.avatar_label
        )

        change_avatar_button = QPushButton(
            "تغییر تصویر"
        )

        change_avatar_button.setObjectName(
            "changeAvatarButton"
        )

        change_avatar_button.setCursor(
            Qt.PointingHandCursor
        )

        change_avatar_button.clicked.connect(
            self.change_avatar
        )

        avatar_layout.addWidget(
            change_avatar_button,
            alignment=Qt.AlignCenter
        )

        profile_layout.addLayout(
            avatar_layout
        )

        content_layout.addWidget(
            profile_box
        )

        # =================================================
        # PERSONAL INFORMATION
        # =================================================

        information_box = QFrame()

        information_box.setObjectName(
            "profileBox"
        )

        information_layout = QVBoxLayout(
            information_box
        )

        information_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        information_layout.setSpacing(
            14
        )

        information_title = QLabel(
            "اطلاعات شخصی"
        )

        information_title.setObjectName(
            "sectionTitle"
        )

        information_layout.addWidget(
            information_title
        )

        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        name_label = QLabel(
            "نام و نام خانوادگی"
        )

        name_label.setObjectName(
            "fieldLabel"
        )

        self.name_input = QLineEdit()

        self.name_input.setObjectName(
            "profileInput"
        )

        self.name_input.setText(
            self.username
        )

        self.name_input.setPlaceholderText(
            "نام و نام خانوادگی"
        )

        information_layout.addWidget(
            name_label
        )

        information_layout.addWidget(
            self.name_input
        )

        self.name_error = QLabel()

        self.name_error.setObjectName(
            "fieldError"
        )

        self.name_error.setAlignment(
            Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter
        )

        self.name_error.setFixedHeight(
            20
        )

        self.name_error.hide()

        information_layout.addWidget(
            self.name_error
        )

        # -------------------------------------------------
        # PHONE
        # -------------------------------------------------

        phone_label = QLabel(
            "ویرایش شماره تلفن یا ایمیل"
        )

        phone_label.setObjectName(
            "fieldLabel"
        )

        phone_button = QPushButton()

        phone_button.setObjectName(
            "phoneButton"
        )

        phone_button.setCursor(
            Qt.PointingHandCursor
        )

        phone_button.setMinimumHeight(
            48
        )

        phone_layout = QHBoxLayout(
            phone_button
        )

        phone_layout.setContentsMargins(
            14,
            8,
            14,
            8
        )

        phone_layout.setSpacing(
            10
        )

        phone_text_layout = QVBoxLayout()

        phone_text_layout.setSpacing(
            2
        )

        self.phone_value = QLabel(
            self.phone_number
        )

        self.phone_value.setObjectName(
            "phoneValue"
        )

        phone_hint = QLabel(
            "برای تغییر شماره، تأیید شماره جدید لازم است"
        )

        phone_hint.setObjectName(
            "phoneHint"
        )

        phone_text_layout.addWidget(
            self.phone_value
        )

        phone_text_layout.addWidget(
            phone_hint
        )

        phone_arrow = QLabel("‹")

        phone_arrow.setObjectName(
            "phoneArrow"
        )

        phone_arrow.setFixedWidth(
            25
        )

        phone_arrow.setAlignment(
            Qt.AlignCenter
        )

        phone_layout.addLayout(
            phone_text_layout,
            1
        )

        phone_layout.addWidget(
            phone_arrow
        )

        phone_button.clicked.connect(
            self.change_phone
        )

        information_layout.addWidget(
            phone_label
        )

        information_layout.addWidget(
            phone_button
        )

        # -------------------------------------------------
        # NATIONAL CODE
        # -------------------------------------------------

        national_label = QLabel(
            "کد ملی"
        )

        national_label.setObjectName(
            "fieldLabel"
        )

        self.national_input = QLineEdit()

        self.national_input.setObjectName(
            "profileInput"
        )

        self.national_input.setText(
            self.national_code
        )

        self.national_input.setPlaceholderText(
            "کد ملی"
        )

        self.national_input.setMaxLength(
            10
        )

        information_layout.addWidget(
            national_label
        )

        information_layout.addWidget(
            self.national_input
        )

        self.national_error = QLabel()

        self.national_error.setObjectName(
            "fieldError"
        )

        self.national_error.setAlignment(
            Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter
        )

        self.national_error.setFixedHeight(
            20
        )

        self.national_error.hide()

        information_layout.addWidget(
            self.national_error
        )

        # -------------------------------------------------
        # BIRTH DATE
        # -------------------------------------------------

        birth_label = QLabel(
            "تاریخ تولد"
        )

        birth_label.setObjectName(
            "fieldLabel"
        )

        self.birth_date_input = QDateEdit()

        self.birth_date_input.setObjectName(
            "profileDate"
        )

        self.birth_date_input.setCalendarPopup(
            True
        )

        self.birth_date_input.setDisplayFormat(
            "yyyy/MM/dd"
        )

        self.birth_date_input.setDate(
            self.birth_date
        )

        information_layout.addWidget(
            birth_label
        )

        information_layout.addWidget(
            self.birth_date_input
        )

        self.birth_date_error = QLabel()

        self.birth_date_error.setObjectName(
            "fieldError"
        )

        self.birth_date_error.setAlignment(
            Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter
        )

        self.birth_date_error.setFixedHeight(
            20
        )

        self.birth_date_error.hide()

        information_layout.addWidget(
            self.birth_date_error
        )

        content_layout.addWidget(
            information_box
        )

        content_layout.addStretch()

        main_layout.addWidget(
            scroll,
            1
        )

        # =================================================
        # BOTTOM BUTTONS
        # =================================================

        buttons_layout = QHBoxLayout()

        buttons_layout.setSpacing(
            10
        )

        cancel_button = QPushButton(
            "انصراف"
        )

        cancel_button.setObjectName(
            "cancelButton"
        )

        cancel_button.setCursor(
            Qt.PointingHandCursor
        )

        cancel_button.clicked.connect(
            self.close
        )

        save_button = QPushButton(
            "ذخیره تغییرات"
        )

        save_button.setObjectName(
            "saveButton"
        )

        save_button.setCursor(
            Qt.PointingHandCursor
        )

        save_button.clicked.connect(
            self.save_profile
        )

        buttons_layout.addWidget(
            cancel_button
        )

        buttons_layout.addWidget(
            save_button
        )

        main_layout.addLayout(
            buttons_layout
        )

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                font-family: Vazirmatn;
            }

            QLabel#title {
                color: #1E2F43;
                font-size: 24px;
                font-weight: 700;
                background: transparent;
                border: none;
            }

            QLabel#subtitle {
                color: #8290A1;
                font-size: 13px;
                background: transparent;
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
                background: transparent;
                border: none;
            }

            QScrollArea::viewport {
                background: transparent;
                border: none;
            }

            QWidget#scrollContent {
                background: transparent;
            }

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

            QLabel#fieldLabel {
                color: #526273;
                background-color: white;
                border: none;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#fieldError {
                color: #D9534F;
                background-color: transparent;
                border: none;
                font-size: 11px;
                font-weight: 600;
                padding: 0px;
                margin: 0px;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
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
                background: transparent;
                border: none;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#phoneHint {
                color: #8290A1;
                background: transparent;
                border: none;
                font-size: 10px;
            }

            QLabel#phoneArrow {
                color: #8290A1;
                background: transparent;
                border: none;
                font-size: 23px;
            }

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
        """)

    # =========================================================
    # SHOW ERROR
    # =========================================================

    def show_field_error(
        self,
        label,
        message
    ):

        label.setText(
            message
        )

        label.setAlignment(
            Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter
        )

        label.show()

    # =========================================================
    # CLEAR ERROR
    # =========================================================

    def clear_field_error(
        self,
        label
    ):

        label.clear()
        label.hide()

    # =========================================================
    # NATIONAL ID VALIDATION
    # =========================================================

    def is_valid_national_id(
        self,
        national_id
    ):

        if len(national_id) != 10:
            return False

        if not national_id.isdigit():
            return False

        if len(set(national_id)) == 1:
            return False

        digits = [
            int(digit)
            for digit in national_id
        ]

        first_nine = digits[:9]

        control_digit = digits[9]

        total = 0

        for index in range(9):

            weight = 10 - index

            total += (
                first_nine[index] *
                weight
            )

        remainder = total % 11

        if remainder < 2:

            calculated_digit = remainder

        else:

            calculated_digit = 11 - remainder

        return (
            control_digit ==
            calculated_digit
        )

    # =========================================================
    # JALALI DATE VALIDATION
    # =========================================================

    def is_valid_jalali_date(
        self,
        date_string
    ):

        if len(date_string) != 10:
            return False

        if date_string[4] != "/":
            return False

        if date_string[7] != "/":
            return False

        year_text = date_string[0:4]
        month_text = date_string[5:7]
        day_text = date_string[8:10]

        if not year_text.isdigit():
            return False

        if not month_text.isdigit():
            return False

        if not day_text.isdigit():
            return False

        year = int(year_text)
        month = int(month_text)
        day = int(day_text)

        if year < 1300 or year > 1500:
            return False

        if month < 1 or month > 12:
            return False

        if month <= 6:

            max_day = 31

        elif month <= 11:

            max_day = 30

        else:

            if (
                (year % 33) in
                [1, 5, 9, 13, 17, 22, 26, 30]
            ):

                max_day = 30

            else:

                max_day = 29

        if day < 1 or day > max_day:
            return False

        return True

    # =========================================================
    # AVATAR
    # =========================================================

    def load_avatar(self):

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        avatar_path = os.path.join(
            base_dir,
            "avatars",
            self.avatar
        )

        if os.path.exists(
            avatar_path
        ):

            pixmap = QPixmap(
                avatar_path
            )

            pixmap = pixmap.scaled(
                94,
                94,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.avatar_label.setPixmap(
                pixmap
            )

        else:

            self.avatar_label.setText(
                "👤"
            )

    # =========================================================
    # CHANGE AVATAR
    # =========================================================

    def change_avatar(self):

        from profileSetupWindow import ProfileSetupWindow

        self.profile_setup_window = ProfileSetupWindow(
            self.phone_number
        )

        self.profile_setup_window.resize(
            self.size()
        )

        self.profile_setup_window.move(
            self.pos()
        )

        self.profile_setup_window.show()

        self.profile_setup_window.raise_()

        self.profile_setup_window.activateWindow()

        self.hide()

    # =========================================================
    # CHANGE PHONE
    # =========================================================

    def change_phone(self):

        from main import LoginWindow

        self.login_window = LoginWindow(
            change_phone=True,
            parent_profile=self
        )

        self.login_window.resize(
            self.size()
        )

        self.login_window.move(
            self.pos()
        )

        self.login_window.show()

        self.login_window.raise_()

        self.login_window.activateWindow()

        self.hide()

    # =========================================================
    # SAVE
    # =========================================================

    def save_profile(self):

        name = (
            self.name_input
            .text()
            .strip()
        )

        national_code = (
            self.national_input
            .text()
            .strip()
        )

        # =================================================
        # NAME VALIDATION
        # =================================================

        if not name:

            self.show_field_error(
                self.name_error,
                "لطفاً نام و نام خانوادگی را وارد کنید."
            )

            self.name_input.setFocus()

            return

        for character in name:

            if character.isdigit():

                self.show_field_error(
                    self.name_error,
                    "نام و نام خانوادگی نباید شامل عدد باشد."
                )

                self.name_input.setFocus()

                return

        self.clear_field_error(
            self.name_error
        )

        # =================================================
        # NATIONAL CODE VALIDATION
        # =================================================

        if not national_code:

            self.show_field_error(
                self.national_error,
                "لطفاً کد ملی را وارد کنید."
            )

            self.national_input.setFocus()

            return

        if not national_code.isdigit():

            self.show_field_error(
                self.national_error,
                "کد ملی باید فقط شامل عدد باشد."
            )

            self.national_input.setFocus()

            return

        if len(national_code) != 10:

            self.show_field_error(
                self.national_error,
                "کد ملی باید ۱۰ رقم باشد."
            )

            self.national_input.setFocus()

            return

        if not self.is_valid_national_id(
            national_code
        ):

            self.show_field_error(
                self.national_error,
                "کد ملی وارد شده معتبر نیست."
            )

            self.national_input.setFocus()

            return

        self.clear_field_error(
            self.national_error
        )

        # =================================================
        # BIRTH DATE
        # =================================================

        selected_date = (
            self.birth_date_input.date()
        )

        birth_date_string = (
            f"{selected_date.year():04d}/"
            f"{selected_date.month():02d}/"
            f"{selected_date.day():02d}"
        )

        if not self.is_valid_jalali_date(
            birth_date_string
        ):

            self.show_field_error(
                self.birth_date_error,
                "تاریخ تولد معتبر نیست."
            )

            self.birth_date_input.setFocus()

            return

        self.clear_field_error(
            self.birth_date_error
        )

        # =================================================
        # DATABASE
        # =================================================

        try:

            db = Database()

            current_user = db.fetch_one(
                """
                SELECT userId
                FROM users
                WHERE phoneNumber = %s
                LIMIT 1
                """,
                (self.phone_number,)
            )

            if not current_user:

                db.close()

                QMessageBox.warning(
                    self,
                    "خطا",
                    "اطلاعات کاربر پیدا نشد."
                )

                return

            user_id = current_user["userId"]

            # ---------------------------------------------
            # Check if national ID belongs to another user
            # ---------------------------------------------

            existing_user = db.fetch_one(
                """
                SELECT userId
                FROM users
                WHERE nationalId = %s
                AND userId <> %s
                LIMIT 1
                """,
                (
                    national_code,
                    user_id
                )
            )

            if existing_user:

                db.close()

                self.show_field_error(
                    self.national_error,
                    "این کد ملی قبلاً برای کاربر دیگری ثبت شده است."
                )

                self.national_input.setFocus()

                return

            # ---------------------------------------------
            # UPDATE USER
            # ---------------------------------------------

            db.execute(
                """
                UPDATE users
                SET
                    name = %s,
                    nationalId = %s,
                    birthDate = %s
                WHERE userId = %s
                """,
                (
                    name,
                    national_code,
                    birth_date_string,
                    user_id
                )
            )

            db.close()

            # ---------------------------------------------
            # Update local values
            # ---------------------------------------------

            self.username = name

            self.national_code = national_code

            self.birth_date_string = (
                birth_date_string
            )

            self.birth_date = (
                self.birth_date_input.date()
            )

            QMessageBox.information(
                self,
                "ذخیره شد",
                "اطلاعات پروفایل با موفقیت ذخیره شد."
            )

        except Exception as e:

            print(
                "Error saving profile:",
                e
            )

            QMessageBox.critical(
                self,
                "خطا",
                "در ذخیره اطلاعات مشکلی پیش آمد."
            )