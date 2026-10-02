import os

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QDialog, QLineEdit,
    QComboBox, QTimeEdit, QCheckBox
)

from PySide6.QtCore import Qt, QTime, QPoint, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QRegion

from database import Database
from signals import signals
from theme import theme_manager
from i18n import tr, set_language, get_language

from addEmployees import AddEmployees, NiceMessageBox, RoundedComboBox

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
        c = theme_manager.colors()

        track_width = 6
        track_x = (self.width() - track_width) / 2
        track_top = 6
        track_bottom = self.height() - 6
        track_height = track_bottom - track_top

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(c["bg_input"]))
        painter.drawRoundedRect(
            int(track_x), int(track_top),
            track_width, int(track_height),
            track_width / 2, track_width / 2
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
        painter.setBrush(QColor(c["accent"]))
        painter.drawRoundedRect(
            int(handle_x), int(handle_y),
            handle_width, int(handle_height),
            handle_width / 2, handle_width / 2
        )

# =========================================================
# CIRCLE MENU BUTTON
# =========================================================

class CircleMenuButton(QPushButton):

    def __init__(self, size=36, parent=None):
        super().__init__("⋮", parent)
        self._size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        self.setAutoFillBackground(False)
        self._apply_mask()

    def _apply_mask(self):
        self.setMask(QRegion(self.rect(), QRegion.Ellipse))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_mask()

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
            0, 0,
            self.avatar_size, self.avatar_size,
            self.avatar_size / 2, self.avatar_size / 2
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

        self.setWindowTitle(tr("employees_title"))
        self.resize(1000, 700)
        self.setMinimumSize(600, 450)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("employeesWindow")

        self.setup_ui()

        signals.employee_added.connect(self.on_employee_changed)
        signals.employee_removed.connect(self.on_employee_changed)
        signals.employee_updated.connect(self.on_employee_changed)

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)

    # =====================================================
    # THEME / LANGUAGE
    # =====================================================

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()
        self.refresh_employees()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("employees_title"))
        QTimer.singleShot(0, self._rebuild)

    def _rebuild(self):
        old = self.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
        self.setup_ui()

    def on_employee_changed(self, complex_id):
        if complex_id == self.complex_id:
            self.load_employees_from_database()

    # =====================================================
    # FIND FIRST COMPLEX
    # =====================================================

    def find_first_complex(self):
        try:
            user = self.db.fetch_one(
                "SELECT userId FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if not user:
                return

            first = self.db.fetch_one(
                """
                SELECT complexId FROM complex_members
                WHERE userId = %s AND isActive = '1'
                ORDER BY complexId ASC LIMIT 1
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

        # HEADER
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setFixedSize(42, 42)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(3)

        title = QLabel(tr("employees_title"))
        title.setObjectName("pageTitle")

        subtitle = QLabel(tr("employees_subtitle"))
        subtitle.setObjectName("pageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        add_button = QPushButton(tr("add_employee"))
        add_button.setObjectName("addEmployeeButton")
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.setFixedHeight(46)
        add_button.setAttribute(Qt.WA_StyledBackground, True)
        add_button.clicked.connect(self.add_employee)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(add_button)

        main_layout.addLayout(header_layout)

        # EMPLOYEES BOX
        employees_box = QFrame()
        employees_box.setObjectName("employeesBox")
        employees_box.setAttribute(Qt.WA_StyledBackground, True)

        employees_layout = QVBoxLayout(employees_box)
        employees_layout.setContentsMargins(18, 18, 18, 18)
        employees_layout.setSpacing(8)

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

        self.employees = []

        self.apply_stylesheet()
        self.load_employees_from_database()

    # =====================================================
    # APPLY STYLESHEET
    # =====================================================

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""

        QWidget#employeesWindow {{
            background-color: {c['bg_main']};
            font-family: "Vazirmatn";
            color: {c['text_main']};
        }}

        QWidget#employeesWindow QLabel {{
            background: transparent;
        }}

        QLabel#pageTitle {{
            color: {c['text_main']};
            font-size: 21px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#pageSubtitle {{
            color: {c['text_dim']};
            font-size: 11px;
            background: transparent;
        }}

        QPushButton#backButton {{
            background-color: {c['bg_card']};
            color: {c['accent']};
            border: 1px solid {c['border']};
            border-radius: 21px;
            font-size: 22px;
            font-weight: 600;
            padding: 0px;
        }}

        QPushButton#backButton:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['border_hover']};
        }}

        QPushButton#addEmployeeButton {{
            background-color: {c['accent']};
            color: white;
            border: none;
            border-radius: 23px;
            padding-left: 22px;
            padding-right: 22px;
            font-size: 12px;
            font-weight: 600;
        }}

        QPushButton#addEmployeeButton:hover {{
            background-color: {c['accent_hover']};
        }}

        QFrame#employeesBox {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 28px;
        }}

        QWidget#scrollContent {{
            background: transparent;
        }}

        QFrame#employeeCard {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 20px;
        }}

        QFrame#employeeCard:hover {{
            background-color: {c['bg_hover']};
            border: 1px solid {c['accent']};
            border-radius: 20px;
        }}

        QLabel#employeeName {{
            color: {c['text_main']};
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#employeeProfession {{
            color: {c['accent']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }}

        QLabel#employeeJob {{
            color: {c['text_dim']};
            font-size: 11px;
            background: transparent;
        }}

        QLabel#employeeJobValue {{
            color: {c['text_main']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }}

        QLabel#employeeInfo {{
            color: {c['text_dim']};
            font-size: 10px;
            background: transparent;
        }}

        QLabel#employeeSalary {{
            color: {c['accent']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }}

        QFrame#divider {{
            background-color: {c['border']};
            border: none;
        }}

        QLabel#activeStatus {{
            color: #238B5B;
            background-color: {c['success_bg']};
            border: none;
            border-radius: 13px;
            padding: 0px;
            font-size: 10px;
            font-weight: 600;
        }}

        QLabel#inactiveStatus {{
            color: {c['text_dim']};
            background-color: {c['bg_input']};
            border: none;
            border-radius: 13px;
            padding: 0px;
            font-size: 10px;
            font-weight: 600;
        }}

        QPushButton#statusButton {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border: none;
            border-radius: 13px;
            padding: 0px;
            font-size: 10px;
            font-weight: 600;
        }}

        QPushButton#statusButton:hover {{
            background-color: {c['bg_hover']};
            border-radius: 13px;
        }}

        QPushButton#menuCircleBtn {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border: none;
            border-radius: 18px;
            padding: 0px;
            font-size: 18px;
            font-weight: 900;
        }}

        QPushButton#menuCircleBtn:hover {{
            background-color: {c['bg_hover']};
        }}

        QScrollArea#employeesScroll {{
            background: transparent;
            border: none;
        }}

        QScrollArea#employeesScroll > QWidget > QWidget {{
            background: transparent;
        }}

        """)

    # =====================================================
    # LOAD EMPLOYEES
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
                    cm.memberId, cm.userId, cm.role, cm.isActive,
                    u.name, u.phoneNumber,
                    ep.jobTitle, ep.nationalCode, ep.employmentType,
                    ep.salaryType, ep.baseSalary, ep.workDays, ep.workHours,
                    ep.workStartTime, ep.workEndTime, ep.description,
                    ep.canSeeEmployees, ep.allowOvertime
                FROM complex_members cm
                INNER JOIN users u ON u.userId = cm.userId
                LEFT JOIN employee_profiles ep ON ep.memberId = cm.memberId
                WHERE cm.complexId = %s
                  AND cm.role IN ('employee', 'both')
                  AND cm.isActive = '1'
                ORDER BY cm.memberId DESC
                """,
                (self.complexId if hasattr(self, "complexId") else self.complex_id,)
            )

            for row in employees:
                employment_type = row.get("employmentType")
                if employment_type == "fullTime":
                    work_type = tr("full_time")
                elif employment_type == "partTime":
                    work_type = tr("part_time")
                else:
                    work_type = employment_type or "-"

                salary_type = row.get("salaryType")
                if salary_type == "monthly":
                    salary_type_text = tr("monthly")
                elif salary_type == "daily":
                    salary_type_text = tr("daily")
                elif salary_type == "hourly":
                    salary_type_text = tr("hourly")
                else:
                    salary_type_text = "-"

                is_active = row.get("isActive")
                status = tr("active_status") if str(is_active) == "1" else tr("inactive_status")

                start_time = str(row.get("workStartTime") or "")
                end_time = str(row.get("workEndTime") or "")

                if start_time and ":" in start_time:
                    start_time = ":".join(start_time.split(":")[:2])
                if end_time and ":" in end_time:
                    end_time = ":".join(end_time.split(":")[:2])

                if start_time and end_time:
                    work_time_text = f"{start_time} - {end_time}"
                else:
                    work_time_text = "-"

                employee = {
                    "memberId": row.get("memberId"),
                    "userId": row.get("userId"),
                    "name": row.get("name") or tr("no_name"),
                    "position": row.get("jobTitle") or tr("no_job"),
                    "phone": row.get("phoneNumber") or "-",
                    "work_type": work_type,
                    "salary_type": salary_type_text,
                    "salary_type_value": salary_type or "monthly",
                    "employment_type_value": employment_type or "fullTime",
                    "salary": float(row.get("baseSalary") or 0),
                    "work_days": float(row.get("workDays") or 26),
                    "work_hours": float(row.get("workHours") or 8),
                    "work_time": work_time_text,
                    "work_start_time": row.get("workStartTime"),
                    "work_end_time": row.get("workEndTime"),
                    "status": status,
                    "avatar": "men.png",
                    "national_code": row.get("nationalCode") or "",
                    "start_time": start_time,
                    "end_time": end_time,
                    "description": row.get("description") or "",
                    "can_see_employees": row.get("canSeeEmployees") or "0",
                    "allow_overtime": row.get("allowOvertime") or "1"
                }

                self.employees.append(employee)

        except Exception as error:
            print("LOAD EMPLOYEES ERROR:", error)

        self.refresh_employees()

    # =====================================================
    # REFRESH
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

        if salary_type == tr("hourly"):
            return salary
        if salary_type == tr("daily"):
            if work_hours == 0:
                return 0
            return salary / work_hours
        if salary_type == tr("monthly"):
            total_hours = work_days * work_hours
            if total_hours == 0:
                return 0
            return salary / total_hours
        return 0

    def calculate_daily_salary(self, employee):
        salary_type = employee.get("salary_type", "")
        salary = employee.get("salary", 0)
        work_hours = employee.get("work_hours", 8)

        if salary_type == tr("hourly"):
            return salary * work_hours
        if salary_type == tr("daily"):
            return salary
        if salary_type == tr("monthly"):
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

        if salary_type == tr("monthly"):
            return salary
        if salary_type == tr("daily"):
            return salary * work_days
        if salary_type == tr("hourly"):
            return salary * work_days * work_hours
        return 0

    def calculate_payment(self, employee):
        return {
            "hourly": self.calculate_hourly_salary(employee),
            "daily": self.calculate_daily_salary(employee),
            "monthly": self.calculate_monthly_salary(employee)
        }

    def format_money(self, amount):
        try:
            return f"{amount:,.0f} {tr('toman')}"
        except Exception:
            return f"0 {tr('toman')}"

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

        # AVATAR
        avatar = RoundedAvatar(60)
        avatar_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "avatars",
            employee.get("avatar", "men.png")
        )
        avatar_pixmap = QPixmap(avatar_path)
        avatar.set_avatar(avatar_pixmap)

        card_layout.addWidget(avatar, 0, Qt.AlignTop)

        # MAIN INFO
        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent;")

        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignRight)

        name_label = QLabel(employee.get("name", tr("no_name")))
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

        job_title_label = QLabel(tr("job_in_group"))
        job_title_label.setObjectName("employeeJob")
        job_title_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        job_value_label = QLabel(employee.get("position", tr("no_job")))
        job_value_label.setObjectName("employeeJobValue")
        job_value_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        job_row.addWidget(job_title_label)
        job_row.addWidget(job_value_label)
        job_row.addStretch()

        work_type_row = QLabel(f"{tr('employment_type')}: {employee.get('work_type', '-')}")
        work_type_row.setObjectName("employeeInfo")
        work_type_row.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        work_time_row = QLabel(f"{tr('work_hours_label')} {employee.get('work_time', '-')}")
        work_time_row.setObjectName("employeeInfo")
        work_time_row.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        days_hours_row = QLabel(
            f"{tr('work_days_label')} {employee.get('work_days', 0):g}   •   "
            f"{tr('hours_per_day')}: {employee.get('work_hours', 0):g}"
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

        # PAYMENT INFO
        payment = self.calculate_payment(employee)

        payment_widget = QWidget()
        payment_widget.setStyleSheet("background: transparent;")

        payment_layout = QVBoxLayout(payment_widget)
        payment_layout.setContentsMargins(0, 0, 0, 0)
        payment_layout.setSpacing(4)
        payment_layout.setAlignment(Qt.AlignCenter)

        salary_type_label = QLabel(
            f"{tr('payment_type_label')} {employee.get('salary_type', '-')}"
        )
        salary_type_label.setObjectName("employeeInfo")
        salary_type_label.setAlignment(Qt.AlignCenter)

        monthly_label = QLabel(
            f"{tr('monthly_label')} {self.format_money(payment['monthly'])}"
        )
        monthly_label.setObjectName("employeeSalary")
        monthly_label.setAlignment(Qt.AlignCenter)

        daily_label = QLabel(
            f"{tr('daily_label')} {self.format_money(payment['daily'])}"
        )
        daily_label.setObjectName("employeeInfo")
        daily_label.setAlignment(Qt.AlignCenter)

        hourly_label = QLabel(
            f"{tr('hourly_label')} {self.format_money(payment['hourly'])}"
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

        # RIGHT: MENU + STATUS
        right_widget = QWidget()
        right_widget.setFixedWidth(120)
        right_widget.setStyleSheet("background-color: transparent;")

        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        menu_btn = CircleMenuButton(36)
        menu_btn.setObjectName("menuCircleBtn")
        menu_btn.setAttribute(Qt.WA_StyledBackground, True)
        menu_btn.clicked.connect(
            lambda checked=False, e=employee: self.open_edit_dialog(e)
        )

        menu_row = QHBoxLayout()
        menu_row.setContentsMargins(0, 0, 0, 0)
        menu_row.addStretch()
        menu_row.addWidget(menu_btn)

        right_layout.addLayout(menu_row)
        right_layout.addStretch()

        status = employee.get("status", tr("active_status"))

        status_label = QLabel(status)
        status_label.setFixedSize(100, 26)
        status_label.setAlignment(Qt.AlignCenter)

        if status == tr("active_status"):
            status_label.setObjectName("activeStatus")
        else:
            status_label.setObjectName("inactiveStatus")

        status_button = QPushButton(tr("change_status"))
        status_button.setObjectName("statusButton")
        status_button.setFixedSize(100, 26)
        status_button.setCursor(Qt.PointingHandCursor)

        status_button.clicked.connect(
            lambda checked=False, e=employee: self.toggle_employee_status(e)
        )

        right_layout.addWidget(status_label, 0, Qt.AlignHCenter)
        right_layout.addWidget(status_button, 0, Qt.AlignHCenter)
        right_layout.addStretch()

        card_layout.addWidget(right_widget, 0, Qt.AlignTop)

        self.employees_layout.addWidget(card)

    # =====================================================
    # TOGGLE STATUS
    # =====================================================

    def toggle_employee_status(self, employee):

        member_id = employee.get("memberId")
        if not member_id:
            return

        current_status = employee.get("status")

        if current_status == tr("active_status"):
            new_status = "0"
            new_status_text = tr("inactive_status")
        else:
            new_status = "1"
            new_status_text = tr("active_status")

        try:
            result = self.db.execute(
                """
                UPDATE complex_members
                SET isActive = %s
                WHERE memberId = %s AND complexId = %s
                """,
                (new_status, member_id, self.complex_id)
            )
            if result is None:
                return
            employee["status"] = new_status_text
            self.refresh_employees()
            signals.data_changed.emit("jobs")
        except Exception as error:
            print("TOGGLE EMPLOYEE STATUS ERROR:", error)

    # =====================================================
    # EDIT DIALOG
    # =====================================================

    def open_edit_dialog(self, employee):

        member_id = employee.get("memberId")
        if not member_id:
            return

        row = self.db.fetch_one(
            """
            SELECT ep.jobTitle, ep.employmentType, ep.salaryType,
                   ep.baseSalary, ep.workDays, ep.workHours,
                   ep.workStartTime, ep.workEndTime,
                   ep.canSeeEmployees, ep.allowOvertime
            FROM employee_profiles ep
            WHERE ep.memberId = %s
            LIMIT 1
            """,
            (member_id,)
        )

        if not row:
            NiceMessageBox.error(
                self, tr("error"),
                tr("err_loading_groups")
            )
            return

        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("edit_salary_info"))
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(500)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(10)

        name = employee.get("name") or tr("no_name")

        title = QLabel(f"{tr('edit_salary_info')} — {name}")
        title.setStyleSheet(f"color: {c['text_main']}; font-size: 15px; font-weight: 700; background: transparent;")
        layout.addWidget(title)
        layout.addSpacing(4)

        # JOB TITLE
        job_lbl = QLabel(tr("role_in_group"))
        job_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        job_input = QLineEdit()
        job_input.setText(row.get("jobTitle") or "")
        job_input.setFixedHeight(44)

        layout.addWidget(job_lbl)
        layout.addWidget(job_input)

        # EMPLOYMENT TYPE
        emp_lbl = QLabel(tr("employment_type"))
        emp_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        emp_combo = RoundedComboBox()
        emp_combo.setFixedHeight(44)
        emp_combo.addItem(tr("full_time"), "fullTime")
        emp_combo.addItem(tr("part_time"), "partTime")

        current_emp = row.get("employmentType") or "fullTime"
        for i in range(emp_combo.count()):
            if emp_combo.itemData(i) == current_emp:
                emp_combo.setCurrentIndex(i)
                break

        layout.addWidget(emp_lbl)
        layout.addWidget(emp_combo)

        # SALARY TYPE
        st_lbl = QLabel(tr("salary_type"))
        st_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        st_combo = RoundedComboBox()
        st_combo.setFixedHeight(44)
        st_combo.addItem(tr("monthly"), "monthly")
        st_combo.addItem(tr("daily"), "daily")
        st_combo.addItem(tr("hourly"), "hourly")

        current_st = row.get("salaryType") or "monthly"
        for i in range(st_combo.count()):
            if st_combo.itemData(i) == current_st:
                st_combo.setCurrentIndex(i)
                break

        layout.addWidget(st_lbl)
        layout.addWidget(st_combo)

        # BASE SALARY
        sal_lbl = QLabel(tr("amount_label"))
        sal_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")

        sal_input = QLineEdit()
        sal_input.setText(str(int(float(row.get("baseSalary") or 0))))
        sal_input.setFixedHeight(44)
        sal_input.setLayoutDirection(Qt.LeftToRight)

        layout.addWidget(sal_lbl)
        layout.addWidget(sal_input)

        # DAYS + HOURS
        dh_row = QHBoxLayout()
        dh_row.setSpacing(10)

        d_col = QVBoxLayout()
        d_lbl = QLabel(tr("days_per_month"))
        d_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")
        d_input = QLineEdit()
        d_input.setText(str(int(float(row.get("workDays") or 26))))
        d_input.setFixedHeight(44)
        d_input.setLayoutDirection(Qt.LeftToRight)
        d_col.addWidget(d_lbl)
        d_col.addWidget(d_input)

        h_col = QVBoxLayout()
        h_lbl = QLabel(tr("hours_per_day"))
        h_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")
        h_input = QLineEdit()
        h_input.setText(str(int(float(row.get("workHours") or 8))))
        h_input.setFixedHeight(44)
        h_input.setLayoutDirection(Qt.LeftToRight)
        h_col.addWidget(h_lbl)
        h_col.addWidget(h_input)

        dh_row.addLayout(d_col, 1)
        dh_row.addLayout(h_col, 1)
        layout.addLayout(dh_row)

        # TIMES
        te_row = QHBoxLayout()
        te_row.setSpacing(10)

        st_col = QVBoxLayout()
        st_lbl2 = QLabel(tr("start_time"))
        st_lbl2.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")
        start_te = QTimeEdit()
        start_te.setDisplayFormat("HH:mm")
        start_te.setFixedHeight(44)

        ws = row.get("workStartTime")
        if ws:
            try:
                if hasattr(ws, "seconds"):
                    start_te.setTime(QTime(ws.seconds // 3600, (ws.seconds % 3600) // 60))
                else:
                    parts = str(ws).split(":")
                    start_te.setTime(QTime(int(parts[0]), int(parts[1])))
            except Exception:
                start_te.setTime(QTime(8, 0))
        else:
            start_te.setTime(QTime(8, 0))

        st_col.addWidget(st_lbl2)
        st_col.addWidget(start_te)

        en_col = QVBoxLayout()
        en_lbl = QLabel(tr("end_time"))
        en_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 12px; font-weight: 600; background: transparent;")
        end_te = QTimeEdit()
        end_te.setDisplayFormat("HH:mm")
        end_te.setFixedHeight(44)

        we = row.get("workEndTime")
        if we:
            try:
                if hasattr(we, "seconds"):
                    end_te.setTime(QTime(we.seconds // 3600, (we.seconds % 3600) // 60))
                else:
                    parts = str(we).split(":")
                    end_te.setTime(QTime(int(parts[0]), int(parts[1])))
            except Exception:
                end_te.setTime(QTime(16, 0))
        else:
            end_te.setTime(QTime(16, 0))

        en_col.addWidget(en_lbl)
        en_col.addWidget(end_te)

        te_row.addLayout(st_col, 1)
        te_row.addLayout(en_col, 1)
        layout.addLayout(te_row)

        # CHECKBOXES
        ot_check = QCheckBox(tr("allow_overtime_check"))
        ot_check.setCursor(Qt.PointingHandCursor)
        ot_check.setChecked(str(row.get("allowOvertime") or "1") == "1")

        see_check = QCheckBox(tr("can_see_employees_check"))
        see_check.setCursor(Qt.PointingHandCursor)
        see_check.setChecked(str(row.get("canSeeEmployees") or "0") == "1")

        layout.addSpacing(4)
        layout.addWidget(ot_check)
        layout.addWidget(see_check)

        # BUTTONS
        layout.addSpacing(8)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        cancel_btn = QPushButton(tr("cancel"))
        cancel_btn.setFixedHeight(46)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_input']};
                color: {c['text_dim']};
                border: 1px solid {c['border']};
                border-radius: 23px;
                padding: 0 26px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {c['bg_hover']}; }}
        """)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = QPushButton(tr("save"))
        save_btn.setFixedHeight(46)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 23px;
                padding: 0 30px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {c['accent_hover']}; }}
        """)

        def on_save():
            job_text = job_input.text().strip()
            sal_text = sal_input.text().strip()
            d_text = d_input.text().strip()
            h_text = h_input.text().strip()
            st_val = st_combo.currentData()
            emp_val = emp_combo.currentData()

            if not job_text:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_job_required"))
                return

            try:
                sal_val = float(sal_text.replace(",", "").replace("٬", ""))
            except ValueError:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_salary_invalid"))
                return

            if sal_val <= 0:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_salary_zero"))
                return

            try:
                d_val = float(d_text) if d_text else 26
            except ValueError:
                d_val = 26

            try:
                h_val = float(h_text) if h_text else 8
            except ValueError:
                h_val = 8

            if d_val <= 0:
                d_val = 26
            if h_val <= 0:
                h_val = 8

            st_time = start_te.time().toString("HH:mm:ss")
            en_time = end_te.time().toString("HH:mm:ss")

            ot_val = "1" if ot_check.isChecked() else "0"
            see_val = "1" if see_check.isChecked() else "0"

            self.db.execute(
                """
                UPDATE employee_profiles
                SET jobTitle = %s, employmentType = %s, salaryType = %s,
                    baseSalary = %s, workDays = %s, workHours = %s,
                    workStartTime = %s, workEndTime = %s,
                    canSeeEmployees = %s, allowOvertime = %s
                WHERE memberId = %s
                """,
                (job_text, emp_val, st_val, sal_val, d_val, h_val,
                 st_time, en_time, see_val, ot_val, member_id)
            )

            dialog.accept()
            signals.employee_updated.emit(self.complex_id)
            signals.data_changed.emit("jobs")
            NiceMessageBox.success(
                self, tr("saved"),
                tr("salary_updated", name=name)
            )
            self.load_employees_from_database()

        save_btn.clicked.connect(on_save)

        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

        # DIALOG STYLESHEET
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {c['bg_main']};
                font-family: "Vazirmatn";
            }}
            QLineEdit, QComboBox, QTimeEdit {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
                padding: 0 18px;
                color: {c['text_main']};
                font-size: 13px;
                min-height: 44px;
            }}
            QLineEdit:focus, QComboBox:focus, QTimeEdit:focus {{
                background-color: {c['bg_card']};
                border: 2px solid {c['accent']};
            }}
            QTimeEdit::up-button, QTimeEdit::down-button {{
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }}
            QComboBox::drop-down {{
                width: 26px;
                border: none;
            }}
            QCheckBox {{
                background: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 14px;
                padding: 12px 14px;
                color: {c['text_main']};
                font-size: 12px;
                font-weight: 600;
                spacing: 12px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid {c['border_hover']};
                background: {c['bg_card']};
            }}
            QCheckBox::indicator:checked {{
                background: {c['accent']};
                border: 2px solid {c['accent']};
            }}
        """)

        dialog.exec()

    # =====================================================
    # ADD EMPLOYEE
    # =====================================================

    def add_employee(self):
        if not self.complex_id:
            print("ADD EMPLOYEE ERROR: COMPLEX ID IS NONE")
            return

        self.add_employee_window = AddEmployees(self, complex_id=self.complex_id)
        self.add_employee_window.setWindowFlags(Qt.Window)
        self.add_employee_window.setGeometry(self.x(), self.y(), self.width(), self.height())
        self.add_employee_window.show()