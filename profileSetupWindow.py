import os
import re
import hashlib

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox,
    QGraphicsDropShadowEffect,
    QScrollArea,
    QScrollBar,
    QFileDialog
)

from PySide6.QtCore import Qt, QSize, QRegularExpression
from PySide6.QtGui import (
    QPixmap,
    QIcon,
    QColor,
    QRegularExpressionValidator,
    QPainter
)

from homeWindow import HomeWindow
from database import Database
from imageStorage import save_image, calculate_hash

# ======================================================
# EMAIL VALIDATION
# ======================================================

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ======================================================
# ROUND SCROLL BAR
# ======================================================

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

# ======================================================
# HOVER BUTTON
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

# ======================================================
# PROFILE SETUP WINDOW
# ======================================================

class ProfileSetupWindow(QWidget):

    def __init__(
        self,
        phone_number=None,
        email=None,
        password=None,
        mode="phone"
    ):
        super().__init__()

        self.mode = mode
        self.phone_number = phone_number
        self.email = email
        self.password_raw = password

        self.selected_avatar = None
        self._custom_image_source = None

        self.db = Database()

        self.setWindowTitle("ساخت پروفایل")
        self.resize(1000, 750)
        self.setMinimumSize(550, 550)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setObjectName("profileWindow")

        self.setup_ui()
        self.setStyleSheet(STYLE)

    # ==================================================
    # UI
    # ==================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(8)

        title = QLabel("پروفایلت رو بساز ✨")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(45)
        main_layout.addWidget(title)

        description = QLabel("اطلاعات خودت رو کامل کن")
        description.setObjectName("description")
        description.setAlignment(Qt.AlignCenter)
        description.setFixedHeight(28)
        main_layout.addWidget(description)

        scroll = QScrollArea()
        scroll.setObjectName("profileScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_bar = RoundScrollBar(Qt.Vertical)
        scroll.setVerticalScrollBar(scroll_bar)

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setAttribute(Qt.WA_TranslucentBackground, True)

        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 15, 10, 15)
        scroll_layout.setSpacing(0)
        scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(520)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(30, 60, 90, 35))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(38, 28, 38, 28)
        card_layout.setSpacing(6)

        profile_title = QLabel("اطلاعات پروفایل")
        profile_title.setObjectName("profileTitle")
        card_layout.addWidget(profile_title)
        card_layout.addSpacing(6)

        # ═══════════════════════════════════════════════════
        # Pre-fill برای حالت no_phone (کارمند اضافه‌شده توسط مالک)
        # ═══════════════════════════════════════════════════
        prefill_name = ""
        prefill_job = ""
        self.prefill_member_id = None

        if self.mode == "no_phone" and self.phone_number:
            try:
                existing = self.db.fetch_one(
                    """
                    SELECT u.name, u.userId,
                           cm.memberId,
                           ep.jobTitle
                    FROM users u
                    LEFT JOIN complex_members cm ON cm.userId = u.userId
                    LEFT JOIN employee_profiles ep ON ep.memberId = cm.memberId
                    WHERE u.phoneNumber = %s
                    ORDER BY cm.memberId DESC
                    LIMIT 1
                    """,
                    (self.phone_number,)
                )
                if existing:
                    if existing.get("name"):
                        prefill_name = existing["name"]
                    if existing.get("jobTitle"):
                        prefill_job = existing["jobTitle"]
                    if existing.get("memberId"):
                        self.prefill_member_id = existing["memberId"]
                    print("PREFILL:", prefill_name, "/", prefill_job, "/ memberId:", self.prefill_member_id)
            except Exception as e:
                print("PREFILL ERROR:", e)

        # ── شماره تلفن (فقط حالت ایمیل) ──
        self.phone_input = None
        self.phone_error = None

        if self.mode == "email":

            phone_label = QLabel("شماره تلفن همراه")
            phone_label.setObjectName("fieldTitle")

            self.phone_input = QLineEdit()
            self.phone_input.setObjectName("usernameInput")
            self.phone_input.setPlaceholderText("مثلاً: 09123456789")
            self.phone_input.setFixedHeight(50)
            self.phone_input.setLayoutDirection(Qt.LeftToRight)
            self.phone_input.setMaxLength(11)

            phone_validator = QRegularExpressionValidator(
                QRegularExpression(r"[0-9]*"),
                self.phone_input
            )
            self.phone_input.setValidator(phone_validator)

            self.phone_error = QLabel()
            self.phone_error.setObjectName("fieldError")
            self.phone_error.setFixedHeight(20)
            self.phone_error.setWordWrap(True)
            self.phone_error.hide()

            # ═══ بعد از ساخت error، signal رو وصل کن ═══
            self.phone_input.textChanged.connect(self.validate_phone_live)

            card_layout.addWidget(phone_label)
            card_layout.addWidget(self.phone_input)
            card_layout.addWidget(self.phone_error)

        # ── نام کاربری ──
        username_label = QLabel("نام کاربری")
        username_label.setObjectName("fieldTitle")

        self.username_input = QLineEdit()
        self.username_input.setObjectName("usernameInput")
        self.username_input.setPlaceholderText("مثلاً: Danesh")
        self.username_input.setFixedHeight(50)
        self.username_input.setLayoutDirection(Qt.LeftToRight)

        self.username_error = QLabel()
        self.username_error.setObjectName("fieldError")
        self.username_error.setFixedHeight(20)
        self.username_error.setWordWrap(True)
        self.username_error.hide()

        # ═══ اول error ساخته شد، حالا signal رو وصل کن ═══
        self.username_input.textChanged.connect(self.validate_username)

        # ═══ حالا setText (بعد از ساخت error) ═══
        self.username_input.setText(prefill_name)

        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.username_error)

        # ── شغل / سمت ──
        profession_label = QLabel("شغل / سمت")
        profession_label.setObjectName("fieldTitle")

        self.profession_input = QLineEdit()
        self.profession_input.setObjectName("professionInput")
        self.profession_input.setPlaceholderText("مثلاً: برنامه‌نویس، حسابدار، معلم")
        self.profession_input.setFixedHeight(50)

        self.profession_error = QLabel()
        self.profession_error.setObjectName("fieldError")
        self.profession_error.setFixedHeight(20)
        self.profession_error.setWordWrap(True)
        self.profession_error.hide()

        # ═══ اول error ساخته شد، حالا signal رو وصل کن ═══
        self.profession_input.textChanged.connect(self.validate_profession)

        # ═══ حالا setText ═══
        self.profession_input.setText(prefill_job)

        card_layout.addWidget(profession_label)
        card_layout.addWidget(self.profession_input)
        card_layout.addWidget(self.profession_error)

        # ── کد ملی ──
        national_id_label = QLabel("کد ملی")
        national_id_label.setObjectName("fieldTitle")

        self.national_id_input = QLineEdit()
        self.national_id_input.setObjectName("nationalIdInput")
        self.national_id_input.setPlaceholderText("کد ملی ۱۰ رقمی")
        self.national_id_input.setFixedHeight(50)
        self.national_id_input.setLayoutDirection(Qt.LeftToRight)
        self.national_id_input.setMaxLength(10)

        national_id_validator = QRegularExpressionValidator(
            QRegularExpression(r"[0-9]*"),
            self.national_id_input
        )
        self.national_id_input.setValidator(national_id_validator)

        self.national_id_error = QLabel()
        self.national_id_error.setObjectName("fieldError")
        self.national_id_error.setFixedHeight(20)
        self.national_id_error.setWordWrap(True)
        self.national_id_error.hide()

        # ═══ بعد از error، signal رو وصل کن ═══
        self.national_id_input.textChanged.connect(self.validate_national_id_live)

        card_layout.addWidget(national_id_label)
        card_layout.addWidget(self.national_id_input)
        card_layout.addWidget(self.national_id_error)

        # ── تاریخ تولد ──
        birth_date_label = QLabel("تاریخ تولد")
        birth_date_label.setObjectName("fieldTitle")

        self.birth_date_input = QLineEdit()
        self.birth_date_input.setObjectName("birthDateInput")
        self.birth_date_input.setPlaceholderText("مثلاً: 1380/05/20")
        self.birth_date_input.setFixedHeight(50)
        self.birth_date_input.setLayoutDirection(Qt.LeftToRight)
        self.birth_date_input.setMaxLength(10)

        birth_date_validator = QRegularExpressionValidator(
            QRegularExpression(r"[0-9/]*"),
            self.birth_date_input
        )
        self.birth_date_input.setValidator(birth_date_validator)

        self.birth_date_error = QLabel()
        self.birth_date_error.setObjectName("fieldError")
        self.birth_date_error.setFixedHeight(20)
        self.birth_date_error.setWordWrap(True)
        self.birth_date_error.hide()

        # ═══ بعد از error، signal رو وصل کن ═══
        self.birth_date_input.textChanged.connect(self.validate_birth_date_live)

        card_layout.addWidget(birth_date_label)
        card_layout.addWidget(self.birth_date_input)
        card_layout.addWidget(self.birth_date_error)

        # ── آواتار پیش‌فرض ──
        avatar_label = QLabel("آواتار خودت رو انتخاب کن")
        avatar_label.setObjectName("fieldTitle")
        card_layout.addWidget(avatar_label)

        avatars_widget = QWidget()
        avatars_widget.setStyleSheet("background: transparent;")

        avatars_layout = QHBoxLayout(avatars_widget)
        avatars_layout.setContentsMargins(0, 4, 0, 4)
        avatars_layout.setSpacing(35)
        avatars_layout.setAlignment(Qt.AlignCenter)

        self.avatar_buttons = []

        for filename in ["men.png", "woman.png"]:
            button = QPushButton()
            button.setObjectName("avatarButton")
            button.setFixedSize(90, 90)

            path = self.avatar_path(filename)
            pixmap = QPixmap(path)

            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    74, 74,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                button.setIcon(QIcon(pixmap))
                button.setIconSize(QSize(74, 74))

            button.clicked.connect(
                lambda checked=False, f=filename: self.select_avatar(f)
            )

            avatars_layout.addWidget(button)
            self.avatar_buttons.append((filename, button))

        card_layout.addWidget(avatars_widget)

        # ═══════════════════════════════════════
        # 📁 انتخاب عکس از دستگاه
        # ═══════════════════════════════════════
        browse_label = QLabel("یا عکس واقعی خودت رو از دستگاه انتخاب کن")
        browse_label.setObjectName("fieldHint")
        browse_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(browse_label)

        self.browse_button = QPushButton("📁  انتخاب عکس از دستگاه")
        self.browse_button.setObjectName("browseButton")
        self.browse_button.setFixedHeight(46)
        self.browse_button.setCursor(Qt.PointingHandCursor)
        self.browse_button.clicked.connect(self.browse_avatar)
        card_layout.addWidget(self.browse_button)

        self.custom_preview = QLabel()
        self.custom_preview.setObjectName("customAvatarPreview")
        self.custom_preview.setFixedSize(90, 90)
        self.custom_preview.setAlignment(Qt.AlignCenter)
        self.custom_preview.hide()
        card_layout.addWidget(self.custom_preview, 0, Qt.AlignCenter)

        self.custom_name = QLabel()
        self.custom_name.setObjectName("customAvatarName")
        self.custom_name.setAlignment(Qt.AlignCenter)
        self.custom_name.hide()
        card_layout.addWidget(self.custom_name)

        self.avatar_error = QLabel()
        self.avatar_error.setObjectName("fieldError")
        self.avatar_error.setFixedHeight(20)
        self.avatar_error.setWordWrap(True)
        self.avatar_error.hide()

        card_layout.addWidget(self.avatar_error)

        card_layout.addSpacing(12)

        self.continue_button = HoverButton("ادامه و ورود به سامانه  →")
        self.continue_button.setObjectName("continueButton")
        self.continue_button.setFixedHeight(56)
        self.continue_button.clicked.connect(self.finish_profile)

        card_layout.addWidget(self.continue_button)

        scroll_layout.addWidget(card)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

    # ==========================================
    # مسیر آواتار پیش‌فرض
    # ==========================================

    def avatar_path(self, filename):
        project_folder = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(project_folder, "avatars", filename)

    # ============================================
    # انتخاب آواتار پیش‌فرض
    # ============================================

    def select_avatar(self, filename):
        self.selected_avatar = filename
        self._custom_image_source = None

        for avatar_filename, button in self.avatar_buttons:
            button.setProperty("selected", avatar_filename == filename)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

        if hasattr(self, "custom_preview"):
            self.custom_preview.hide()
        if hasattr(self, "custom_name"):
            self.custom_name.hide()

        self.clear_field_error(self.avatar_error)

    # ============================================
    # 📁 انتخاب عکس از دستگاه
    # ============================================

    def browse_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب عکس پروفایل",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.gif)"
        )

        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(
                self,
                "خطا",
                "فایل انتخابی یک عکس معتبر نیست."
            )
            return

        self._custom_image_source = file_path
        self.selected_avatar = None

        preview = pixmap.scaled(
            80, 80,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.custom_preview.setPixmap(preview)
        self.custom_preview.show()

        file_name = os.path.basename(file_path)
        if len(file_name) > 28:
            file_name = file_name[:25] + "..."
        self.custom_name.setText(f"✓ {file_name}")
        self.custom_name.show()

        for avatar_filename, button in self.avatar_buttons:
            button.setProperty("selected", False)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

        self.clear_field_error(self.avatar_error)

    # ============================================
    # اعتبارسنجی کد ملی
    # ============================================

    def is_valid_national_id(self, national_id):
        if len(national_id) != 10:
            return False
        if not national_id.isdigit():
            return False
        if len(set(national_id)) == 1:
            return False

        digits = [int(d) for d in national_id]
        first_nine = digits[:9]
        control_digit = digits[9]

        total = 0
        for index in range(9):
            weight = 10 - index
            total += first_nine[index] * weight

        remainder = total % 11

        if remainder < 2:
            calculated_digit = remainder
        else:
            calculated_digit = 11 - remainder

        return control_digit == calculated_digit

    def validate_username(self, text):
        # ═══ محافظت: اگه error_label ساخته نشده، برگرد ═══
        if not hasattr(self, "username_error"):
            return

        if not text:
            self.clear_field_error(self.username_error)
            return
        for character in text:
            if character.isdigit():
                self.show_field_error(
                    self.username_error,
                    "نام کاربری نباید شامل عدد باشد."
                )
                return
        self.clear_field_error(self.username_error)

    def validate_profession(self, text):
        # ═══ محافظت ═══
        if not hasattr(self, "profession_error"):
            return

        if not text:
            self.clear_field_error(self.profession_error)
            return
        for character in text:
            if character.isdigit():
                self.show_field_error(
                    self.profession_error,
                    "شغل نباید شامل عدد باشد."
                )
                return
        self.clear_field_error(self.profession_error)

    def validate_national_id_live(self, text):
        if not hasattr(self, "national_id_error"):
            return

        if not text:
            self.clear_field_error(self.national_id_error)
            return
        if not text.isdigit():
            self.show_field_error(
                self.national_id_error,
                "کد ملی باید فقط شامل عدد باشد."
            )
            return
        if len(text) < 10:
            self.clear_field_error(self.national_id_error)
            return
        if not self.is_valid_national_id(text):
            self.show_field_error(
                self.national_id_error,
                "کد ملی وارد شده معتبر نیست."
            )
            return
        self.clear_field_error(self.national_id_error)

    def validate_birth_date_live(self, text):
        if not hasattr(self, "birth_date_error"):
            return

        if not text:
            self.clear_field_error(self.birth_date_error)
            return
        if len(text) < 10:
            self.clear_field_error(self.birth_date_error)
            return
        if not self.is_valid_jalali_date(text):
            self.show_field_error(
                self.birth_date_error,
                "تاریخ تولد معتبر نیست."
            )
            return
        self.clear_field_error(self.birth_date_error)

    def validate_phone_live(self, text):
        if not self.phone_error:
            return

        if not text:
            self.clear_field_error(self.phone_error)
            return

        if not text.isdigit():
            self.show_field_error(
                self.phone_error,
                "شماره تلفن باید فقط شامل عدد باشد."
            )
            return

        if len(text) != 11:
            self.clear_field_error(self.phone_error)
            return

        if not text.startswith("09"):
            self.show_field_error(
                self.phone_error,
                "شماره تلفن باید با ۰۹ شروع شود."
            )
            return

        self.clear_field_error(self.phone_error)

    def is_valid_jalali_date(self, date_string):
        if len(date_string) != 10:
            return False
        if date_string[4] != "/":
            return False
        if date_string[7] != "/":
            return False

        year_text = date_string[0:4]
        month_text = date_string[5:7]
        day_text = date_string[8:10]

        if not year_text.isdigit() or not month_text.isdigit() or not day_text.isdigit():
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
            if (year % 33) in [1, 5, 9, 13, 17, 22, 26, 30]:
                max_day = 30
            else:
                max_day = 29

        if day < 1 or day > max_day:
            return False

        return True

    def show_field_error(self, error_label, message):
        error_label.setText(message)
        error_label.setAlignment(
            Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter
        )
        error_label.show()

    def clear_field_error(self, error_label):
        error_label.clear()
        error_label.hide()

    # ==========================================
    # ذخیره آواتار نهایی + محاسبه هش
    # ==========================================

    def _resolve_final_avatar(self):
        if not self._custom_image_source:
            return self.selected_avatar, None

        file_hash = calculate_hash(self._custom_image_source)
        print("IMAGE HASH:", file_hash)

        if not file_hash:
            return "men.png", None

        existing = None
        try:
            existing = self.db.fetch_one(
                """
                SELECT imageBase64
                FROM users
                WHERE imageHash = %s
                  AND imageBase64 IS NOT NULL
                  AND imageBase64 != ''
                LIMIT 1
                """,
                (file_hash,)
            )
            print("DB LOOKUP RESULT:", existing)
        except Exception as e:
            print("DB LOOKUP ERROR (imageHash column?):", e)

        if existing and existing.get("imageBase64"):
            print("REUSING EXISTING PATH:", existing["imageBase64"])
            return existing["imageBase64"], file_hash

        dest = save_image(self._custom_image_source, file_hash)
        print("SAVE IMAGE RESULT:", dest)

        if dest:
            return dest, file_hash

        return "men.png", None

    # ==========================================
    # ادامه
    # ==========================================

    def finish_profile(self):

        username = self.username_input.text().strip()
        profession = self.profession_input.text().strip()
        national_id = self.national_id_input.text().strip()
        birth_date_string = self.birth_date_input.text().strip()

        if not username:
            self.show_field_error(self.username_error, "لطفاً نام کاربری خودت را وارد کن.")
            self.username_input.setFocus()
            return

        for character in username:
            if character.isdigit():
                self.show_field_error(self.username_error, "نام کاربری نباید شامل عدد باشد.")
                self.username_input.setFocus()
                return

        self.clear_field_error(self.username_error)

        if not profession:
            self.show_field_error(self.profession_error, "لطفاً شغل خودت را وارد کن.")
            self.profession_input.setFocus()
            return

        for character in profession:
            if character.isdigit():
                self.show_field_error(self.profession_error, "شغل نباید شامل عدد باشد.")
                self.profession_input.setFocus()
                return

        letter_count = sum(1 for c in profession if c.isalpha())
        if letter_count < 3:
            self.show_field_error(self.profession_error, "شغل باید حداقل ۳ حرف داشته باشد.")
            self.profession_input.setFocus()
            return

        self.clear_field_error(self.profession_error)

        if not national_id:
            self.show_field_error(self.national_id_error, "لطفاً کد ملی خودت را وارد کن.")
            self.national_id_input.setFocus()
            return

        if not national_id.isdigit() or len(national_id) != 10:
            self.show_field_error(self.national_id_error, "کد ملی باید ۱۰ رقم باشد.")
            self.national_id_input.setFocus()
            return

        if not self.is_valid_national_id(national_id):
            self.show_field_error(self.national_id_error, "کد ملی وارد شده معتبر نیست.")
            self.national_id_input.setFocus()
            return

        self.clear_field_error(self.national_id_error)

        if not birth_date_string:
            self.show_field_error(self.birth_date_error, "لطفاً تاریخ تولد خودت را وارد کن.")
            self.birth_date_input.setFocus()
            return

        if not self.is_valid_jalali_date(birth_date_string):
            self.show_field_error(self.birth_date_error, "تاریخ تولد معتبر نیست.")
            self.birth_date_input.setFocus()
            return

        self.clear_field_error(self.birth_date_error)

        if not self.selected_avatar and not self._custom_image_source:
            self.show_field_error(
                self.avatar_error,
                "لطفاً یکی از آواتارها را انتخاب کن یا عکس خودت رو آپلود کن."
            )
            return

        self.clear_field_error(self.avatar_error)

        final_avatar, final_avatar_hash = self._resolve_final_avatar()
        print("FINAL AVATAR:", final_avatar)
        print("FINAL HASH:", final_avatar_hash)

        # ═══════════════════════════════════════
        # حالت no_phone (کارمند اضافه‌شده توسط مالک)
        # ═══════════════════════════════════════
        if self.mode == "no_phone":

            existing_national_id = self.db.fetch_one(
                """
                SELECT userId FROM users
                WHERE nationalId = %s AND phoneNumber != %s
                LIMIT 1
                """,
                (national_id, self.phone_number)
            )

            if existing_national_id:
                self.show_field_error(
                    self.national_id_error,
                    "این کد ملی قبلاً ثبت شده است."
                )
                self.national_id_input.setFocus()
                return

            existing_user = self.db.fetch_one(
                "SELECT userId FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )

            if not existing_user:
                QMessageBox.warning(self, "خطا", "کاربر یافت نشد.")
                return

            result = self.db.execute(
                """
                UPDATE users
                SET name = %s,
                    nationalId = %s,
                    birthDate = %s,
                    imageBase64 = %s,
                    imageHash = %s
                WHERE phoneNumber = %s
                """,
                (
                    username,
                    national_id,
                    birth_date_string,
                    final_avatar,
                    final_avatar_hash,
                    self.phone_number
                )
            )

            if result is None:
                QMessageBox.critical(self, "خطا", "بروزرسانی پروفایل انجام نشد.")
                return

            if self.prefill_member_id:
                try:
                    self.db.execute(
                        """
                        UPDATE employee_profiles
                        SET jobTitle = %s
                        WHERE memberId = %s
                        """,
                        (profession, self.prefill_member_id)
                    )
                except Exception as e:
                    print("UPDATE JOBTITLE ERROR:", e)

            self.home_window = HomeWindow(
                self.phone_number,
                username,
                final_avatar
            )
            self.home_window.show()
            self.close()
            return

        # ═══════════════════════════════════════
        # حالت ایمیل (گوگل)
        # ═══════════════════════════════════════
        if self.mode == "email":

            phone_value = self.phone_input.text().strip()

            if not phone_value:
                self.show_field_error(
                    self.phone_error,
                    "لطفاً شماره تلفن همراه را وارد کن."
                )
                self.phone_input.setFocus()
                return

            if not phone_value.isdigit() or len(phone_value) != 11:
                self.show_field_error(
                    self.phone_error,
                    "شماره تلفن باید ۱۱ رقم باشد."
                )
                self.phone_input.setFocus()
                return

            if not phone_value.startswith("09"):
                self.show_field_error(
                    self.phone_error,
                    "شماره تلفن باید با ۰۹ شروع شود."
                )
                self.phone_input.setFocus()
                return

            self.clear_field_error(self.phone_error)

            existing_national_id = self.db.fetch_one(
                "SELECT userId FROM users WHERE nationalId = %s LIMIT 1",
                (national_id,)
            )

            if existing_national_id:
                self.show_field_error(
                    self.national_id_error,
                    "این کد ملی قبلاً ثبت شده است."
                )
                self.national_id_input.setFocus()
                return

            existing_phone = self.db.fetch_one(
                "SELECT userId FROM users WHERE phoneNumber = %s LIMIT 1",
                (phone_value,)
            )

            if existing_phone:
                self.show_field_error(
                    self.phone_error,
                    "این شماره تلفن قبلاً ثبت شده است."
                )
                self.phone_input.setFocus()
                return

            password_hash = hashlib.sha256(
                self.password_raw.encode("utf-8")
            ).hexdigest()

            user_id = self.db.execute(
                """
                INSERT INTO users (
                    name, profession, nationalId, birthDate,
                    countryCode, phoneNumber, email, passwordHash,
                    createdDate, sentOtp, otpUsed, isActive,
                    imageBase64, imageHash
                )
                VALUES (
                    %s, %s, %s, %s,
                    '+98', %s, %s, %s,
                    NOW(), 0, '1', '1',
                    %s, %s
                )
                """,
                (
                    username,
                    profession,
                    national_id,
                    birth_date_string,
                    phone_value,
                    self.email,
                    password_hash,
                    final_avatar,
                    final_avatar_hash
                )
            )

            if user_id is None:
                QMessageBox.critical(self, "خطا", "ثبت اطلاعات پروفایل انجام نشد.")
                return

            self.home_window = HomeWindow(
                phone_value,
                username,
                final_avatar
            )
            self.home_window.show()
            self.close()
            return

        # ═══════════════════════════════════════
        # حالت phone (کاربر جدید)
        # ═══════════════════════════════════════

        existing_national_id = self.db.fetch_one(
            "SELECT userId FROM users WHERE nationalId = %s LIMIT 1",
            (national_id,)
        )

        if existing_national_id:
            self.show_field_error(
                self.national_id_error,
                "این کد ملی قبلاً ثبت شده است."
            )
            self.national_id_input.setFocus()
            return

        otp_data = self.db.fetch_one(
            """
            SELECT countryCode, otpCode, createdDate
            FROM pending_otps
            WHERE phoneNumber = %s AND used = '1'
            ORDER BY otpId DESC
            LIMIT 1
            """,
            (self.phone_number,)
        )

        if not otp_data:
            QMessageBox.warning(self, "خطا", "اطلاعات تأیید شماره تلفن پیدا نشد.")
            return

        user_id = self.db.execute(
            """
            INSERT INTO users (
                name, profession, nationalId, birthDate,
                countryCode, phoneNumber,
                createdDate, sentOtp, otpSentDateTime,
                otpUsed, isActive, imageBase64, imageHash
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s,
                NOW(), %s, %s,
                '1', '1', %s, %s
            )
            """,
            (
                username,
                profession,
                national_id,
                birth_date_string,
                otp_data["countryCode"],
                self.phone_number,
                otp_data["otpCode"],
                otp_data["createdDate"],
                final_avatar,
                final_avatar_hash
            )
        )

        if user_id is None:
            QMessageBox.critical(self, "خطا", "ثبت اطلاعات پروفایل انجام نشد.")
            return

        self.home_window = HomeWindow(
            self.phone_number,
            username,
            final_avatar
        )
        self.home_window.show()
        self.close()

# ======================================================
# STYLE
# ======================================================

STYLE = """

QWidget {
    font-family: "Vazirmatn";
    color: #243447;
}

QWidget#profileWindow {
    background-color: #F5F8FC;
}

QLabel#title {
    background-color: transparent;
    color: #173B67;
    font-size: 28px;
    font-weight: 800;
}

QLabel#description {
    background-color: transparent;
    color: #7A8999;
    font-size: 13px;
}

QScrollArea#profileScroll {
    background: transparent;
    border: none;
}

QScrollArea#profileScroll > QWidget {
    background: transparent;
    border: none;
}

QWidget#scrollContent {
    background: transparent;
}

QFrame#card {
    background-color: #FFFFFF;
    border: 1px solid #E2EAF4;
    border-radius: 26px;
}

QLabel#profileTitle {
    background-color: transparent;
    color: #183B61;
    font-size: 17px;
    font-weight: 800;
}

QLabel#fieldTitle {
    background-color: transparent;
    color: #536779;
    font-size: 13px;
    font-weight: 600;
}

QLabel#fieldHint {
    background-color: transparent;
    color: #98A2B3;
    font-size: 11px;
    font-weight: 500;
    padding: 4px 0px 0px 0px;
}

QLabel#fieldError {
    background-color: transparent;
    color: #D9534F;
    font-size: 11px;
    font-weight: 600;
    padding: 0px;
    qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
}

QLineEdit#usernameInput,
QLineEdit#professionInput,
QLineEdit#nationalIdInput,
QLineEdit#birthDateInput {
    background-color: #F5F8FC;
    color: #243B53;
    border: 1px solid #DCE6F2;
    border-radius: 13px;
    padding: 0 17px;
    font-size: 13px;
}

QLineEdit#usernameInput:hover,
QLineEdit#professionInput:hover,
QLineEdit#nationalIdInput:hover,
QLineEdit#birthDateInput:hover {
    background-color: #FFFFFF;
    border: 1px solid #C9DDF5;
}

QLineEdit#usernameInput:focus,
QLineEdit#professionInput:focus,
QLineEdit#nationalIdInput:focus,
QLineEdit#birthDateInput:focus {
    background-color: #FFFFFF;
    border: 2px solid #4B82C3;
}

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

QPushButton#browseButton {
    background-color: #FFFFFF;
    color: #3478C9;
    border: 2px dashed #8DA8C2;
    border-radius: 13px;
    font-family: "Vazirmatn";
    font-size: 13px;
    font-weight: 700;
    padding: 0px 20px;
}

QPushButton#browseButton:hover {
    background-color: #E8F1FB;
    border: 2px dashed #3978B9;
    color: #1961C7;
}

QLabel#customAvatarPreview {
    background-color: #FFFFFF;
    border: 3px solid #3978B9;
    border-radius: 45px;
    padding: 4px;
}

QLabel#customAvatarName {
    background-color: transparent;
    color: #16A34A;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 0px;
}

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