
import os
import random
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialog, QFrame,
    QGraphicsDropShadowEffect, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QIcon, QColor

from profileSetupWindow import ProfileSetupWindow
from homeWindow import HomeWindow
from database import Database
from theme import theme_manager

# ═══════════════════════════════════════════════════════
# MODERN MESSAGE DIALOG (پاپ‌آپ مدرن، شیک و قرمز)
# ═══════════════════════════════════════════════════════

class ModernMessageDialog(QDialog):
    def __init__(self, parent, title, text, icon_type="info"):
        super().__init__(parent)
        
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedSize(360, 240)
        
        if parent:
            parent_rect = parent.geometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2
            )
        
        c = theme_manager.colors()
        
        if icon_type == "success":
            icon_char, color, bg = "✓", "#16A34A", "#DCFCE7"
        elif icon_type == "error":
            icon_char, color, bg = "✕", "#D93025", "#FFE5E8"
        elif icon_type == "warning":
            icon_char, color, bg = "!", "#D93025", "#FFE5E8"
        else:
            icon_char, color, bg = "i", "#1961C7", "#DBEAFE"
            
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        
        card = QFrame()
        card.setObjectName("msgCard")
        card.setStyleSheet(f"""
            QFrame#msgCard {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 20px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)
        outer.addWidget(card)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        icon_label = QLabel(icon_char)
        icon_label.setFixedSize(56, 56)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border-radius: 28px;
                font-size: 24px;
                font-weight: 700;
                font-family: "Segoe UI Emoji", "Vazirmatn";
            }}
        """)
        
        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()
        layout.addLayout(icon_row)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_main']};
                font-size: 16px;
                font-weight: 800;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title_label)
        
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_dim']};
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                border: none;
                line-height: 1.5;
            }}
        """)
        layout.addWidget(text_label)
        
        layout.addStretch()
        
        btn = QPushButton("تایید")
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        
        hover_color = "#B71C1C" if icon_type in ("warning", "error") else c['accent_hover']
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 30px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        btn.clicked.connect(self.accept)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

# ═══════════════════════════════════════════════════════
# OTP BOX — جلوگیری از کلیک و تایپ الکی در هر خانه
# ═══════════════════════════════════════════════════════

class OtpBox(QLineEdit):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.otp_boxes_ref = None

    def keyPressEvent(self, event):
        # ═══ Backspace ═══
        if event.key() == Qt.Key_Backspace:
            if self.text() == "":
                if self.otp_boxes_ref and self.index > 0:
                    prev = self.otp_boxes_ref[self.index - 1]
                    prev.setFocus()
                    prev.clear()
                event.accept()
                return
            else:
                self.clear()
                event.accept()
                return

        # ═══ Delete ═══
        if event.key() == Qt.Key_Delete:
            self.clear()
            event.accept()
            return

        # ═══ Left Arrow ═══
        if event.key() == Qt.Key_Left:
            if self.otp_boxes_ref and self.index > 0:
                self.otp_boxes_ref[self.index - 1].setFocus()
            event.accept()
            return

        # ═══ Right Arrow ═══
        if event.key() == Qt.Key_Right:
            if self.otp_boxes_ref and self.index < len(self.otp_boxes_ref) - 1:
                self.otp_boxes_ref[self.index + 1].setFocus()
            event.accept()
            return

        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # هر جا کاربر کلیک کرد، فوکوس بره روی اولین خانه خالی (از چپ)
        if self.otp_boxes_ref:
            for box in self.otp_boxes_ref:
                if box.text() == "":
                    box.setFocus()
                    event.accept()
                    return
            self.otp_boxes_ref[-1].setFocus()
        event.accept()

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

        self.message = QLabel(
            f"کد تأیید به شماره {self.phone_number} ارسال شد"
        )
        self.message.setObjectName("message")
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setWordWrap(True)
        self.message.setFixedWidth(360)

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

            box = OtpBox(i)

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

        for box in self.otp_boxes:
            box.otp_boxes_ref = self.otp_boxes

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

        self.resend_btn = QPushButton("ارسال مجدد کد")
        self.resend_btn.setObjectName("resendButton")
        self.resend_btn.setCursor(Qt.PointingHandCursor)
        self.resend_btn.clicked.connect(self.restart_timer)

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
            self.message,
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
            self.resend_btn,
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

        # ═══ اول چک کن کد اصلاً وجود داره ═══
        row = self.db.fetch_one(
            """
            SELECT otpId, otpCode, expiresDate, used
            FROM pending_otps
            WHERE phoneNumber = %s
            ORDER BY otpId DESC
            LIMIT 1
            """,
            (self.phone_number,)
        )

        if row is None:
            self.show_otp_error(
                "کد تأیید پیدا نشد. لطفاً دوباره درخواست بده."
            )
            return

        # ═══ اگه استفاده شده ═══
        if str(row.get("used") or "0") == "1":
            self.show_otp_error(
                "این کد قبلاً استفاده شده است."
            )
            return

        # ═══ چک انقضا ═══
        expires = row.get("expiresDate")
        is_expired = False
        if isinstance(expires, datetime):
            is_expired = expires < datetime.now()
        elif expires is not None:
            try:
                is_expired = str(expires) < str(datetime.now())
            except Exception:
                pass

        if is_expired:
            self.show_otp_error(
                "کد تأیید منقضی شده است ."
            )
            return

        # ═══ چک درستی کد ═══
        if int(code) != int(row["otpCode"]):

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
                row["otpId"],
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
    # ارسال مجدد کد
    # =====================================

    def restart_timer(self):

        # اگر تایمر هنوز تموم نشده
        if self.remaining_seconds > 0:
            
            ModernMessageDialog(
                self,
                "ارسال کد",
                "کد تایید قبلاً ارسال شده است.\nلطفاً تا پایان زمان تایمر صبر کنید.",
                "warning"
            ).exec()
            
            return

        # ═══ اگر تایمر تموم شده بود، کد جدید بساز ═══
        
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
                "+98", # پیش‌فرض
                self.phone_number,
                otp_code,
                created_date,
                expires_date
            )
        )

        if otp_id is not None:
            print("NEW RESENT OTP:", otp_code) # برای تست تو کنسول
            self.clear_otp_error()
            
            # ریست تایمر ۴۵ ثانیه
            self.start_timer()

            ModernMessageDialog(
                self,
                "ارسال مجدد",
                "کد تایید جدید با موفقیت ارسال شد.",
                "success"
            ).exec()
            
        else:
            self.show_otp_error("خطا در ارسال مجدد کد. لطفاً دوباره تلاش کنید.")
