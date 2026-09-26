from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)

from PySide6.QtCore import Qt, QTimer

from profileSetupWindow import ProfileSetupWindow

class VerifyWindow(QWidget):

    def __init__(self, phone_number):
        super().__init__()

        self.phone_number = phone_number
        self.correct_code = "123456"

        self.setWindowTitle("تأیید شماره موبایل")
        self.resize(1200, 750)

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

        # =========================
        # پیام
        # =========================

        message = QLabel(
            f"کد تأیید به شماره {self.phone_number} ارسال شد"
        )
        message.setObjectName("message")

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

        otp_layout = QHBoxLayout(otp_widget)
        otp_layout.setSpacing(12)

        self.otp_boxes = []

        for _ in range(6):

            box = QLineEdit()

            box.setMaxLength(1)
            box.setAlignment(Qt.AlignCenter)
            box.setObjectName("otpBox")

            # بعد از وارد کردن هر رقم
            # برو به خانه بعدی
            box.textChanged.connect(
                lambda text, current_box=box:
                self.move_to_next(current_box, text)
            )

            self.otp_boxes.append(box)
            otp_layout.addWidget(box)

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
            350,
            150,
            350,
            150
        )

        layout.setSpacing(20)

        layout.addStretch()

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

        layout.addSpacing(20)

        layout.addWidget(
            otp_widget,
            alignment=Qt.AlignCenter
        )

        layout.addWidget(
            self.timer_label,
            alignment=Qt.AlignCenter
        )

        layout.addWidget(
            resend,
            alignment=Qt.AlignCenter
        )

        layout.addStretch()

        self.setLayout(layout)

        # =========================
        # Timer Object
        # =========================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_timer
        )

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

            QLineEdit#otpBox:focus {
                border: 2px solid #4589E8;
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
    # رفتن به خانه بعدی
    # =====================================

    def move_to_next(self, current_box, text):

        # اگر چیزی وارد نشده
        if not text:
            return

        # پیدا کردن شماره خانه فعلی
        index = self.otp_boxes.index(current_box)

        # اگر خانه آخر نیست
        if index < len(self.otp_boxes) - 1:

            self.otp_boxes[index + 1].setFocus()

        # اگر خانه ششم است
        else:

            self.check_code()

    # =====================================
    # بررسی کد
    # =====================================

    def check_code(self):

        code = ""

        for box in self.otp_boxes:
            code += box.text()

        # اگر هنوز 6 رقم کامل نشده
        if len(code) != 6:
            return

        # کد صحیح
        if code == self.correct_code:

            self.profile_window = ProfileSetupWindow(
                self.phone_number
            )

            self.profile_window.show()

            self.close()

    # =====================================
    # ویرایش شماره
    # =====================================

    def edit_phone(self):

        from main import LoginWindow

        self.login_window = LoginWindow()

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