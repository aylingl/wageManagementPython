import os

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QDialog, QLineEdit,
    QTimeEdit, QCheckBox, QApplication
)

from PySide6.QtCore import Qt, QTime, QPoint, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QRegion

from database import Database
from signals import signals
from theme import theme_manager
from i18n import tr, set_language, get_language

from addEmployees import AddEmployees, NiceMessageBox, RoundedComboBox
from hierarchy import (
    LEVEL_OWNER, LEVEL_MANAGER, LEVEL_SUPERVISOR, LEVEL_EMPLOYEE,
    role_to_level, get_visible_member_ids, get_member_level,
    ensure_hierarchy_row, set_supervisor_and_level
)

# =========================================================
# ROLE BADGES
# =========================================================

ROLE_BADGE_FA = {
    "owner":      ("👑 مالک",   "#B87900", "#FFF4DD"),
    "both":       ("👑 مالک",   "#B87900", "#FFF4DD"),
    "manager":    ("📋 مدیر",   "#1961C7", "#DBEAFE"),
    "supervisor": ("🎯 سرپرست", "#16A34A", "#DCFCE7"),
    "employee":   ("👤 کارمند", "#526273", "#EEF2F6"),
}

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

        self.user_id = None
        self.member_id = None
        self.level = LEVEL_EMPLOYEE
        self.is_owner = False
        self.visible_ids = []

        if self.complex_id is None:
            self.find_first_complex()

        self.load_user_hierarchy()

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
            self.load_user_hierarchy()
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
    # LOAD USER HIERARCHY
    # =====================================================

    def load_user_hierarchy(self):
        self.user_id = None
        self.member_id = None
        self.level = LEVEL_EMPLOYEE
        self.is_owner = False
        self.visible_ids = []

        if not self.phone_number or not self.complex_id:
            return

        try:
            user = self.db.fetch_one(
                "SELECT userId FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if not user:
                return
            self.user_id = user["userId"]

            member = self.db.fetch_one(
                """
                SELECT memberId, role
                FROM complex_members
                WHERE complexId = %s AND userId = %s AND isActive = '1'
                LIMIT 1
                """,
                (self.complex_id, self.user_id)
            )
            if not member:
                return
            self.member_id = member["memberId"]
            role_value = member.get("role") or "employee"

            self.level = get_member_level(
                self.db, self.complex_id, self.member_id
            )

            expected_level = role_to_level(role_value)
            if expected_level < self.level:
                self.level = expected_level
                ensure_hierarchy_row(
                    self.db, self.complex_id, self.member_id, role_value
                )

            self.is_owner = (self.level == LEVEL_OWNER)

            self.visible_ids = get_visible_member_ids(
                self.db, self.complex_id, self.member_id, self.level
            )

            print("DEBUG: member_id =", self.member_id,
                  "| level =", self.level,
                  "| is_owner =", self.is_owner,
                  "| visible_ids =", self.visible_ids)

        except Exception as e:
            print("LOAD USER HIERARCHY ERROR:", e)

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(16)

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

        inactive_button = QPushButton("کارمندان غیرفعال")
        inactive_button.setObjectName("inactiveEmployeesButton")
        inactive_button.setCursor(Qt.PointingHandCursor)
        inactive_button.setFixedHeight(46)
        inactive_button.setAttribute(Qt.WA_StyledBackground, True)
        inactive_button.clicked.connect(self.open_inactive_employees)

        add_button = QPushButton(tr("add_employee"))
        add_button.setObjectName("addEmployeeButton")
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.setFixedHeight(46)
        add_button.setAttribute(Qt.WA_StyledBackground, True)
        add_button.clicked.connect(self.add_employee)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(inactive_button)
        header_layout.addWidget(add_button)

        main_layout.addLayout(header_layout)

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

        QPushButton#inactiveEmployeesButton {{
            background-color: {c['bg_card']};
            color: {c['accent']};
            border: 1px solid {c['accent']};
            border-radius: 23px;
            padding-left: 22px;
            padding-right: 22px;
            font-size: 12px;
            font-weight: 600;
        }}

        QPushButton#inactiveEmployeesButton:hover {{
            background-color: {c['accent_light']};
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

        if not self.visible_ids:
            self.load_user_hierarchy()

        # ═══════════════════════════════════════════════════
        # ⭐ محاسبه target_ids
        # ═══════════════════════════════════════════════════
        target_ids = []

        if self.is_owner:
            # ═══ مالک: همه اعضای مجموعه به جز خودش ═══
            try:
                rows = self.db.fetch_all(
                    """
                    SELECT memberId FROM complex_members
                    WHERE complexId = %s
                      AND isActive = '1'
                      AND role NOT IN ('owner', 'both')
                      AND memberId != %s
                    """,
                    (self.complex_id, self.member_id or 0)
                )
                target_ids = [r["memberId"] for r in rows] if rows else []
                print("DEBUG OWNER target_ids:", target_ids)
            except Exception as e:
                print("LOAD OWNER TARGET IDS ERROR:", e)
                target_ids = []

        else:
            # ═══ مدیر/سرپرست: زیردست‌ها به جز خودش ═══
            target_ids = [
                mid for mid in self.visible_ids
                if mid != self.member_id
            ]
            print("DEBUG NON-OWNER target_ids:", target_ids)

        if not target_ids:
            print("DEBUG: target_ids is empty -> empty state")
            self.refresh_employees()
            return

        placeholders = ",".join(["%s"] * len(target_ids))

        try:
            employees = self.db.fetch_all(
                f"""
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
                  AND cm.memberId IN ({placeholders})
                  AND cm.role NOT IN ('owner', 'both')
                  AND cm.isActive = '1'
                ORDER BY
                    CASE cm.role
                        WHEN 'manager'    THEN 1
                        WHEN 'supervisor' THEN 2
                        WHEN 'employee'   THEN 3
                        ELSE 4
                    END,
                    u.name ASC
                """,
                (self.complex_id, *target_ids)
            )

            print("DEBUG QUERY RESULT COUNT:", len(employees) if employees else 0)

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

                role_val = row.get("role") or "employee"

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
                    "allow_overtime": row.get("allowOvertime") or "1",
                    "role_value": role_val,
                    "level": role_to_level(role_val),
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
                widget.setParent(None)
                widget.deleteLater()

        QApplication.processEvents()

        if not self.employees:
            empty = QLabel("هنوز کارمندی برای نمایش وجود ندارد.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {theme_manager.colors()['text_dim']};"
                f"font-size: 13px; padding: 40px; background: transparent;"
            )
            self.employees_layout.addWidget(empty)
            self.employees_layout.addStretch()
            return

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

        avatar = RoundedAvatar(60)
        avatar_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "avatars",
            employee.get("avatar", "men.png")
        )
        avatar_pixmap = QPixmap(avatar_path)
        avatar.set_avatar(avatar_pixmap)

        card_layout.addWidget(avatar, 0, Qt.AlignTop)

        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent;")

        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignRight)

        name_row = QHBoxLayout()
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(8)

        name_label = QLabel(employee.get("name", tr("no_name")))
        name_label.setObjectName("employeeName")
        name_label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        role_value = employee.get("role_value", "employee")
        badge_info = ROLE_BADGE_FA.get(role_value, ROLE_BADGE_FA["employee"])
        role_badge = QLabel(badge_info[0])
        role_badge.setAlignment(Qt.AlignCenter)
        role_badge.setStyleSheet(
            f"color: {badge_info[1]};"
            f"background-color: {badge_info[2]};"
            f"border: none; border-radius: 10px;"
            f"padding: 3px 10px; font-size: 10px; font-weight: 700;"
        )

        name_row.addWidget(name_label)
        name_row.addWidget(role_badge)
        name_row.addStretch()

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

        info_layout.addLayout(name_row)
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
    # INACTIVE EMPLOYEES DIALOG
    # =====================================================

    def open_inactive_employees(self):
        if not self.complex_id:
            return

        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setWindowTitle("کارمندان غیرفعال")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(640)
        dialog.setMinimumHeight(520)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(12)

        title = QLabel("کارمندان غیرفعال")
        title.setStyleSheet(f"color: {c['text_main']}; font-size: 17px; font-weight: 800; background: transparent;")
        layout.addWidget(title)

        sub = QLabel("برای فعال کردن مجدد، روی دکمه «فعال کردن» بزنید.")
        sub.setStyleSheet(f"color: {c['text_dim']}; font-size: 11px; background: transparent;")
        layout.addWidget(sub)

        layout.addSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QScrollArea::viewport { background: transparent; }")
        vbar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(vbar)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(4, 4, 12, 4)
        content_layout.setSpacing(8)

        try:
            inactive = self.db.fetch_all(
                """
                SELECT cm.memberId, cm.userId, u.name, u.phoneNumber,
                       ep.jobTitle
                FROM complex_members cm
                INNER JOIN users u ON u.userId = cm.userId
                LEFT JOIN employee_profiles ep ON ep.memberId = cm.memberId
                WHERE cm.complexId = %s
                  AND cm.role NOT IN ('owner', 'both')
                  AND cm.isActive = '0'
                ORDER BY cm.memberId DESC
                """,
                (self.complex_id,)
            )
        except Exception as e:
            print("LOAD INACTIVE EMPLOYEES ERROR:", e)
            inactive = []

        if not inactive:
            empty = QLabel("کارمند غیرفعالی وجود ندارد.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color: {c['text_dim']}; font-size: 13px; padding: 40px; background: transparent;")
            content_layout.addWidget(empty)
        else:
            for emp in inactive:
                card = QFrame()
                card.setObjectName("inactiveCard")
                card.setAttribute(Qt.WA_StyledBackground, True)
                card.setMinimumHeight(72)
                card.setStyleSheet(f"""
                    QFrame#inactiveCard {{
                        background-color: {c['bg_card']};
                        border: 1px solid {c['border']};
                        border-radius: 18px;
                    }}
                """)

                cl = QHBoxLayout(card)
                cl.setContentsMargins(16, 12, 16, 12)
                cl.setSpacing(12)

                name_lbl = QLabel(emp.get("name") or "—")
                name_lbl.setStyleSheet(f"color: {c['text_main']}; font-size: 13px; font-weight: 700; background: transparent;")
                name_lbl.setMinimumWidth(140)

                phone_lbl = QLabel(emp.get("phoneNumber") or "—")
                phone_lbl.setStyleSheet(f"color: {c['text_dim']}; font-size: 11px; background: transparent;")
                phone_lbl.setMinimumWidth(120)

                job_lbl = QLabel(emp.get("jobTitle") or "—")
                job_lbl.setStyleSheet(f"color: {c['accent']}; font-size: 11px; font-weight: 600; background: transparent;")
                job_lbl.setMinimumWidth(120)

                activate_btn = QPushButton("فعال کردن")
                activate_btn.setCursor(Qt.PointingHandCursor)
                activate_btn.setFixedHeight(34)
                activate_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c['success_bg']};
                        color: {c['success']};
                        border: 1px solid {c['success']};
                        border-radius: 17px;
                        padding: 0 20px;
                        font-size: 12px;
                        font-weight: 700;
                    }}
                    QPushButton:hover {{
                        background-color: {c['bg_hover']};
                    }}
                """)
                activate_btn.clicked.connect(
                    lambda checked=False, m=emp.get("memberId"): self.activate_member(m, dialog)
                )

                cl.addWidget(name_lbl, 2)
                cl.addWidget(phone_lbl, 2)
                cl.addWidget(job_lbl, 2)
                cl.addStretch()
                cl.addWidget(activate_btn)

                content_layout.addWidget(card)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        close_btn = QPushButton(tr("close"))
        close_btn.setFixedHeight(46)
        close_btn.setMinimumWidth(140)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 23px;
                padding: 0 28px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {c['accent_hover']}; }}
        """)
        close_btn.clicked.connect(dialog.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        dialog.setStyleSheet(f"QDialog {{ background-color: {c['bg_main']}; font-family: 'Vazirmatn'; }}")
        dialog.exec()

    def activate_member(self, member_id, dialog):
        if not member_id:
            return
        try:
            result = self.db.execute(
                "UPDATE complex_members SET isActive = '1' WHERE memberId = %s AND complexId = %s",
                (member_id, self.complex_id)
            )
            if result is None:
                NiceMessageBox.error(self, tr("error"), "فعال‌سازی ناموفق بود.")
                return

            NiceMessageBox.success(self, tr("saved"), "کارمند با موفقیت فعال شد.")
            dialog.accept()
            self.load_user_hierarchy()
            self.load_employees_from_database()
            signals.employee_added.emit(self.complex_id)
            signals.data_changed.emit("jobs")
        except Exception as e:
            print("ACTIVATE MEMBER ERROR:", e)
            NiceMessageBox.error(self, tr("error"), str(e))

    # =====================================================
    # GET OWNER MEMBER ID
    # =====================================================

    def get_owner_member_id(self):
        try:
            row = self.db.fetch_one(
                """
                SELECT memberId FROM complex_members
                WHERE complexId = %s
                  AND role IN ('owner', 'both')
                  AND isActive = '1'
                ORDER BY memberId ASC
                LIMIT 1
                """,
                (self.complex_id,)
            )
            if row:
                return row["memberId"]
        except Exception as e:
            print("GET OWNER MEMBER ID ERROR:", e)
        return None

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
                   ep.canSeeEmployees, ep.allowOvertime,
                   u.name, u.phoneNumber,
                   cm.role
            FROM employee_profiles ep
            INNER JOIN complex_members cm ON cm.memberId = ep.memberId
            INNER JOIN users u ON u.userId = cm.userId
            WHERE ep.memberId = %s
            LIMIT 1
            """,
            (member_id,)
        )

        if not row:
            NiceMessageBox.error(self, tr("error"), tr("err_loading_groups"))
            return

        c = theme_manager.colors()

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("edit_salary_info"))
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setMinimumSize(400, 300)

        try:
            pg = self.frameGeometry()
            dialog.setGeometry(pg.x(), pg.y(), pg.width(), pg.height())
        except Exception:
            dialog.resize(self.width(), self.height())

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ═══ HEADER ═══
        header_frame = QFrame()
        header_frame.setAttribute(Qt.WA_StyledBackground, True)
        header_frame.setStyleSheet(
            f"QFrame {{ background-color: {c['bg_main']}; border: none; }}"
        )

        header_outer = QVBoxLayout(header_frame)
        header_outer.setContentsMargins(28, 22, 28, 10)
        header_outer.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        back_btn = QPushButton("›")
        back_btn.setFixedSize(42, 42)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_card']};
                color: {c['accent']};
                border: 1px solid {c['border']};
                border-radius: 21px;
                font-size: 22px;
                font-weight: 600;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                border-color: {c['border_hover']};
            }}
        """)
        back_btn.clicked.connect(dialog.reject)

        title_v = QVBoxLayout()
        title_v.setSpacing(3)

        d_title = QLabel(f"{tr('edit_salary_info')} — {employee.get('name') or tr('no_name')}")
        d_title.setStyleSheet(
            f"color: {c['text_main']}; font-size: 21px; "
            f"font-weight: 700; background: transparent;"
        )

        d_sub = QLabel("ویرایش اطلاعات کارمند")
        d_sub.setStyleSheet(
            f"color: {c['text_dim']}; font-size: 11px; background: transparent;"
        )

        title_v.addWidget(d_title)
        title_v.addWidget(d_sub)

        header_row.addWidget(back_btn)
        header_row.addLayout(title_v)
        header_row.addStretch()

        header_outer.addLayout(header_row)
        main_layout.addWidget(header_frame)

        # ═══ SCROLL ═══
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollArea::viewport { background: transparent; }"
        )
        vbar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(vbar)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_main']};")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 10, 28, 24)
        layout.setSpacing(6)

        form_box = QFrame()
        form_box.setObjectName("formBox")
        form_box.setAttribute(Qt.WA_StyledBackground, True)

        form_layout = QVBoxLayout(form_box)
        form_layout.setContentsMargins(24, 20, 24, 20)
        form_layout.setSpacing(6)

        # ═══ NAME ═══
        name_lbl = QLabel("نام")
        name_lbl.setObjectName("fieldLabel")
        name_input = QLineEdit()
        name_input.setObjectName("formInput")
        name_input.setText(row.get("name") or "")
        name_input.setFixedHeight(44)
        name_err = QLabel()
        name_err.setObjectName("fieldError")
        name_err.setFixedHeight(16)
        name_err.hide()
        form_layout.addWidget(name_lbl)
        form_layout.addWidget(name_input)
        form_layout.addWidget(name_err)

        # ═══ PHONE ═══
        phone_lbl = QLabel("شماره موبایل")
        phone_lbl.setObjectName("fieldLabel")
        phone_input = QLineEdit()
        phone_input.setObjectName("formInput")
        phone_input.setText(str(row.get("phoneNumber") or ""))
        phone_input.setFixedHeight(44)
        phone_input.setLayoutDirection(Qt.LeftToRight)
        phone_input.setMaxLength(11)
        phone_err = QLabel()
        phone_err.setObjectName("fieldError")
        phone_err.setFixedHeight(16)
        phone_err.hide()
        form_layout.addWidget(phone_lbl)
        form_layout.addWidget(phone_input)
        form_layout.addWidget(phone_err)

        form_layout.addSpacing(4)

        # ═══ HIERARCHY ROLE ═══
        role_global_lbl = QLabel("نقش کلی")
        role_global_lbl.setObjectName("fieldLabel")

        role_global_combo = RoundedComboBox()
        role_global_combo.setObjectName("formInput")
        role_global_combo.setFixedHeight(44)

        role_global_combo.addItem("👤  کارمند",  "employee")
        role_global_combo.addItem("🎯  سرپرست", "supervisor")
        role_global_combo.addItem("📋  مدیر",   "manager")

        current_role_value = row.get("role") or "employee"
        if current_role_value not in ("employee", "supervisor", "manager"):
            current_role_value = "employee"

        for i in range(role_global_combo.count()):
            if role_global_combo.itemData(i) == current_role_value:
                role_global_combo.setCurrentIndex(i)
                break

        form_layout.addWidget(role_global_lbl)
        form_layout.addWidget(role_global_combo)

        form_layout.addSpacing(4)

        # ═══ ROLE IN GROUP ═══
        role_lbl = QLabel(tr("role_in_group"))
        role_lbl.setObjectName("fieldLabel")

        role_input = QLineEdit()
        role_input.setObjectName("formInput")
        role_input.setFixedHeight(44)

        role_titles = {
            "employee":   "کارمند",
            "supervisor": "سرپرست",
            "manager":    "مدیر",
        }
        all_prefixes = ["کارمند", "سرپرست", "مدیر"]

        def strip_prefix(text):
            stripped = text.strip()
            for p in all_prefixes:
                if stripped.startswith(p):
                    return stripped[len(p):].strip()
            return stripped

        initial_job_title = row.get("jobTitle") or ""
        initial_suffix = strip_prefix(initial_job_title)
        initial_base = role_titles.get(current_role_value, "کارمند")

        if initial_suffix:
            role_input.setText(f"{initial_base} {initial_suffix}")
        else:
            role_input.setText(initial_base)

        role_err = QLabel()
        role_err.setObjectName("fieldError")
        role_err.setFixedHeight(16)
        role_err.hide()

        def on_global_role_changed():
            new_role = role_global_combo.currentData()
            base = role_titles.get(new_role, "کارمند")
            current = role_input.text()
            suffix = strip_prefix(current)
            new_text = f"{base} {suffix}".strip() if suffix else base
            if role_input.text() != new_text:
                role_input.blockSignals(True)
                role_input.setText(new_text)
                role_input.setCursorPosition(len(new_text))
                role_input.blockSignals(False)

        role_global_combo.currentIndexChanged.connect(on_global_role_changed)

        form_layout.addWidget(role_lbl)
        form_layout.addWidget(role_input)
        form_layout.addWidget(role_err)

        form_layout.addSpacing(4)

        # ═══ EMPLOYMENT TYPE ═══
        emp_lbl = QLabel(tr("employment_type"))
        emp_lbl.setObjectName("fieldLabel")

        emp_combo = RoundedComboBox()
        emp_combo.setObjectName("formInput")
        emp_combo.setFixedHeight(44)
        emp_combo.addItem(tr("full_time"), "fullTime")
        emp_combo.addItem(tr("part_time"), "partTime")

        current_emp = row.get("employmentType") or "fullTime"
        for i in range(emp_combo.count()):
            if emp_combo.itemData(i) == current_emp:
                emp_combo.setCurrentIndex(i)
                break

        form_layout.addWidget(emp_lbl)
        form_layout.addWidget(emp_combo)

        # ═══ DIVIDER ═══
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        form_layout.addSpacing(6)
        form_layout.addWidget(divider)
        form_layout.addSpacing(6)

        section_title = QLabel(f"💰  {tr('salary_details_section')}")
        section_title.setObjectName("sectionTitle")
        form_layout.addWidget(section_title)
        form_layout.addSpacing(4)

        # ═══ SALARY TYPE ═══
        st_lbl = QLabel(tr("salary_type"))
        st_lbl.setObjectName("fieldLabel")

        st_combo = RoundedComboBox()
        st_combo.setObjectName("formInput")
        st_combo.setFixedHeight(44)
        st_combo.addItem(tr("monthly"), "monthly")
        st_combo.addItem(tr("daily"), "daily")
        st_combo.addItem(tr("hourly"), "hourly")

        current_st = row.get("salaryType") or "monthly"
        for i in range(st_combo.count()):
            if st_combo.itemData(i) == current_st:
                st_combo.setCurrentIndex(i)
                break

        form_layout.addWidget(st_lbl)
        form_layout.addWidget(st_combo)

        # ═══ SALARY AMOUNT ═══
        sal_lbl = QLabel(tr("amount_label"))
        sal_lbl.setObjectName("fieldLabel")

        sal_input = QLineEdit()
        sal_input.setObjectName("formInput")
        try:
            sal_input.setText(f"{int(float(row.get('baseSalary') or 0)):,}")
        except Exception:
            sal_input.setText("0")
        sal_input.setFixedHeight(44)
        sal_input.setLayoutDirection(Qt.LeftToRight)
        sal_input.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        def format_salary_live(text):
            digits = "".join(ch for ch in text if ch.isdigit())
            if not digits:
                return
            try:
                num = int(digits)
                formatted = f"{num:,}"
                if text != formatted:
                    sal_input.blockSignals(True)
                    sal_input.setText(formatted)
                    sal_input.setCursorPosition(len(formatted))
                    sal_input.blockSignals(False)
            except ValueError:
                pass

        sal_input.textChanged.connect(format_salary_live)

        sal_err = QLabel()
        sal_err.setObjectName("fieldError")
        sal_err.setFixedHeight(16)
        sal_err.hide()

        form_layout.addWidget(sal_lbl)
        form_layout.addWidget(sal_input)
        form_layout.addWidget(sal_err)

        # ═══ DAYS + HOURS ═══
        dh_row = QHBoxLayout()
        dh_row.setSpacing(10)

        d_col = QVBoxLayout()
        d_col.setSpacing(4)
        d_lbl = QLabel(tr("days_per_month"))
        d_lbl.setObjectName("fieldLabel")
        d_input = QLineEdit()
        d_input.setObjectName("formInput")
        d_input.setText(str(int(float(row.get("workDays") or 26))))
        d_input.setFixedHeight(44)
        d_input.setLayoutDirection(Qt.LeftToRight)
        d_col.addWidget(d_lbl)
        d_col.addWidget(d_input)

        h_col = QVBoxLayout()
        h_col.setSpacing(4)
        h_lbl = QLabel(tr("hours_per_day"))
        h_lbl.setObjectName("fieldLabel")
        h_input = QLineEdit()
        h_input.setObjectName("formInput")
        h_input.setText(str(int(float(row.get("workHours") or 8))))
        h_input.setFixedHeight(44)
        h_input.setLayoutDirection(Qt.LeftToRight)
        h_col.addWidget(h_lbl)
        h_col.addWidget(h_input)

        dh_row.addLayout(d_col, 1)
        dh_row.addLayout(h_col, 1)
        form_layout.addLayout(dh_row)

        # ═══ TIMES ═══
        te_row = QHBoxLayout()
        te_row.setSpacing(10)

        st_col = QVBoxLayout()
        st_col.setSpacing(4)
        st_lbl2 = QLabel(tr("start_time"))
        st_lbl2.setObjectName("fieldLabel")
        start_te = QTimeEdit()
        start_te.setObjectName("formInput")
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
        en_col.setSpacing(4)
        en_lbl = QLabel(tr("end_time"))
        en_lbl.setObjectName("fieldLabel")
        end_te = QTimeEdit()
        end_te.setObjectName("formInput")
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
        form_layout.addLayout(te_row)

        # ═══ CHECKBOX ═══
        ot_check = QCheckBox(tr("allow_overtime_check"))
        ot_check.setObjectName("formCheckbox")
        ot_check.setCursor(Qt.PointingHandCursor)
        ot_check.setChecked(str(row.get("allowOvertime") or "1") == "1")

        form_layout.addSpacing(4)
        form_layout.addWidget(ot_check)
        form_layout.addStretch()

        layout.addWidget(form_box)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

        # ═══ BOTTOM ═══
        bottom = QFrame()
        bottom.setAttribute(Qt.WA_StyledBackground, True)
        bottom.setStyleSheet(
            f"QFrame {{ background-color: {c['bg_main']}; border: none; }}"
        )
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(28, 10, 28, 22)
        bottom_layout.setSpacing(12)

        cancel_btn = QPushButton(tr("cancel"))
        cancel_btn.setFixedHeight(50)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_card']};
                color: {c['text_dim']};
                border: 1px solid {c['border']};
                border-radius: 23px;
                padding: 0 28px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                color: {c['accent']};
                border-color: {c['border_hover']};
            }}
        """)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = QPushButton(tr("save"))
        save_btn.setFixedHeight(50)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent']};
                color: white;
                border: none;
                border-radius: 23px;
                padding: 0 28px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {c['accent_hover']};
            }}
        """)

        def contains_digit(text):
            for ch in text:
                if ch.isdigit():
                    return True
            return False

        def show_err(label, msg):
            label.setText(msg)
            label.setAlignment(Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter)
            label.show()

        def on_save():
            name_text = name_input.text().strip()
            phone_text = phone_input.text().strip()
            job_text = role_input.text().strip()
            sal_text = sal_input.text().strip()
            d_text = d_input.text().strip()
            h_text = h_input.text().strip()
            st_val = st_combo.currentData()
            emp_val = emp_combo.currentData()
            new_role_value = role_global_combo.currentData() or "employee"

            name_err.hide()
            phone_err.hide()
            role_err.hide()
            sal_err.hide()

            if not name_text:
                show_err(name_err, "لطفاً نام را وارد کنید.")
                name_input.setFocus()
                return
            if contains_digit(name_text):
                show_err(name_err, "نام نباید شامل عدد باشد.")
                name_input.setFocus()
                return
            if not phone_text:
                show_err(phone_err, "لطفاً شماره موبایل را وارد کنید.")
                phone_input.setFocus()
                return
            if not phone_text.isdigit() or len(phone_text) != 11 or not phone_text.startswith("09"):
                show_err(phone_err, "شماره باید ۱۱ رقم و با ۰۹ شروع شود.")
                phone_input.setFocus()
                return
            if not job_text:
                show_err(role_err, "لطفاً نقش در مجموعه را وارد کنید.")
                role_input.setFocus()
                return

            try:
                sal_val = float(sal_text.replace(",", "").replace("٬", ""))
            except ValueError:
                show_err(sal_err, "حقوق باید عدد باشد.")
                sal_input.setFocus()
                return
            if sal_val <= 0:
                show_err(sal_err, "حقوق باید بزرگ‌تر از صفر باشد.")
                sal_input.setFocus()
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
            see_val = row.get("canSeeEmployees") or "1"

            dup = self.db.fetch_one(
                """
                SELECT u.userId FROM users u
                INNER JOIN complex_members cm ON cm.userId = u.userId
                WHERE u.phoneNumber = %s AND cm.memberId != %s
                LIMIT 1
                """,
                (phone_text, member_id)
            )
            if dup:
                show_err(phone_err, "این شماره قبلاً ثبت شده است.")
                phone_input.setFocus()
                return

            # ═══ UPDATE user ═══
            self.db.execute(
                """
                UPDATE users u
                INNER JOIN complex_members cm ON cm.userId = u.userId
                SET u.name = %s, u.phoneNumber = %s
                WHERE cm.memberId = %s
                """,
                (name_text, phone_text, member_id)
            )

            # ═══ UPDATE profile ═══
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

            # ═══ UPDATE role ═══
            self.db.execute(
                """
                UPDATE complex_members SET role = %s
                WHERE memberId = %s AND complexId = %s
                """,
                (new_role_value, member_id, self.complex_id)
            )

            # ═══ بررسی ذخیره role ═══
            verify = self.db.fetch_one(
                "SELECT role FROM complex_members WHERE memberId = %s LIMIT 1",
                (member_id,)
            )
            saved_role = verify.get("role") if verify else None

            print("EDIT: requested role =", new_role_value, "| saved role =", saved_role)

            if saved_role != new_role_value:
                NiceMessageBox.error(
                    dialog, "خطا",
                    "نقش ذخیره نشد. لطفاً migration نقش‌ها را اجرا کن:\n\n"
                    "migrations/003_role_varchar.sql"
                )
                return

            # ═══ UPDATE hierarchy ═══
            new_level = role_to_level(new_role_value)
            sup_id = self.get_owner_member_id()
            set_supervisor_and_level(
                self.db, self.complex_id, member_id,
                sup_id, new_level
            )

            dialog.accept()
            signals.employee_updated.emit(self.complex_id)
            signals.data_changed.emit("jobs")

            NiceMessageBox.success(
                self, tr("saved"),
                tr("salary_updated", name=name_text)
            )

            self.load_user_hierarchy()
            self.load_employees_from_database()

        save_btn.clicked.connect(on_save)

        bottom_layout.addWidget(cancel_btn)
        bottom_layout.addWidget(save_btn)

        main_layout.addWidget(bottom)

        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {c['bg_main']};
                font-family: "Vazirmatn";
            }}
            QLabel#fieldLabel {{
                color: {c['text_dim']}; font-size: 12px;
                font-weight: 600; background: transparent; padding: 0px;
            }}
            QLabel#fieldError {{
                color: #D93025; font-size: 11px; font-weight: 600;
                background: transparent; padding: 0px;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
            }}
            QLabel#sectionTitle {{
                color: {c['accent']}; font-size: 13px;
                font-weight: 700; background: transparent;
            }}
            QFrame#formBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 28px;
            }}
            QFrame#divider {{
                background-color: {c['border']}; border: none;
            }}
            QLineEdit#formInput, QTimeEdit#formInput {{
                background: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 22px;
                padding: 0 18px;
                color: {c['text_main']};
                font-size: 13px;
                min-height: 44px;
            }}
            QLineEdit#formInput:hover, QTimeEdit#formInput:hover {{
                background: {c['bg_card']};
                border: 1px solid {c['border_hover']};
            }}
            QLineEdit#formInput:focus, QTimeEdit#formInput:focus {{
                background: {c['bg_card']};
                border: 2px solid {c['accent']};
            }}
            QTimeEdit#formInput::up-button, QTimeEdit#formInput::down-button {{
                width: 20px; border: none; background: transparent;
            }}
            QCheckBox#formCheckbox {{
                background: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 14px;
                padding: 12px 14px;
                color: {c['text_main']};
                font-size: 12px; font-weight: 600;
                spacing: 12px;
            }}
            QCheckBox#formCheckbox:hover {{
                background: {c['bg_card']};
                border: 1px solid {c['border_hover']};
            }}
            QCheckBox#formCheckbox::indicator {{
                width: 20px; height: 20px; border-radius: 5px;
                border: 2px solid {c['border_hover']};
                background: {c['bg_card']};
            }}
            QCheckBox#formCheckbox::indicator:checked {{
                background: {c['accent']};
                border: 2px solid {c['accent']};
                image: none;
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
        self.add_employee_window.show()