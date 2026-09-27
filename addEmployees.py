import os

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QComboBox,
    QLineEdit,
    QMessageBox
)

from PySide6.QtCore import Qt

# =========================================================
# ADD EMPLOYEES
# =========================================================

class AddEmployees(QWidget):

    def __init__(self, parent_window=None):

        super().__init__()

        self.parent_window = parent_window

        self.setWindowTitle("افزودن کارمند")

        self.setMinimumSize(
            650,
            700
        )

        self.setLayoutDirection(
            Qt.RightToLeft
        )

        self.setup_ui()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            28,
            24,
            28,
            24
        )

        main_layout.setSpacing(
            16
        )

        # =================================================
        # HEADER
        # =================================================

        title = QLabel(
            "افزودن کارمند"
        )

        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "اطلاعات کارمند جدید را وارد کنید"
        )

        subtitle.setObjectName(
            "pageSubtitle"
        )

        main_layout.addWidget(
            title
        )

        main_layout.addWidget(
            subtitle
        )

        # =================================================
        # SCROLL
        # =================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        scroll.setFrameShape(
            QFrame.NoFrame
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
            5,
            5,
            5
        )

        content_layout.setSpacing(
            14
        )

        scroll.setWidget(
            content
        )

        main_layout.addWidget(
            scroll
        )

        # =================================================
        # PERSONAL INFORMATION
        # =================================================

        personal_box = self.create_section(
            "اطلاعات کارمند"
        )

        personal_layout = personal_box.layout()

        self.name_input = self.create_input(
            "نام و نام خانوادگی"
        )

        self.position_input = self.create_input(
            "سمت شغلی"
        )

        self.phone_input = self.create_input(
            "شماره موبایل"
        )

        self.national_code_input = self.create_input(
            "کد ملی"
        )

        personal_layout.addWidget(
            self.name_input
        )

        personal_layout.addWidget(
            self.position_input
        )

        personal_layout.addWidget(
            self.phone_input
        )

        personal_layout.addWidget(
            self.national_code_input
        )

        # =================================================
        # WORK INFORMATION
        # =================================================

        work_box = self.create_section(
            "اطلاعات کاری"
        )

        work_layout = work_box.layout()

        self.work_type_combo = QComboBox()

        self.work_type_combo.addItems([
            "تمام‌وقت",
            "پاره‌وقت"
        ])

        self.work_type_combo.setObjectName(
            "modernCombo"
        )

        self.work_days_input = self.create_input(
            "تعداد روز کاری در ماه"
        )

        self.work_hours_input = self.create_input(
            "ساعت کاری در روز"
        )

        self.start_time_input = self.create_input(
            "ساعت شروع کار"
        )

        self.end_time_input = self.create_input(
            "ساعت پایان کار"
        )

        work_layout.addWidget(
            self.create_label(
                "نوع همکاری"
            )
        )

        work_layout.addWidget(
            self.work_type_combo
        )

        work_layout.addWidget(
            self.work_days_input
        )

        work_layout.addWidget(
            self.work_hours_input
        )

        work_layout.addWidget(
            self.start_time_input
        )

        work_layout.addWidget(
            self.end_time_input
        )

        # =================================================
        # PAYMENT
        # =================================================

        payment_box = self.create_section(
            "نحوه پرداخت"
        )

        payment_layout = payment_box.layout()

        self.salary_type_combo = QComboBox()

        self.salary_type_combo.addItems([
            "ماهانه",
            "روزانه",
            "ساعتی"
        ])

        self.salary_type_combo.setObjectName(
            "modernCombo"
        )

        self.salary_input = self.create_input(
            "مبلغ پرداختی"
        )

        self.payment_description_input = self.create_input(
            "توضیحات پرداخت"
        )

        payment_layout.addWidget(
            self.create_label(
                "نوع پرداخت"
            )
        )

        payment_layout.addWidget(
            self.salary_type_combo
        )

        payment_layout.addWidget(
            self.salary_input
        )

        payment_layout.addWidget(
            self.payment_description_input
        )

        # =================================================
        # STATUS
        # =================================================

        status_box = self.create_section(
            "وضعیت کارمند"
        )

        status_layout = status_box.layout()

        self.status_combo = QComboBox()

        self.status_combo.addItems([
            "فعال",
            "غیرفعال"
        ])

        self.status_combo.setObjectName(
            "modernCombo"
        )

        status_layout.addWidget(
            self.create_label(
                "وضعیت"
            )
        )

        status_layout.addWidget(
            self.status_combo
        )

        # =================================================
        # ADD SECTIONS
        # =================================================

        content_layout.addWidget(
            personal_box
        )

        content_layout.addWidget(
            work_box
        )

        content_layout.addWidget(
            payment_box
        )

        content_layout.addWidget(
            status_box
        )

        content_layout.addStretch()

        # =================================================
        # BUTTONS
        # =================================================

        buttons_layout = QHBoxLayout()

        buttons_layout.setSpacing(
            10
        )

        back_button = QPushButton(
            "بازگشت"
        )

        back_button.setObjectName(
            "backButton"
        )

        back_button.setCursor(
            Qt.PointingHandCursor
        )

        back_button.setFixedHeight(
            46
        )

        back_button.clicked.connect(
            self.close
        )

        save_button = QPushButton(
            "ثبت کارمند"
        )

        save_button.setObjectName(
            "saveButton"
        )

        save_button.setCursor(
            Qt.PointingHandCursor
        )

        save_button.setFixedHeight(
            46
        )

        save_button.clicked.connect(
            self.save_employee
        )

        buttons_layout.addWidget(
            back_button
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
            font-family: "Vazirmatn";
        }

        QLabel#pageTitle {
            color: #1E2F43;
            font-size: 21px;
            font-weight: 700;
            background: transparent;
        }

        QLabel#pageSubtitle {
            color: #8290A1;
            font-size: 11px;
            background: transparent;
        }

        QFrame#section {
            background-color: white;
            border: 1px solid #E2EAF4;
            border-radius: 22px;
        }

        QLabel#sectionTitle {
            color: #1E2F43;
            font-size: 13px;
            font-weight: 700;
            background: transparent;
        }

        QLabel#fieldLabel {
            color: #617287;
            font-size: 10px;
            background: transparent;
        }

        QLineEdit {
            background-color: #F8FAFD;
            border: 1px solid #DCE6F1;
            border-radius: 13px;
            padding: 10px 13px;
            color: #1E2F43;
            font-size: 11px;
        }

        QLineEdit:focus {
            border: 1px solid #4589E8;
            background-color: white;
        }

        QComboBox#modernCombo {
            background-color: #F8FAFD;
            border: 1px solid #DCE6F1;
            border-radius: 13px;
            padding: 10px 13px;
            color: #1E2F43;
            font-size: 11px;
        }

        QComboBox#modernCombo:focus {
            border: 1px solid #4589E8;
        }

        QComboBox#modernCombo::drop-down {
            border: none;
            width: 30px;
        }

        QComboBox#modernCombo QAbstractItemView {
            background-color: white;
            border: 1px solid #DCE6F1;
            selection-background-color: #EAF3FF;
            selection-color: #1961C7;
            padding: 5px;
        }

        QPushButton#saveButton {
            background-color: #1961C7;
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 11px;
            font-weight: 600;
        }

        QPushButton#saveButton:hover {
            background-color: #4589E8;
        }

        QPushButton#backButton {
            background-color: white;
            color: #1961C7;
            border: 1px solid #DCE6F1;
            border-radius: 16px;
            font-size: 11px;
            font-weight: 600;
        }

        QPushButton#backButton:hover {
            background-color: #EAF3FF;
        }

        QScrollBar:vertical {
            background-color: #E8EEF6;
            width: 10px;
            border-radius: 5px;
            margin: 3px;
        }

        QScrollBar::handle:vertical {
            background-color: #4589E8;
            min-height: 35px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #1961C7;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        """)

    # =====================================================
    # CREATE SECTION
    # =====================================================

    def create_section(self, title):

        box = QFrame()

        box.setObjectName(
            "section"
        )

        layout = QVBoxLayout(
            box
        )

        layout.setContentsMargins(
            18,
            16,
            18,
            16
        )

        layout.setSpacing(
            9
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(
            title_label
        )

        return box

    # =====================================================
    # CREATE INPUT
    # =====================================================

    def create_input(self, placeholder):

        line_edit = QLineEdit()

        line_edit.setPlaceholderText(
            placeholder
        )

        line_edit.setFixedHeight(
            42
        )

        return line_edit

    # =====================================================
    # CREATE LABEL
    # =====================================================

    def create_label(self, text):

        label = QLabel(
            text
        )

        label.setObjectName(
            "fieldLabel"
        )

        return label

    # =====================================================
    # SAVE EMPLOYEE
    # =====================================================

    def save_employee(self):

        name = self.name_input.text().strip()

        position = self.position_input.text().strip()

        phone = self.phone_input.text().strip()

        national_code = (
            self.national_code_input
            .text()
            .strip()
        )

        salary = (
            self.salary_input
            .text()
            .strip()
        )

        work_days = (
            self.work_days_input
            .text()
            .strip()
        )

        work_hours = (
            self.work_hours_input
            .text()
            .strip()
        )

        # =================================================
        # VALIDATION
        # =================================================

        if not name:

            QMessageBox.warning(
                self,
                "اطلاعات ناقص",
                "لطفاً نام و نام خانوادگی را وارد کنید."
            )

            return

        if not position:

            QMessageBox.warning(
                self,
                "اطلاعات ناقص",
                "لطفاً سمت شغلی را وارد کنید."
            )

            return

        if not salary:

            QMessageBox.warning(
                self,
                "اطلاعات ناقص",
                "لطفاً مبلغ پرداختی را وارد کنید."
            )

            return

        try:

            salary_value = int(
                salary.replace(
                    ",",
                    ""
                )
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "مبلغ نامعتبر",
                "مبلغ پرداختی باید عددی باشد."
            )

            return

        try:

            work_days_value = int(
                work_days
            ) if work_days else 26

        except ValueError:

            QMessageBox.warning(
                self,
                "مقدار نامعتبر",
                "تعداد روز کاری باید عددی باشد."
            )

            return

        try:

            work_hours_value = float(
                work_hours
            ) if work_hours else 8

        except ValueError:

            QMessageBox.warning(
                self,
                "مقدار نامعتبر",
                "ساعت کاری باید عددی باشد."
            )

            return

        # =================================================
        # EMPLOYEE DATA
        # =================================================

        employee = {

            "name": name,

            "position": position,

            "work_type":
                self.work_type_combo.currentText(),

            "salary_type":
                self.salary_type_combo.currentText(),

            "salary":
                salary_value,

            "work_days":
                work_days_value,

            "work_hours":
                work_hours_value,

            "status":
                self.status_combo.currentText(),

            "avatar":
                "men.png",

            "phone":
                phone,

            "national_code":
                national_code,

            "start_time":
                self.start_time_input.text().strip(),

            "end_time":
                self.end_time_input.text().strip(),

            "payment_description":
                self.payment_description_input.text().strip()

        }

        # =================================================
        # ADD TO EMPLOYEES WINDOW
        # =================================================

        if self.parent_window is not None:

            self.parent_window.employees.append(
                employee
            )

            self.parent_window.refresh_employees()

        # =================================================
        # CLOSE
        # =================================================

        self.close()