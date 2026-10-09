from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox
)

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QIcon

from profileSetupWindow import ProfileSetupWindow
from homeWindow import HomeWindow
from database import Database

class VerifyWindow(QWidget):

    def __init__(
        self,
        phone_number,
        change_phone=False,
        parent_profile=None
    ):
        super().__init__()

        self.phone_number = phone_number
        self.change_phone_mode = change_phone
        self.parent_profile = parent_profile

        # اتصال به دیتابیس
        self.db = Database()

        self.setWindowTitle("تأیید شماره موبایل")
        self.resize(1200, 750)
        self.setMinimumSize(500, 450)

        # کل صفحه راست به چپ
        self.setLayoutDirection(Qt.RightToLeft)

        # زمان تایمر
        self.remaining_seconds = 45

        self.setup_ui()
        self.start_timer()

    def setup_ui(self):

        # =========================
        # عنوان
        # =========================

        title = QLabel("تأیید شماره موبایل")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setFixedWidth(360)

        # =========================
        # پیام
        # =========================

        message = QLabel(
            f"کد تأیید به شماره {self.phone_number} ارسال شد"
        )
        message.setObjectName("message")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setFixedWidth(360)

        # =========================
        # ویرایش شماره
        # =========================

        edit_phone = QPushButton("ویرایش شماره")
        edit_phone.setObjectName("editPhoneButton")

        edit_phone.clicked.connect(
            self.edit_phone
        )

        # =========================
        # OTP
        # =========================

        otp_widget = QWidget()
        otp_widget.setLayoutDirection(Qt.LeftToRight)
        otp_widget.setFixedHeight(65)

        otp_layout = QHBoxLayout(otp_widget)
        otp_layout.setSpacing(12)

        otp_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.otp_boxes = []

        for i in range(6):

            box = QLineEdit()

            box.setMaxLength(1)
            box.setAlignment(Qt.AlignCenter)
            box.setObjectName("otpBox")

            # بعد از وارد کردن هر رقم
            # برو به خانه بعدی
            box.textChanged.connect(
                lambda text, index=i:
                self.move_to_next(index, text)
            )

            self.otp_boxes.append(box)
            otp_layout.addWidget(box)

        # =========================
        # خطای OTP
        # =========================

        error_container = QWidget()

        error_container.setFixedSize(
            330,
            22
        )

        error_container.setLayoutDirection(
            Qt.LeftToRight
        )

        self.otp_error = QLabel(
            "",
            error_container
        )

        self.otp_error.setObjectName(
            "otpError"
        )

        self.otp_error.setGeometry(
            180,
            0,
            330,
            22
        )

        self.otp_error.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self.otp_error.hide()

        # =========================
        # دکمه تأیید
        # =========================

        confirm_button = QPushButton(
            "تأیید"
        )

        confirm_button.setObjectName(
            "confirmButton"
        )

        confirm_button.setFixedSize(
            330,
            52
        )

        confirm_button.clicked.connect(
            self.check_code
        )

        # =========================
        # Timer
        # =========================

        self.timer_label = QLabel("00:45")
        self.timer_label.setObjectName("timer")
        self.timer_label.setAlignment(Qt.AlignCenter)

        # =========================
        # دکمه ارسال مجدد
        # =========================

        resend = QPushButton("ارسال مجدد کد")
        resend.setObjectName("resendButton")

        resend.clicked.connect(
            self.restart_timer
        )

        # =========================
        # Layout اصلی
        # =========================

        layout = QVBoxLayout()

        layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        layout.setSpacing(14)

        layout.addStretch(1)

        layout.addWidget(
            title,
            alignment=Qt.AlignCenter
        )

        layout.addWidget(
            message,
            alignment=Qt.AlignCenter
        )

        layout.addWidget(
            edit_phone,
            alignment=Qt.AlignCenter
        )

        layout.addSpacing(10)

        layout.addWidget(
            otp_widget,
            alignment=Qt.AlignCenter
        )

        # =========================
        # خطای OTP
        # =========================

        error_wrapper = QWidget()

        error_wrapper.setFixedWidth(330)
        error_wrapper.setFixedHeight(22)

        error_wrapper_layout = QHBoxLayout(
            error_wrapper
        )

        error_wrapper_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        error_wrapper_layout.setSpacing(0)

        error_wrapper_layout.addWidget(
            error_container
        )

        layout.addWidget(
            error_wrapper,
            alignment=Qt.AlignCenter
        )

        # =========================
        # دکمه تأیید
        # =========================

        layout.addWidget(
            confirm_button,
            alignment=Qt.AlignCenter
        )

        # =========================
        # تایمر
        # =========================

        layout.addWidget(
            self.timer_label,
            alignment=Qt.AlignCenter
        )

        # =========================
        # ارسال مجدد
        # =========================

        layout.addWidget(
            resend,
            alignment=Qt.AlignCenter
        )

        layout.addStretch(1)

        self.setLayout(layout)

        # =========================
        # Timer Object
        # =========================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_timer
        )

        # ═══ focus خودکار روی اولین خانه OTP ═══
        QTimer.singleShot(100, self.otp_boxes[0].setFocus)

        # =========================
        # Style
        # =========================

        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }

            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: #1961C7;
            }

            QLabel#message {
                font-size: 15px;
                color: #667085;
            }

            QPushButton#editPhoneButton {
                background-color: transparent;
                border: none;
                color: #4589E8;
                font-size: 13px;
                padding: 0;
            }

            QPushButton#editPhoneButton:hover {
                color: #1961C7;
            }

            QLineEdit#otpBox {
                background-color: white;
                border: 1px solid #D9E2F0;
                border-radius: 12px;

                min-width: 45px;
                max-width: 45px;

                min-height: 55px;
                max-height: 55px;

                font-size: 22px;
                font-weight: bold;
            }

            QLineEdit#otpBox:hover {
                border: 1px solid #AFC2D8;
            }

            QLineEdit#otpBox:focus {
                border: 2px solid #4589E8;
            }

            QLabel#otpError {
                background-color: transparent;
                color: #D9534F;

                font-size: 11px;
                font-weight: 600;

                padding: 0;
                margin: 0;
            }

            QPushButton#confirmButton {
                background-color: #1961C7;
                color: white;

                border: none;
                border-radius: 14px;

                font-family: "Vazirmatn";
                font-size: 14px;
                font-weight: 700;

                padding: 0;
            }

            QPushButton#confirmButton:hover {
                background-color: #4589E8;
            }

            QPushButton#confirmButton:pressed {
                background-color: #1453AA;
            }

            QLabel#timer {
                color: #4589E8;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton#resendButton {
                background-color: transparent;
                border: none;
                color: #4589E8;
                font-size: 14px;
            }

            QPushButton#resendButton:hover {
                color: #1961C7;
            }

        """)

    # =====================================
    # focus خودکار روی اولین خانه OTP
    # =====================================

    def showEvent(self, event):
        super().showEvent(event)
        # هر بار که پنجره نمایش داده شد، focus روی اولین خانه OTP
        QTimer.singleShot(50, lambda: self.otp_boxes[0].setFocus())

    # =====================================
    # رفتن به خانه بعدی
    # =====================================

    def move_to_next(self, index, text):

        # اگر چیزی وارد نشده
        if not text:
            return

        # پاک کردن خطای قبلی
        self.clear_otp_error()

        # اگر خانه آخر نیست
        if index < len(self.otp_boxes) - 1:

            self.otp_boxes[index + 1].setFocus()

    # =====================================
    # نمایش خطای OTP
    # =====================================

    def show_otp_error(self, message):

        self.otp_error.setText(
            message
        )

        self.otp_error.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self.otp_error.show()

    # =====================================
    # حذف خطای OTP
    # =====================================

    def clear_otp_error(self):

        self.otp_error.clear()

        self.otp_error.hide()

    # =====================================
    # بررسی کد
    # =====================================

    def check_code(self):

        code = ""

        for box in self.otp_boxes:
            code += box.text()

        # اگر هنوز 6 رقم کامل نشده
        if len(code) != 6:

            self.show_otp_error(
                "لطفاً کد تأیید را کامل وارد کن."
            )

            return

        # =====================================
        # بررسی OTP از MySQL
        # =====================================

        result = self.db.fetch_one(
            """
            SELECT otpId
            FROM pending_otps
            WHERE phoneNumber = %s
            AND otpCode = %s
            AND used = '0'
            AND expiresDate >= NOW()
            ORDER BY otpId DESC
            LIMIT 1
            """,
            (
                self.phone_number,
                int(code)
            )
        )

        # کد اشتباه یا منقضی شده
        if result is None:

            self.show_otp_error(
                "کد تأیید وارد شده صحیح نیست."
            )

            return

        # کد درست است
        self.clear_otp_error()

        # =====================================
        # مصرف کردن OTP
        # =====================================

        self.db.execute(
            """
            UPDATE pending_otps
            SET used = '1'
            WHERE otpId = %s
            """,
            (
                result["otpId"],
            )
        )

        # =====================================
        # تغییر شماره از داخل پروفایل
        # =====================================

        if self.change_phone_mode:

            if self.parent_profile is not None:

                self.parent_profile.phone_number = (
                    self.phone_number
                )

                self.parent_profile.phone_value.setText(
                    self.phone_number
                )

                self.parent_profile.show()

                self.parent_profile.raise_()

                self.parent_profile.activateWindow()

            self.close()

            return

        # =====================================
        # بررسی کاربر قبلی
        # =====================================

        user = self.db.fetch_one(
            """
            SELECT userId, name, imageBase64
            FROM users
            WHERE phoneNumber = %s
            LIMIT 1
            """,
            (
                self.phone_number,
            )
        )

        # =====================================
        # اگر کاربر قبلاً وجود دارد
        # =====================================

        if user is not None:

            avatar = user["imageBase64"]

            # ─────────────────────────────────
            # کاربر با پروفایل کامل (خودش ثبت‌نام کرده)
            # مستقیم بره Home
            # ─────────────────────────────────
            if avatar:

                self.open_home(
                    user["name"],
                    avatar
                )

                return

            # ─────────────────────────────────
            # کاربر بدون پروفایل کامل
            # (احتمالاً مالک اضافه کرده)
            # بره Setup بدون پرسیدن شماره تلفن
            # ─────────────────────────────────
            self.profile_window = ProfileSetupWindow(
                phone_number=self.phone_number,
                mode="no_phone"
            )
            self.profile_window.show()
            self.close()

            return

        # =====================================
        # کاربر جدید (خودش با OTP ثبت‌نام می‌کنه)
        # =====================================

        self.profile_window = ProfileSetupWindow(
            phone_number=self.phone_number,
            mode="phone"
        )

        self.profile_window.show()

        self.close()

    # =====================================
    # باز کردن Home
    # =====================================

    def open_home(self, username, avatar):

        self.home_window = HomeWindow(
            self.phone_number,
            username,
            avatar
        )

        self.home_window.show()

        self.close()

    # =====================================
    # انتخاب آواتار برای کاربر قدیمی
    # =====================================

    def show_avatar_selection(self, user_id, username):

        self.avatar_window = QWidget()

        self.avatar_window.setWindowTitle(
            "انتخاب آواتار"
        )

        self.avatar_window.setFixedSize(
            500,
            350
        )

        self.avatar_window.setLayoutDirection(
            Qt.RightToLeft
        )

        layout = QVBoxLayout(
            self.avatar_window
        )

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout.setSpacing(20)

        title = QLabel(
            "آواتارت رو انتخاب کن"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet("""
            QLabel {
                color: #173B67;
                font-family: "Vazirmatn";
                font-size: 22px;
                font-weight: 800;
            }
        """)

        description = QLabel(
            "برای ادامه ورود، یکی از آواتارها را انتخاب کن."
        )

        description.setAlignment(
            Qt.AlignCenter
        )

        description.setStyleSheet("""
            QLabel {
                color: #7A8999;
                font-family: "Vazirmatn";
                font-size: 13px;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(description)

        avatars_layout = QHBoxLayout()

        avatars_layout.setSpacing(30)
        avatars_layout.setAlignment(
            Qt.AlignCenter
        )

        for filename in [
            "men.png",
            "woman.png"
        ]:

            button = QPushButton()

            button.setFixedSize(
                120,
                120
            )

            path = self.avatar_path(
                filename
            )

            pixmap = QPixmap(path)

            if not pixmap.isNull():

                pixmap = pixmap.scaled(
                    90,
                    90,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                button.setIcon(
                    QIcon(pixmap)
                )

                button.setIconSize(
                    QSize(90, 90)
                )

            button.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 2px solid #D5DEE8;
                    border-radius: 60px;
                    padding: 5px;
                }

                QPushButton:hover {
                    background-color: #E8F1FB;
                    border: 3px solid #3978B9;
                }
            """)

            button.clicked.connect(
                lambda checked=False,
                       f=filename:
                self.select_old_user_avatar(
                    user_id,
                    username,
                    f
                )
            )

            avatars_layout.addWidget(
                button
            )

        layout.addLayout(
            avatars_layout
        )

        self.avatar_window.setStyleSheet("""
            QWidget {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }
        """)

        self.avatar_window.show()

    # =====================================
    # مسیر آواتار
    # =====================================

    def avatar_path(self, filename):

        import os

        project_folder = os.path.dirname(
            os.path.abspath(__file__)
        )

        return os.path.join(
            project_folder,
            "avatars",
            filename
        )

    # =====================================
    # ذخیره آواتار کاربر قدیمی
    # =====================================

    def select_old_user_avatar(
        self,
        user_id,
        username,
        filename
    ):

        self.db.execute(
            """
            UPDATE users
            SET imageBase64 = %s
            WHERE userId = %s
            """,
            (
                filename,
                user_id
            )
        )

        self.avatar_window.close()

        self.open_home(
            username,
            filename
        )

    # =====================================
    # ویرایش شماره
    # =====================================

    def edit_phone(self):

        from main import LoginWindow

        self.login_window = LoginWindow(
            change_phone=self.change_phone_mode,
            parent_profile=self.parent_profile
        )

        self.login_window.show()

        self.close()

    # =====================================
    # شروع تایمر
    # =====================================

    def start_timer(self):

        self.remaining_seconds = 45

        self.timer_label.setText("00:45")

        self.timer.start(1000)

    # =====================================
    # آپدیت تایمر
    # =====================================

    def update_timer(self):

        self.remaining_seconds -= 1

        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60

        self.timer_label.setText(
            f"{minutes:02d}:{seconds:02d}"
        )

        if self.remaining_seconds <= 0:

            self.timer.stop()

    # =====================================
    # ارسال مجدد
    # =====================================

    def restart_timer(self):

        self.start_timer()