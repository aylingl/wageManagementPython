import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QCheckBox,
    QDialog
)

from PySide6.QtCore import Qt

from database import Database

# =========================================================
# NICE MESSAGE BOX
# =========================================================

class NiceMessageDialog(QDialog):

    def __init__(self, parent, title, text, kind="info"):

        super().__init__(parent)

        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedSize(380, 260)

        if kind == "success":
            icon_char = "✓"
            color = "#16A34A"
            bg = "#DCFCE7"
        elif kind == "error":
            icon_char = "✕"
            color = "#D93025"
            bg = "#FEE2E2"
        elif kind == "warning":
            icon_char = "!"
            color = "#F59E0B"
            bg = "#FEF3C7"
        else:
            icon_char = "i"
            color = "#1961C7"
            bg = "#DBEAFE"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("niceMsgCard")
        card.setStyleSheet("""
            QFrame#niceMsgCard {
                background-color: #FFFFFF;
                border-radius: 22px;
                border: 1px solid #E2EAF4;
            }
        """)

        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)

        icon_label = QLabel(icon_char)
        icon_label.setFixedSize(56, 56)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border-radius: 28px;
                font-size: 26px;
                font-weight: 700;
            }}
        """)

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()

        layout.addLayout(icon_row)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #1E2F43;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
                border: none;
            }
        """)

        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            QLabel {
                color: #526273;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)

        layout.addWidget(text_label)
        layout.addStretch()

        btn = QPushButton("تأیید")
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(120)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                padding: 0px 24px;
            }}
        """)

        btn.clicked.connect(self.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

class NiceMessageBox:

    @staticmethod
    def info(parent, title, text):
        NiceMessageDialog(parent, title, text, "info").exec()

    @staticmethod
    def success(parent, title, text):
        NiceMessageDialog(parent, title, text, "success").exec()

    @staticmethod
    def error(parent, title, text):
        NiceMessageDialog(parent, title, text, "error").exec()

    @staticmethod
    def warning(parent, title, text):
        NiceMessageDialog(parent, title, text, "warning").exec()

# =========================================================
# ADD EMPLOYEES WINDOW
# =========================================================

class AddEmployees(QWidget):

    def __init__(self, parent_window=None, complex_id=None):
        super().__init__(parent_window)

        self.parent_window = parent_window
        self.complex_id = complex_id

        if self.complex_id is None and self.parent_window is not None:
            self.complex_id = getattr(
                self.parent_window,
                "complex_id",
                None
            )

        self.db = Database()

        self.complex_name = "—"

        self.setWindowTitle("افزودن کارمند")
        self.resize(560, 640)
        self.setMinimumSize(500, 550)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("addEmployeesWindow")

        self.load_complex_name()
        self.setup_ui()

    # =========================================================
    # LOAD COMPLEX NAME
    # =========================================================

    def load_complex_name(self):

        if not self.complex_id:
            return

        try:

            row = self.db.fetch_one(
                """
                SELECT name
                FROM complexes
                WHERE complexId = %s
                LIMIT 1
                """,
                (self.complex_id,)
            )

            if row and row.get("name"):
                self.complex_name = row["name"]

        except Exception as e:
            print("LOAD COMPLEX NAME ERROR:", e)

    # =========================================================
    # UI
    # =========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(14)

        # =====================================================
        # HEADER
        # =====================================================

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("افزودن کارمند")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            f"افزودن کارمند به مجموعه: {self.complex_name}"
        )
        subtitle.setObjectName("pageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # =====================================================
        # FORM BOX
        # =====================================================

        form_box = QFrame()
        form_box.setObjectName("formBox")
        form_box.setAttribute(Qt.WA_StyledBackground, True)

        form_layout = QVBoxLayout(form_box)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(8)

        # =====================================================
        # NAME
        # =====================================================

        name_label = QLabel("نام و نام خانوادگی")
        name_label.setObjectName("fieldLabel")

        self.name_input = QLineEdit()
        self.name_input.setObjectName("formInput")
        self.name_input.setPlaceholderText("مثلاً: علی رضایی")
        self.name_input.setFixedHeight(48)
        self.name_input.textChanged.connect(self.clear_name_error)

        self.name_error = QLabel()
        self.name_error.setObjectName("fieldError")
        self.name_error.setFixedHeight(18)
        self.name_error.setWordWrap(True)
        self.name_error.hide()

        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.name_error)

        form_layout.addSpacing(4)

        # =====================================================
        # ROLE
        # =====================================================

        role_label = QLabel(
            f"نقش در مجموعه «{self.complex_name}»"
        )
        role_label.setObjectName("fieldLabel")

        self.role_input = QLineEdit()
        self.role_input.setObjectName("formInput")
        self.role_input.setPlaceholderText(
            "مثلاً: حسابدار، فروشنده، سرپرست"
        )
        self.role_input.setFixedHeight(48)
        self.role_input.textChanged.connect(self.clear_role_error)

        self.role_error = QLabel()
        self.role_error.setObjectName("fieldError")
        self.role_error.setFixedHeight(18)
        self.role_error.setWordWrap(True)
        self.role_error.hide()

        form_layout.addWidget(role_label)
        form_layout.addWidget(self.role_input)
        form_layout.addWidget(self.role_error)

        form_layout.addSpacing(4)

        # =====================================================
        # PHONE
        # =====================================================

        phone_label = QLabel("شماره تلفن")
        phone_label.setObjectName("fieldLabel")

        self.phone_input = QLineEdit()
        self.phone_input.setObjectName("formInput")
        self.phone_input.setPlaceholderText("مثلاً: 09123456789")
        self.phone_input.setFixedHeight(48)
        self.phone_input.setLayoutDirection(Qt.LeftToRight)
        self.phone_input.setMaxLength(11)
        self.phone_input.textChanged.connect(self.clear_phone_error)

        self.phone_error = QLabel()
        self.phone_error.setObjectName("fieldError")
        self.phone_error.setFixedHeight(18)
        self.phone_error.setWordWrap(True)
        self.phone_error.hide()

        form_layout.addWidget(phone_label)
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(self.phone_error)

        form_layout.addSpacing(10)

        # =====================================================
        # PERMISSION CHECKBOX
        # =====================================================

        self.permission_checkbox = QCheckBox(
            "این کارمند اجازه دارد بقیه کارمندان را ببیند"
        )
        self.permission_checkbox.setObjectName("permissionCheckbox")
        self.permission_checkbox.setChecked(True)
        self.permission_checkbox.setCursor(Qt.PointingHandCursor)

        form_layout.addWidget(self.permission_checkbox)

        form_layout.addStretch()

        main_layout.addWidget(form_box, 1)

        # =====================================================
        # BUTTONS
        # =====================================================

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        cancel_button = QPushButton("انصراف")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setFixedHeight(50)
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.close)

        save_button = QPushButton("ذخیره کارمند")
        save_button.setObjectName("saveButton")
        save_button.setFixedHeight(50)
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.clicked.connect(self.save_employee)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet("""

            QWidget#addEmployeesWindow {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }

            QLabel#pageTitle {
                background: transparent;
                color: #17324D;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                background: transparent;
                color: #4589E8;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#fieldLabel {
                background: transparent;
                color: #526273;
                font-size: 13px;
                font-weight: 600;
                padding: 0px;
            }

            QLabel#fieldError {
                background: transparent;
                color: #D93025;
                font-size: 11px;
                font-weight: 600;
                padding: 0px;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
            }

            QPushButton#backButton {
                background-color: #FFFFFF;
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

            QFrame#formBox {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QLineEdit#formInput {
                background: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                padding: 0 16px;
                color: #17324D;
                font-size: 13px;
            }

            QLineEdit#formInput:hover {
                background: #FFFFFF;
                border: 1px solid #C9DDF5;
            }

            QLineEdit#formInput:focus {
                background: #FFFFFF;
                border: 2px solid #4589E8;
            }

            QCheckBox#permissionCheckbox {
                background: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                padding: 14px 16px;
                color: #17324D;
                font-size: 13px;
                font-weight: 600;
                spacing: 12px;
            }

            QCheckBox#permissionCheckbox:hover {
                background: #FFFFFF;
                border: 1px solid #C9DDF5;
            }

            QCheckBox#permissionCheckbox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid #C9D5E2;
                background: #FFFFFF;
            }

            QCheckBox#permissionCheckbox::indicator:checked {
                background: #1961C7;
                border: 2px solid #1961C7;
                image: none;
            }

            QCheckBox#permissionCheckbox::indicator:hover {
                border: 2px solid #4589E8;
            }

            QPushButton#saveButton {
                background: #1961C7;
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 700;
                padding: 0 28px;
            }

            QPushButton#saveButton:hover {
                background: #4589E8;
            }

            QPushButton#saveButton:pressed {
                background: #1453AA;
            }

            QPushButton#cancelButton {
                background: #FFFFFF;
                color: #526273;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 28px;
            }

            QPushButton#cancelButton:hover {
                background: #EAF3FF;
                color: #1961C7;
                border-color: #C9DDF5;
            }

        """)

    # =========================================================
    # ERROR HELPERS
    # =========================================================

    def show_error(self, label, message):

        label.setText(message)
        label.setAlignment(
            Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter
        )
        label.show()

    def clear_error(self, label):

        label.clear()
        label.hide()

    def clear_name_error(self):
        self.clear_error(self.name_error)

    def clear_role_error(self):
        self.clear_error(self.role_error)

    def clear_phone_error(self):
        self.clear_error(self.phone_error)

    def contains_digit(self, text):

        for c in text:
            if c.isdigit():
                return True
        return False

    # =========================================================
    # SAVE
    # =========================================================

    def save_employee(self):

        name = self.name_input.text().strip()
        role = self.role_input.text().strip()
        phone = self.phone_input.text().strip()

        can_see = "1" if self.permission_checkbox.isChecked() else "0"

        # =====================================================
        # NAME VALIDATION
        # =====================================================

        self.clear_error(self.name_error)

        if not name:

            self.show_error(
                self.name_error,
                "لطفاً نام و نام خانوادگی را وارد کنید."
            )

            self.name_input.setFocus()
            return

        if self.contains_digit(name):

            self.show_error(
                self.name_error,
                "نام نباید شامل عدد باشد."
            )

            self.name_input.setFocus()
            return

        # =====================================================
        # ROLE VALIDATION
        # =====================================================

        self.clear_error(self.role_error)

        if not role:

            self.show_error(
                self.role_error,
                "لطفاً نقش کارمند را وارد کنید."
            )

            self.role_input.setFocus()
            return

        if self.contains_digit(role):

            self.show_error(
                self.role_error,
                "نقش نباید شامل عدد باشد."
            )

            self.role_input.setFocus()
            return

        # =====================================================
        # PHONE VALIDATION
        # =====================================================

        self.clear_error(self.phone_error)

        if not phone:

            self.show_error(
                self.phone_error,
                "لطفاً شماره تلفن را وارد کنید."
            )

            self.phone_input.setFocus()
            return

        if not phone.isdigit():

            self.show_error(
                self.phone_error,
                "شماره تلفن باید فقط شامل عدد باشد."
            )

            self.phone_input.setFocus()
            return

        if len(phone) != 11:

            self.show_error(
                self.phone_error,
                "شماره تلفن باید دقیقاً ۱۱ رقم باشد."
            )

            self.phone_input.setFocus()
            return

        if not phone.startswith("09"):

            self.show_error(
                self.phone_error,
                "شماره تلفن باید با ۰۹ شروع شود."
            )

            self.phone_input.setFocus()
            return

        # =====================================================
        # COMPLEX CHECK
        # =====================================================

        if not self.complex_id:

            NiceMessageBox.warning(
                self,
                "خطا",
                "مجموعه فعلی مشخص نیست."
            )
            return

        # =====================================================
        # FIND OR CREATE USER
        # =====================================================

        user = self.db.fetch_one(
            """
            SELECT userId, name
            FROM users
            WHERE phoneNumber = %s
            LIMIT 1
            """,
            (phone,)
        )

        if user:

            user_id = user["userId"]

        else:

            # کاربر جدید
            user_id = self.db.execute(
                """
                INSERT INTO users (
                    name,
                    profession,
                    countryCode,
                    phoneNumber,
                    createdDate,
                    sentOtp,
                    otpSentDateTime,
                    otpUsed,
                    isActive
                )
                VALUES (
                    %s,
                    'unknown',
                    '+98',
                    %s,
                    NOW(),
                    0,
                    NULL,
                    '0',
                    '1'
                )
                """,
                (name, phone)
            )

            if not user_id:

                NiceMessageBox.error(
                    self,
                    "خطا",
                    "ساخت کاربر جدید انجام نشد."
                )
                return

        # =====================================================
        # CHECK EXISTING MEMBER
        # =====================================================

        existing_member = self.db.fetch_one(
            """
            SELECT memberId
            FROM complex_members
            WHERE complexId = %s
              AND userId = %s
            LIMIT 1
            """,
            (self.complex_id, user_id)
        )

        if existing_member:

            NiceMessageBox.warning(
                self,
                "قبلاً عضو است",
                "این کاربر قبلاً در این مجموعه اضافه شده است."
            )
            return

        # =====================================================
        # INSERT MEMBER
        # =====================================================

        member_id = self.db.execute(
            """
            INSERT INTO complex_members (
                complexId,
                userId,
                role,
                joinedDate,
                isActive
            )
            VALUES (%s, %s, 'employee', %s, '1')
            """,
            (
                self.complex_id,
                user_id,
                datetime.now()
            )
        )

        if not member_id:

            NiceMessageBox.error(
                self,
                "خطا",
                "افزودن کارمند به مجموعه انجام نشد."
            )
            return

        # =====================================================
        # INSERT PROFILE
        # =====================================================

        profile_id = self.db.execute(
            """
            INSERT INTO employee_profiles (
                memberId,
                jobTitle,
                employmentType,
                salaryType,
                baseSalary,
                workDays,
                workHours,
                workStartTime,
                workEndTime,
                description,
                canSeeEmployees,
                createdDate
            )
            VALUES (
                %s,
                %s,
                'fullTime',
                'monthly',
                0,
                26,
                8,
                '08:00:00',
                '16:00:00',
                NULL,
                %s,
                NOW()
            )
            """,
            (
                member_id,
                role,
                can_see
            )
        )

        if not profile_id:

            self.db.execute(
                "DELETE FROM complex_members WHERE memberId = %s",
                (member_id,)
            )

            NiceMessageBox.error(
                self,
                "خطا",
                "اطلاعات پروفایل کارمند ذخیره نشد."
            )
            return

        # =====================================================
        # REFRESH PARENT
        # =====================================================

        if self.parent_window is not None:

            if hasattr(self.parent_window, "load_employees_from_database"):
                self.parent_window.load_employees_from_database()

            elif hasattr(self.parent_window, "refresh_employees"):
                self.parent_window.refresh_employees()

        # =====================================================
        # SUCCESS
        # =====================================================

        NiceMessageBox.success(
            self,
            "ثبت موفق",
            f"{name} با موفقیت به مجموعه "
            f"«{self.complex_name}» اضافه شد."
        )

        self.close()