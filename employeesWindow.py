import os

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QScrollBar
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor

from database import Database
from signals import signals

from addEmployees import AddEmployees

# =========================================================
# ROUND SCROLL BAR
# =========================================================

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

        result = QPixmap(self.avatar_size, self.avatar_size)
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
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self.setPixmap(result)

# =========================================================
# EMPLOYEES WINDOW
# =========================================================

class EmployeesWindow(QWidget):

    def __init__(self, phone_number, complex_id=None):

        super().__init__()

        self.phone_number = phone_number
        self.complex_id = complex_id

        self.db = Database()

        if self.complex_id is None:
            self.find_first_complex()

        self.setWindowTitle("کارمندان")
        self.resize(1000, 700)
        self.setMinimumSize(600, 450)
        self.setLayoutDirection(Qt.RightToLeft)

        self.full_time_hours_per_day = 8
        self.part_time_hours_per_day = 4
        self.default_work_days_per_month = 26

        self.setup_ui()

        signals.employee_added.connect(self.on_employee_changed)
        signals.employee_removed.connect(self.on_employee_changed)
        signals.employee_updated.connect(self.on_employee_changed)

    # =====================================================
    # SIGNAL HANDLER
    # =====================================================

    def on_employee_changed(self, complex_id):
        if complex_id == self.complex_id:
            self.load_employees_from_database()

    # =====================================================
    # FIND FIRST COMPLEX
    # =====================================================

    def find_first_complex(self):

        try:
            user = self.db.fetch_one(
                """
                SELECT userId
                FROM users
                WHERE phoneNumber = %s
                LIMIT 1
                """,
                (self.phone_number,)
            )

            if not user:
                return

            first = self.db.fetch_one(
                """
                SELECT complexId
                FROM complex_members
                WHERE userId = %s
                  AND isActive = '1'
                ORDER BY complexId ASC
                LIMIT 1
                """,
                (user["userId"],)
            )

            if first:
                self.complex_id = first["complexId"]

        except Exception as e:
            print("FIND FIRST COMPLEX ERROR:", e)

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(16)

        # =================================================
        # HEADER
        # =================================================

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setFixedSize(42, 42)
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(3)

        title = QLabel("کارمندان")
        title.setObjectName("pageTitle")

        subtitle = QLabel("مدیریت و مشاهده کارمندان مجموعه")
        subtitle.setObjectName("pageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        add_button = QPushButton("+  افزودن کارمند")
        add_button.setObjectName("addEmployeeButton")
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.setFixedHeight(46)
        add_button.clicked.connect(self.add_employee)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(add_button)

        main_layout.addLayout(header_layout)

        # =================================================
        # EMPLOYEES BOX
        # =================================================

        employees_box = QFrame()
        employees_box.setObjectName("employeesBox")
        employees_box.setAttribute(Qt.WA_StyledBackground, True)

        employees_layout = QVBoxLayout(employees_box)
        employees_layout.setContentsMargins(18, 18, 18, 18)
        employees_layout.setSpacing(8)

        # =================================================
        # SCROLL
        # =================================================

        self.scroll = QScrollArea()
        self.scroll.setObjectName("employeesScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setFrameShape(QFrame.NoFrame)

        scroll_bar = RoundScrollBar(Qt.Vertical)
        self.scroll.setVerticalScrollBar(scroll_bar)

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setAttribute(Qt.WA_TranslucentBackground, True)

        self.employees_layout = QVBoxLayout(scroll_content)
        self.employees_layout.setContentsMargins(4, 4, 16, 4)
        self.employees_layout.setSpacing(10)

        self.scroll.setWidget(scroll_content)

        employees_layout.addWidget(self.scroll)

        main_layout.addWidget(employees_box)

        # =================================================
        # EMPLOYEES
        # =================================================

        self.employees = []

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
            background-color: #FAFCFF;
            border: 1px solid #C9DDF5;
            border-radius: 20px;
        }

        QLabel#employeeName {
            color: #1E2F43;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
            qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
        }

        QLabel#employeeProfession {
            color: #4589E8;
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
        }

        QLabel#employeeJob {
            color: #617287;
            font-size: 11px;
            background: transparent;
            qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
        }

        QLabel#employeeJobValue {
            color: #1E2F43;
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
        }

        QLabel#employeeInfo {
            color: #617287;
            font-size: 10px;
            background: transparent;
            qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
        }

        QLabel#employeeSalary {
            color: #1961C7;
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }

        QFrame#divider {
            background-color: #EEF3FA;
            border: none;
        }

        QLabel#activeStatus {
            color: #238B5B;
            background-color: #E8F7F0;
            border: none;
            border-radius: 13px;
            padding: 0px;
            font-size: 10px;
            font-weight: 600;
        }

        QLabel#inactiveStatus {
            color: #7B8794;
            background-color: #EEF1F5;
            border: none;
            border-radius: 13px;
            padding: 0px;
            font-size: 10px;
            font-weight: 600;
        }

        QPushButton#statusButton {
            background-color: #EAF3FF;
            color: #1961C7;
            border: none;
            border-radius: 13px;
            padding: 0px;
            font-size: 10px;
            font-weight: 600;
        }

        QPushButton#statusButton:hover {
            background-color: #D8E9FF;
            border-radius: 13px;
        }

        QPushButton#statusButton:pressed {
            background-color: #C8DDF5;
            border-radius: 13px;
        }

        QScrollArea#employeesScroll {
            background: transparent;
            border: none;
        }

        QScrollArea#employeesScroll > QWidget > QWidget {
            background: transparent;
        }

        """)

        self.load_employees_from_database()

    # =====================================================
    # LOAD EMPLOYEES FROM DATABASE
    # =====================================================

    def load_employees_from_database(self):

        self.employees = []

        if not self.complex_id:
            print("LOAD EMPLOYEES ERROR: COMPLEX ID IS NONE")
            self.refresh_employees()
            return

        try:
            employees = self.db.fetch_all(
                """
                SELECT
                    cm.memberId,
                    cm.userId,
                    cm.role,
                    cm.isActive,
                    u.name,
                    u.phoneNumber,
                    u.imageBase64,
                    ep.jobTitle,
                    ep.nationalCode,
                    ep.employmentType,
                    ep.salaryType,
                    ep.baseSalary,
                    ep.workDays,
                    ep.workHours,
                    ep.workStartTime,
                    ep.workEndTime,
                    ep.description
                FROM complex_members cm
                INNER JOIN users u
                    ON u.userId = cm.userId
                LEFT JOIN employee_profiles ep
                    ON ep.memberId = cm.memberId
                WHERE cm.complexId = %s
                  AND cm.role IN ('employee', 'both')
                  AND cm.isActive = '1'
                ORDER BY cm.memberId DESC
                """,
                (self.complex_id,)
            )

            for row in employees:

                employment_type = row.get("employmentType")

                if employment_type == "fullTime":
                    work_type = "تمام‌وقت"
                elif employment_type == "partTime":
                    work_type = "پاره‌وقت"
                else:
                    work_type = employment_type or "-"

                salary_type = row.get("salaryType")

                if salary_type == "monthly":
                    salary_type_text = "ماهانه"
                elif salary_type == "daily":
                    salary_type_text = "روزانه"
                elif salary_type == "hourly":
                    salary_type_text = "ساعتی"
                else:
                    salary_type_text = "-"

                is_active = row.get("isActive")

                if str(is_active) == "1":
                    status = "فعال"
                else:
                    status = "غیرفعال"

                start_time = str(row.get("workStartTime") or "")
                end_time = str(row.get("workEndTime") or "")

                if start_time and ":" in start_time:
                    start_time = ":".join(start_time.split(":")[:2])

                if end_time and ":" in end_time:
                    end_time = ":".join(end_time.split(":")[:2])

                if start_time and end_time:
                    work_time_text = f"{start_time} تا {end_time}"
                else:
                    work_time_text = "-"

                employee = {
                    "memberId": row.get("memberId"),
                    "userId": row.get("userId"),
                    "name": row.get("name") or "بدون نام",
                    "position": row.get("jobTitle") or "بدون شغل",
                    "phone": row.get("phoneNumber") or "-",
                    "work_type": work_type,
                    "salary_type": salary_type_text,
                    "salary": float(row.get("baseSalary") or 0),
                    "work_days": float(row.get("workDays") or 0),
                    "work_hours": float(row.get("workHours") or 0),
                    "work_time": work_time_text,
                    "status": status,
                    "avatar": "men.png",
                    "national_code": row.get("nationalCode") or "",
                    "start_time": start_time,
                    "end_time": end_time,
                    "description": row.get("description") or ""
                }

                self.employees.append(employee)

        except Exception as error:
            print("LOAD EMPLOYEES ERROR:")
            print(type(error).__name__)
            print(error)

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
            self.add_employee_card(employee)

        self.employees_layout.addStretch()

    # =====================================================
    # SALARY CALCULATIONS
    # =====================================================

    def calculate_hourly_salary(self, employee):

        salary_type = employee.get("salary_type", "")
        salary = employee.get("salary", 0)
        work_days = employee.get("work_days", 26)
        work_hours = employee.get("work_hours", 8)

        if salary_type == "ساعتی":
            return salary

        if salary_type == "روزانه":
            if work_hours == 0:
                return 0
            return salary / work_hours

        if salary_type == "ماهانه":
            total_hours = work_days * work_hours
            if total_hours == 0:
                return 0
            return salary / total_hours

        return 0

    def calculate_daily_salary(self, employee):

        salary_type = employee.get("salary_type", "")
        salary = employee.get("salary", 0)
        work_hours = employee.get("work_hours", 8)

        if salary_type == "ساعتی":
            return salary * work_hours

        if salary_type == "روزانه":
            return salary

        if salary_type == "ماهانه":
            work_days = employee.get("work_days", 26)
            if work_days == 0:
                return 0
            return salary / work_days

        return 0

    def calculate_monthly_salary(self, employee):

        salary_type = employee.get("salary_type", "")
        salary = employee.get("salary", 0)
        work_days = employee.get("work_days", 26)
        work_hours = employee.get("work_hours", 8)

        if salary_type == "ماهانه":
            return salary

        if salary_type == "روزانه":
            return salary * work_days

        if salary_type == "ساعتی":
            return salary * work_days * work_hours

        return 0

    def calculate_payment(self, employee):

        return {
            "hourly": self.calculate_hourly_salary(employee),
            "daily": self.calculate_daily_salary(employee),
            "monthly": self.calculate_monthly_salary(employee)
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
        card.setObjectName("employeeCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setMinimumHeight(160)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(16)

        # =================================================
        # AVATAR
        # =================================================

        avatar = RoundedAvatar(60)

        avatar_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "avatars",
            employee.get("avatar", "men.png")
        )

        avatar_pixmap = QPixmap(avatar_path)
        avatar.set_avatar(avatar_pixmap)

        card_layout.addWidget(avatar, 0, Qt.AlignTop)

        # =================================================
        # MAIN INFO — همه راست‌چین
        # =================================================

        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent;")

        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignRight)

        name_label = QLabel(employee.get("name", "بدون نام"))
        name_label.setObjectName("employeeName")
        name_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        phone = employee.get("phone", "-")

        phone_row = QLabel(f"{phone}")
        phone_row.setObjectName("employeeProfession")
        phone_row.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)

        job_row = QHBoxLayout()
        job_row.setSpacing(6)

        job_title_label = QLabel("شغل در مجموعه:")
        job_title_label.setObjectName("employeeJob")
        job_title_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        job_value_label = QLabel(employee.get("position", "بدون شغل"))
        job_value_label.setObjectName("employeeJobValue")
        job_value_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        job_row.addWidget(job_title_label)
        job_row.addWidget(job_value_label)
        job_row.addStretch()

        work_type_row = QLabel(
            f"نوع همکاری: {employee.get('work_type', '-')}"
        )
        work_type_row.setObjectName("employeeInfo")
        work_type_row.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        work_time_row = QLabel(
            f"ساعت کاری: {employee.get('work_time', '-')}"
        )
        work_time_row.setObjectName("employeeInfo")
        work_time_row.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        days_hours_row = QLabel(
            f"روز کاری: {employee.get('work_days', 0):g} روز"
            f"   •   "
            f"ساعت روزانه: {employee.get('work_hours', 0):g} ساعت"
        )
        days_hours_row.setObjectName("employeeInfo")
        days_hours_row.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        info_layout.addWidget(name_label)
        info_layout.addWidget(phone_row)
        info_layout.addSpacing(4)
        info_layout.addWidget(divider)
        info_layout.addSpacing(4)
        info_layout.addLayout(job_row)
        info_layout.addWidget(work_type_row)
        info_layout.addWidget(work_time_row)
        info_layout.addWidget(days_hours_row)
        info_layout.addStretch()

        card_layout.addWidget(info_widget, 2)

        # =================================================
        # PAYMENT INFO
        # =================================================

        payment = self.calculate_payment(employee)

        payment_widget = QWidget()
        payment_widget.setStyleSheet("background: transparent;")

        payment_layout = QVBoxLayout(payment_widget)
        payment_layout.setContentsMargins(0, 0, 0, 0)
        payment_layout.setSpacing(4)
        payment_layout.setAlignment(Qt.AlignCenter)

        salary_type_label = QLabel(
            f"پرداخت: {employee.get('salary_type', '-')}"
        )
        salary_type_label.setObjectName("employeeInfo")
        salary_type_label.setAlignment(Qt.AlignCenter)

        monthly_label = QLabel(
            "ماهانه: " + self.format_money(payment["monthly"])
        )
        monthly_label.setObjectName("employeeSalary")
        monthly_label.setAlignment(Qt.AlignCenter)

        daily_label = QLabel(
            "روزانه: " + self.format_money(payment["daily"])
        )
        daily_label.setObjectName("employeeInfo")
        daily_label.setAlignment(Qt.AlignCenter)

        hourly_label = QLabel(
            "ساعتی: " + self.format_money(payment["hourly"])
        )
        hourly_label.setObjectName("employeeInfo")
        hourly_label.setAlignment(Qt.AlignCenter)

        payment_layout.addStretch()
        payment_layout.addWidget(salary_type_label, 0, Qt.AlignHCenter)
        payment_layout.addWidget(monthly_label, 0, Qt.AlignHCenter)
        payment_layout.addWidget(daily_label, 0, Qt.AlignHCenter)
        payment_layout.addWidget(hourly_label, 0, Qt.AlignHCenter)
        payment_layout.addStretch()

        card_layout.addWidget(payment_widget, 2)

        # =================================================
        # STATUS
        # =================================================

        status_widget = QWidget()
        status_widget.setFixedWidth(120)
        status_widget.setStyleSheet("background-color: transparent;")

        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(6)
        status_layout.setAlignment(Qt.AlignCenter)

        status = employee.get("status", "فعال")

        status_label = QLabel(status)
        status_label.setFixedSize(100, 26)
        status_label.setAlignment(Qt.AlignCenter)

        if status == "فعال":
            status_label.setObjectName("activeStatus")
        else:
            status_label.setObjectName("inactiveStatus")

        status_button = QPushButton("تغییر وضعیت")
        status_button.setObjectName("statusButton")
        status_button.setFixedSize(100, 26)
        status_button.setCursor(Qt.PointingHandCursor)

        status_button.clicked.connect(
            lambda checked=False, e=employee:
            self.toggle_employee_status(e)
        )

        status_layout.addStretch()
        status_layout.addWidget(status_label, 0, Qt.AlignHCenter)
        status_layout.addWidget(status_button, 0, Qt.AlignHCenter)
        status_layout.addStretch()

        card_layout.addWidget(status_widget, 0, Qt.AlignVCenter)

        self.employees_layout.addWidget(card)

    # =====================================================
    # TOGGLE STATUS
    # =====================================================

    def toggle_employee_status(self, employee):

        member_id = employee.get("memberId")

        if not member_id:
            return

        current_status = employee.get("status")

        if current_status == "فعال":
            new_status = "0"
            new_status_text = "غیرفعال"
        else:
            new_status = "1"
            new_status_text = "فعال"

        try:
            result = self.db.execute(
                """
                UPDATE complex_members
                SET isActive = %s
                WHERE memberId = %s
                  AND complexId = %s
                """,
                (
                    new_status,
                    member_id,
                    self.complex_id
                )
            )

            if result is None:
                return

            employee["status"] = new_status_text

            self.refresh_employees()

        except Exception as error:
            print("TOGGLE EMPLOYEE STATUS ERROR:")
            print(type(error).__name__)
            print(error)

    # =====================================================
    # ADD EMPLOYEE
    # =====================================================

    def add_employee(self):

        if not self.complex_id:
            print("ADD EMPLOYEE ERROR: COMPLEX ID IS NONE")
            return

        self.add_employee_window = AddEmployees(
            self,
            complex_id=self.complex_id
        )

        self.add_employee_window.setWindowFlags(Qt.Window)

        self.add_employee_window.setGeometry(
            self.x(),
            self.y(),
            self.width(),
            self.height()
        )

        self.add_employee_window.show()