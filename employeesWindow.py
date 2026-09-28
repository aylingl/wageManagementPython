import os

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath

from addEmployees import AddEmployees

# =========================================================
# ROUNDED AVATAR
# =========================================================

class RoundedAvatar(QLabel):

    def __init__(self, size=52, parent=None):
        super().__init__(parent)

        self.avatar_size = size

        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def set_avatar(self, pixmap):

        if pixmap.isNull():
            return

        pixmap = pixmap.scaled(
            self.avatar_size,
            self.avatar_size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        result = QPixmap(
            self.avatar_size,
            self.avatar_size
        )

        result.fill(Qt.transparent)

        painter = QPainter(result)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        path = QPainterPath()

        path.addRoundedRect(
            0,
            0,
            self.avatar_size,
            self.avatar_size,
            self.avatar_size / 2,
            self.avatar_size / 2
        )

        painter.setClipPath(path)

        painter.drawPixmap(
            0,
            0,
            pixmap
        )

        painter.end()

        self.setPixmap(result)

# =========================================================
# EMPLOYEES WINDOW
# =========================================================

class EmployeesWindow(QWidget):

    def __init__(self, phone_number):

        super().__init__()

        self.phone_number = phone_number

        self.setWindowTitle("کارمندان")

        self.setMinimumSize(
            900,
            620
        )

        self.setLayoutDirection(
            Qt.RightToLeft
        )

        # تنظیمات پیش فرض
        self.full_time_hours_per_day = 8
        self.part_time_hours_per_day = 4
        self.default_work_days_per_month = 26

        self.setup_ui()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            28,
            22,
            28,
            22
        )

        main_layout.setSpacing(16)

        # =================================================
        # HEADER
        # =================================================

        header_layout = QHBoxLayout()

        header_layout.setSpacing(12)

        # =================================================
        # BACK BUTTON
        # =================================================

        back_button = QPushButton(
           "›" 
        )

        back_button.setObjectName(
            "backButton"
        )

        back_button.setCursor(
            Qt.PointingHandCursor
        )

        back_button.setFixedSize(
            42,
            42
        )

        back_button.clicked.connect(
            self.close
        )

        header_layout.addWidget(
            back_button
        )

        title_layout = QVBoxLayout()

        title_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        title_layout.setSpacing(3)

        title = QLabel("کارمندان")

        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "مدیریت و مشاهده کارمندان مجموعه"
        )

        subtitle.setObjectName(
            "pageSubtitle"
        )

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        # =================================================
        # ADD BUTTON
        # =================================================

        add_button = QPushButton(
            "+  افزودن کارمند"
        )

        add_button.setObjectName(
            "addEmployeeButton"
        )

        add_button.setCursor(
            Qt.PointingHandCursor
        )

        add_button.setFixedHeight(
            46
        )

        add_button.clicked.connect(
            self.add_employee
        )

        header_layout.addLayout(
            title_layout
        )

        header_layout.addStretch()

        header_layout.addWidget(
            add_button
        )

        main_layout.addLayout(
            header_layout
        )

        # =================================================
        # EMPLOYEES BOX
        # =================================================

        employees_box = QFrame()

        employees_box.setObjectName(
            "employeesBox"
        )

        employees_box.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        employees_layout = QVBoxLayout(
            employees_box
        )

        employees_layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        employees_layout.setSpacing(8)

        # =================================================
        # SCROLL
        # =================================================

        self.scroll = QScrollArea()

        self.scroll.setObjectName(
            "employeesScroll"
        )

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        scroll_content = QWidget()

        scroll_content.setObjectName(
            "scrollContent"
        )

        scroll_content.setAttribute(
            Qt.WA_TranslucentBackground,
            True
        )

        self.employees_layout = QVBoxLayout(
            scroll_content
        )

        self.employees_layout.setContentsMargins(
            4,
            4,
            4,
            4
        )

        self.employees_layout.setSpacing(
            10
        )

        self.scroll.setWidget(
            scroll_content
        )

        employees_layout.addWidget(
            self.scroll
        )

        main_layout.addWidget(
            employees_box
        )

        # =================================================
        # SAMPLE EMPLOYEES
        # =================================================

        self.employees = [

            {
                "name": "علی رضایی",
                "position": "مدیر فروش",
                "work_type": "تمام‌وقت",
                "salary_type": "ماهانه",
                "salary": 25000000,
                "work_days": 26,
                "work_hours": 8,
                "status": "فعال",
                "avatar": "men.png"
            },

            {
                "name": "سارا محمدی",
                "position": "حسابدار",
                "work_type": "پاره‌وقت",
                "salary_type": "ساعتی",
                "salary": 150000,
                "work_days": 20,
                "work_hours": 4,
                "status": "فعال",
                "avatar": "woman.png"
            },

            {
                "name": "محمد احمدی",
                "position": "کارشناس فروش",
                "work_type": "تمام‌وقت",
                "salary_type": "روزانه",
                "salary": 900000,
                "work_days": 18,
                "work_hours": 8,
                "status": "غیرفعال",
                "avatar": "men.png"
            }

        ]

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

        QPushButton#addEmployeeButton {
            background-color: #1961C7;
            color: white;
            border: none;
            border-radius: 18px;
            padding-left: 22px;
            padding-right: 22px;
            font-size: 12px;
            font-weight: 600;
        }

        QPushButton#addEmployeeButton:hover {
            background-color: #4589E8;
        }

        QFrame#employeesBox {
            background-color: white;
            border: 1px solid #E2EAF4;
            border-radius: 28px;
        }

        QWidget#scrollContent {
            background: transparent;
        }

        QFrame#employeeCard {
            background-color: white;
            border: 1px solid #E2EAF4;
            border-radius: 20px;
        }

        QFrame#employeeCard:hover {
            background-color: #EAF3FF;
            border-color: #C9DDF5;
        }

        QLabel#employeeName {
            color: #1E2F43;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        }

        QLabel#employeePosition {
            color: #8290A1;
            font-size: 11px;
            background: transparent;
        }

        QLabel#employeeInfo {
            color: #617287;
            font-size: 10px;
            background: transparent;
        }

        QLabel#employeeSalary {
            color: #1961C7;
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }

        QLabel#activeStatus {
            color: #238B5B;
            background-color: #E8F7F0;
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 9px;
            font-weight: 600;
        }

        QLabel#inactiveStatus {
            color: #7B8794;
            background-color: #EEF1F5;
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 9px;
            font-weight: 600;
        }

        QPushButton#statusButton {
            background-color: #EAF3FF;
            color: #1961C7;
            border: none;
            border-radius: 10px;
            padding: 5px 10px;
            font-size: 9px;
        }

        QPushButton#statusButton:hover {
            background-color: #D8E9FF;
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

        self.refresh_employees()

    # =====================================================
    # REFRESH EMPLOYEES
    # =====================================================

    def refresh_employees(self):

        while self.employees_layout.count():

            item = self.employees_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        for employee in self.employees:

            self.add_employee_card(
                employee
            )

        self.employees_layout.addStretch()

    # =====================================================
    # SALARY CALCULATIONS
    # =====================================================

    def calculate_hourly_salary(self, employee):

        salary_type = employee.get(
            "salary_type",
            ""
        )

        salary = employee.get(
            "salary",
            0
        )

        work_days = employee.get(
            "work_days",
            26
        )

        work_hours = employee.get(
            "work_hours",
            8
        )

        if salary_type == "ساعتی":

            return salary

        if salary_type == "روزانه":

            if work_hours == 0:
                return 0

            return salary / work_hours

        if salary_type == "ماهانه":

            total_hours = (
                work_days *
                work_hours
            )

            if total_hours == 0:
                return 0

            return salary / total_hours

        return 0

    def calculate_daily_salary(self, employee):

        salary_type = employee.get(
            "salary_type",
            ""
        )

        salary = employee.get(
            "salary",
            0
        )

        work_hours = employee.get(
            "work_hours",
            8
        )

        if salary_type == "ساعتی":

            return salary * work_hours

        if salary_type == "روزانه":

            return salary

        if salary_type == "ماهانه":

            work_days = employee.get(
                "work_days",
                26
            )

            if work_days == 0:
                return 0

            return salary / work_days

        return 0

    def calculate_monthly_salary(self, employee):

        salary_type = employee.get(
            "salary_type",
            ""
        )

        salary = employee.get(
            "salary",
            0
        )

        work_days = employee.get(
            "work_days",
            26
        )

        work_hours = employee.get(
            "work_hours",
            8
        )

        if salary_type == "ماهانه":

            return salary

        if salary_type == "روزانه":

            return salary * work_days

        if salary_type == "ساعتی":

            return (
                salary *
                work_days *
                work_hours
            )

        return 0

    def calculate_payment(self, employee):

        return {
            "hourly": self.calculate_hourly_salary(
                employee
            ),
            "daily": self.calculate_daily_salary(
                employee
            ),
            "monthly": self.calculate_monthly_salary(
                employee
            )
        }

    # =====================================================
    # FORMAT MONEY
    # =====================================================

    def format_money(self, amount):

        try:
            return f"{amount:,.0f} تومان"

        except:

            return "0 تومان"

    # =====================================================
    # EMPLOYEE CARD
    # =====================================================

    def add_employee_card(self, employee):

        card = QFrame()

        card.setObjectName(
            "employeeCard"
        )

        card.setMinimumHeight(
            118
        )

        card_layout = QHBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            14,
            12,
            14,
            12
        )

        card_layout.setSpacing(
            14
        )

        # =================================================
        # AVATAR
        # =================================================

        avatar = RoundedAvatar(
            56
        )

        avatar_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "avatars",
            employee.get(
                "avatar",
                "men.png"
            )
        )

        avatar_pixmap = QPixmap(
            avatar_path
        )

        avatar.set_avatar(
            avatar_pixmap
        )

        card_layout.addWidget(
            avatar
        )

        # =================================================
        # MAIN INFO
        # =================================================

        info_layout = QVBoxLayout()

        info_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        info_layout.setSpacing(
            3
        )

        name_label = QLabel(
            employee.get(
                "name",
                "بدون نام"
            )
        )

        name_label.setObjectName(
            "employeeName"
        )

        position_label = QLabel(
            employee.get(
                "position",
                "بدون سمت"
            )
        )

        position_label.setObjectName(
            "employeePosition"
        )

        work_label = QLabel(
            f"نوع همکاری: "
            f"{employee.get('work_type', '-')}"
        )

        work_label.setObjectName(
            "employeeInfo"
        )

        days_hours_label = QLabel(
            f"روز کاری: "
            f"{employee.get('work_days', 0)} روز"
            f"   •   "
            f"ساعت روزانه: "
            f"{employee.get('work_hours', 0)} ساعت"
        )

        days_hours_label.setObjectName(
            "employeeInfo"
        )

        info_layout.addWidget(
            name_label
        )

        info_layout.addWidget(
            position_label
        )

        info_layout.addWidget(
            work_label
        )

        info_layout.addWidget(
            days_hours_label
        )

        info_layout.addStretch()

        card_layout.addLayout(
            info_layout,
            2
        )

        # =================================================
        # PAYMENT INFO
        # =================================================

        payment = self.calculate_payment(
            employee
        )

        payment_layout = QVBoxLayout()

        payment_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        payment_layout.setSpacing(
            3
        )

        salary_type_label = QLabel(
            f"پرداخت: "
            f"{employee.get('salary_type', '-')}"
        )

        salary_type_label.setObjectName(
            "employeeInfo"
        )

        monthly_label = QLabel(
            "ماهانه: "
            + self.format_money(
                payment["monthly"]
            )
        )

        monthly_label.setObjectName(
            "employeeSalary"
        )

        daily_label = QLabel(
            "روزانه: "
            + self.format_money(
                payment["daily"]
            )
        )

        daily_label.setObjectName(
            "employeeInfo"
        )

        hourly_label = QLabel(
            "ساعتی: "
            + self.format_money(
                payment["hourly"]
            )
        )

        hourly_label.setObjectName(
            "employeeInfo"
        )

        payment_layout.addWidget(
            salary_type_label
        )

        payment_layout.addWidget(
            monthly_label
        )

        payment_layout.addWidget(
            daily_label
        )

        payment_layout.addWidget(
            hourly_label
        )

        payment_layout.addStretch()

        card_layout.addLayout(
            payment_layout,
            2
        )

        # =================================================
        # STATUS
        # =================================================

        status_layout = QVBoxLayout()

        status_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        status_layout.setSpacing(
            7
        )

        status = employee.get(
            "status",
            "فعال"
        )

        status_label = QLabel(
            status
        )

        if status == "فعال":

            status_label.setObjectName(
                "activeStatus"
            )

        else:

            status_label.setObjectName(
                "inactiveStatus"
            )

        status_label.setAlignment(
            Qt.AlignCenter
        )

        status_button = QPushButton(
            "تغییر وضعیت"
        )

        status_button.setObjectName(
            "statusButton"
        )

        status_button.setCursor(
            Qt.PointingHandCursor
        )

        status_button.clicked.connect(
            lambda checked=False,
            e=employee:
            self.toggle_employee_status(e)
        )

        status_layout.addWidget(
            status_label
        )

        status_layout.addWidget(
            status_button
        )

        status_layout.addStretch()

        card_layout.addLayout(
            status_layout
        )

        self.employees_layout.addWidget(
            card
        )

    # =====================================================
    # TOGGLE STATUS
    # =====================================================

    def toggle_employee_status(self, employee):

        if employee.get("status") == "فعال":

            employee["status"] = "غیرفعال"

        else:

            employee["status"] = "فعال"

        self.refresh_employees()

    # =====================================================
    # ADD EMPLOYEE
    # =====================================================

    def add_employee(self):

        self.add_employee_window = AddEmployees(
            self
        )

        self.add_employee_window.resize(
            self.size()
        )

        self.add_employee_window.move(
            self.pos()
        )

        self.add_employee_window.show()