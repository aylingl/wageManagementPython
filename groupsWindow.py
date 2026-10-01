from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QLineEdit,
    QTextEdit,
    QDialog
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextOption

from database import Database
from signals import signals

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
# VALIDATION HELPERS
# =========================================================

def contains_digit(text):
    for c in text:
        if c.isdigit():
            return True
    return False

def count_letters(text):
    return sum(1 for c in text if c.isalpha())

# =========================================================
# GROUPS WINDOW
# =========================================================

class GroupsWindow(QWidget):

    def __init__(self, parent_window=None, phone_number="09123456789"):

        super().__init__()

        self.parent_window = parent_window
        self.phone_number = phone_number

        self.db = Database()

        self.groups = []
        self.user_id = None

        self.setWindowTitle("مجموعه‌ها")
        self.setMinimumSize(700, 550)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("groupsWindow")

        self.setup_ui()
        self.load_data()

        signals.employee_added.connect(self.on_employee_changed)
        signals.employee_removed.connect(self.on_employee_changed)
        signals.employee_updated.connect(self.on_employee_changed)

    # =====================================================
    # SIGNAL HANDLER
    # =====================================================

    def on_employee_changed(self, complex_id):
        self.load_groups()
        self.refresh_groups()

    # =====================================================
    # LOAD DATA
    # =====================================================

    def load_data(self):

        try:
            user = self.db.fetch_one(
                """
                SELECT userId, name
                FROM users
                WHERE phoneNumber = %s
                LIMIT 1
                """,
                (self.phone_number,)
            )

            if not user:
                NiceMessageBox.warning(self, "خطا", "اطلاعات کاربر پیدا نشد.")
                return

            self.user_id = user["userId"]

            self.load_groups()
            self.refresh_groups()

        except Exception as error:
            print("GroupsWindow load error:", error)
            NiceMessageBox.error(
                self, "خطا",
                "در دریافت اطلاعات مجموعه‌ها مشکلی به وجود آمد."
            )

    # =====================================================
    # LOAD GROUPS
    # =====================================================

    def load_groups(self):

        self.groups = []

        try:
            rows = self.db.fetch_all(
                """
                SELECT
                    c.complexId,
                    c.name,
                    c.address,
                    c.activity,
                    c.description,
                    c.ownerId,
                    c.createdDate,
                    c.isActive,
                    cm.role
                FROM complexes c
                INNER JOIN complex_members cm
                    ON cm.complexId = c.complexId
                    AND cm.userId = %s
                    AND cm.isActive = '1'
                WHERE c.isActive = '1'
                ORDER BY c.complexId ASC
                """,
                (self.user_id,)
            )

            for row in rows:

                employee_count = self.db.fetch_one(
                    """
                    SELECT COUNT(*) AS total
                    FROM complex_members
                    WHERE complexId = %s
                      AND isActive = '1'
                      AND role IN ('employee', 'both')
                    """,
                    (row["complexId"],)
                )

                count = employee_count["total"] if employee_count else 0
                count = count or 0

                role = row["role"]

                if role == "owner":
                    role_text = "مالک"
                elif role == "employee":
                    role_text = "کارمند"
                elif role == "both":
                    role_text = "مالک و کارمند"
                else:
                    role_text = "کاربر"

                self.groups.append({
                    "complexId": row["complexId"],
                    "name": row["name"],
                    "address": row["address"] or "بدون آدرس",
                    "activity": row["activity"] or "بدون فعالیت",
                    "description": row["description"] or "بدون توضیحات",
                    "role": role_text,
                    "roleValue": role,
                    "employeeCount": count
                })

        except Exception as error:
            print("LOAD GROUPS ERROR:", error)

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.go_back)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("مجموعه‌ها")
        title.setObjectName("title")

        subtitle = QLabel("مدیریت مجموعه‌های شما")
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        add_group_button = QPushButton("+  افزودن مجموعه")
        add_group_button.setObjectName("addGroupButton")
        add_group_button.setCursor(Qt.PointingHandCursor)
        add_group_button.clicked.connect(self.add_group)

        header_layout.addWidget(add_group_button)

        main_layout.addLayout(header_layout)

        # =================================================
        # CONTAINER — باکس پهن گرد دور کارت‌های مجموعه
        # =================================================

        groups_container_frame = QFrame()
        groups_container_frame.setObjectName("groupsContainer")
        groups_container_frame.setAttribute(Qt.WA_StyledBackground, True)

        container_layout = QVBoxLayout(groups_container_frame)
        container_layout.setContentsMargins(20, 18, 20, 18)
        container_layout.setSpacing(12)

        container_title = QLabel("مجموعه‌های من")
        container_title.setObjectName("containerTitle")
        container_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        container_layout.addWidget(container_title)

        # SCROLL داخل باکس
        scroll = QScrollArea()
        scroll.setObjectName("groupsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("scrollContent")
        content.setAttribute(Qt.WA_TranslucentBackground, True)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(4, 4, 12, 4)
        content_layout.setSpacing(10)

        self.groups_container = QVBoxLayout()
        self.groups_container.setSpacing(10)

        content_layout.addLayout(self.groups_container)
        content_layout.addStretch()

        scroll.setWidget(content)

        container_layout.addWidget(scroll)

        main_layout.addWidget(groups_container_frame)

        self.setStyleSheet("""

            QWidget#groupsWindow {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }

            QLabel#title {
                background: transparent;
                border: none;
                color: #1E2F43;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#subtitle {
                background: transparent;
                border: none;
                color: #8290A1;
                font-size: 12px;
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

            QPushButton#addGroupButton {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 13px;
                padding: 11px 18px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#addGroupButton:hover {
                background-color: #4589E8;
            }

            QFrame#groupsContainer {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 24px;
            }

            QLabel#containerTitle {
                background: transparent;
                border: none;
                color: #25364A;
                font-size: 14px;
                font-weight: 700;
                padding: 0px 4px;
            }

            QScrollArea#groupsScroll {
                background: transparent;
                border: none;
                border-radius: 16px;
            }

            QScrollArea#groupsScroll::viewport {
                background: transparent;
                border: none;
                border-radius: 16px;
            }

            QWidget#scrollContent {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                width: 10px;
                background: transparent;
                border: none;
                margin: 8px 0px;
            }

            QScrollBar::handle:vertical {
                background: #4589E8;
                min-height: 45px;
                border-radius: 5px;
                border: none;
            }

            QScrollBar::handle:vertical:hover {
                background: #1961C7;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
                background: transparent;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
            }

            QLabel#description {
                background: transparent;
                border: none;
                color: #8290A1;
                font-size: 11px;
            }

            QFrame#groupCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }

            QFrame#groupCard:hover {
                background-color: #EAF3FF;
                border-color: #4589E8;
            }

            QLabel#groupIcon {
                background-color: #EAF3FF;
                border: none;
                border-radius: 20px;
                font-size: 20px;
            }

            QLabel#groupName {
                background: transparent;
                border: none;
                color: #25364A;
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#groupAddress {
                background: transparent;
                border: none;
                color: #8290A1;
                font-size: 10px;
            }

            QLabel#groupActivity {
                background: transparent;
                border: none;
                color: #6E7D8E;
                font-size: 10px;
            }

            QLabel#employeeCount {
                background-color: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 8px;
                padding: 2px 8px;
                font-size: 9px;
                font-weight: 600;
            }

            QPushButton#manageButton {
                background-color: #F1F6FD;
                color: #1961C7;
                border: none;
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton#manageButton:hover {
                background-color: #DDEEFF;
            }

            QPushButton#deleteButton {
                background-color: #FDECEC;
                color: #D93025;
                border: none;
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton#deleteButton:hover {
                background-color: #FBD5D5;
            }

            QFrame#groupDialog,
            QFrame#confirmDialog {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }

            QLabel#dialogTitle {
                background: transparent;
                border: none;
                color: #1E2F43;
                font-size: 17px;
                font-weight: 700;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
            }

            QLabel#dialogDescription {
                background: transparent;
                border: none;
                color: #8290A1;
                font-size: 12px;
                qproperty-alignment: 'AlignRight | AlignAbsolute';
            }

            QLabel#errorLabel {
                color: #D93025;
                background: transparent;
                border: none;
                font-size: 11px;
                font-weight: 500;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
            }

            QLineEdit#dialogInput {
                background-color: #F5F8FC;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                padding: 10px 14px;
                color: #25364A;
                font-size: 12px;
            }

            QLineEdit#dialogInput:focus {
                border-color: #4589E8;
                background-color: #FFFFFF;
            }

            QTextEdit#dialogInput {
                background-color: #F5F8FC;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                padding: 10px 14px;
                color: #25364A;
                font-size: 12px;
            }

            QTextEdit#dialogInput:focus {
                border-color: #4589E8;
                background-color: #FFFFFF;
            }

            QPushButton#dialogCancel {
                background-color: #F5F8FC;
                color: #526273;
                border: 1px solid #E2EAF4;
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
            }

            QPushButton#dialogCancel:hover {
                background-color: #EEF3FA;
            }

            QPushButton#dialogSave {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#dialogSave:hover {
                background-color: #4589E8;
            }

            QPushButton#dialogDelete {
                background-color: #D93025;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#dialogDelete:hover {
                background-color: #B71C1C;
            }

        """)

    # =====================================================
    # BACK
    # =====================================================

    def go_back(self):

        self.close()

        if self.parent_window:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()

            if hasattr(self.parent_window, "refresh_groups_from_database"):
                self.parent_window.refresh_groups_from_database()

    # =====================================================
    # REFRESH GROUPS
    # =====================================================

    def refresh_groups(self):

        while self.groups_container.count():
            item = self.groups_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.groups:
            empty_label = QLabel("هنوز مجموعه‌ای نداری.")
            empty_label.setObjectName("description")
            empty_label.setContentsMargins(0, 0, 12, 0)
            self.groups_container.addWidget(empty_label)
            return

        for group in self.groups:
            card = self.create_group_card(group)
            self.groups_container.addWidget(card)

    # =====================================================
    # GROUP CARD
    # =====================================================

    def create_group_card(self, group):

        card = QFrame()
        card.setObjectName("groupCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setFixedHeight(100)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        icon = QLabel("🏢")
        icon.setObjectName("groupIcon")
        icon.setFixedSize(42, 42)
        icon.setAlignment(Qt.AlignCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        name = QLabel(group["name"])
        name.setObjectName("groupName")
        name.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        address = QLabel(f"آدرس: {group['address']}")
        address.setObjectName("groupAddress")
        address.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        activity = QLabel(f"فعالیت: {group['activity']}")
        activity.setObjectName("groupActivity")
        activity.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        text_layout.addWidget(name)
        text_layout.addWidget(address)
        text_layout.addWidget(activity)

        count = QLabel(f"{group['employeeCount']} کارمند")
        count.setObjectName("employeeCount")
        count.setAlignment(Qt.AlignCenter)
        count.setFixedHeight(22)

        layout.addWidget(icon)
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(count)

        role_label = QLabel(group["role"])
        role_label.setAlignment(Qt.AlignCenter)
        role_label.setFixedHeight(22)
        role_label.setStyleSheet("""
            QLabel {
                background-color: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 8px;
                padding: 2px 10px;
                font-size: 10px;
                font-weight: 600;
            }
        """)

        layout.addWidget(role_label)

        if group["role"] == "مالک" or group["role"] == "مالک و کارمند":
            manage_button = QPushButton("مدیریت")
            manage_button.setObjectName("manageButton")
            manage_button.setCursor(Qt.PointingHandCursor)
            manage_button.clicked.connect(
                lambda checked=False, g=group: self.manage_group(g)
            )

            delete_button = QPushButton("حذف")
            delete_button.setObjectName("deleteButton")
            delete_button.setCursor(Qt.PointingHandCursor)
            delete_button.clicked.connect(
                lambda checked=False, g=group: self.confirm_delete_group(g)
            )

            layout.addWidget(manage_button)
            layout.addWidget(delete_button)

        return card

    # =====================================================
    # MANAGE GROUP
    # =====================================================

    def manage_group(self, group):

        try:
            employees = self.get_group_employee_names(group["complexId"])

            if employees:
                employee_text = "\n".join(f"• {e}" for e in employees)
            else:
                employee_text = "هنوز کارمندی به این مجموعه اضافه نشده است."

            NiceMessageBox.info(
                self,
                group["name"],
                (
                    f"آدرس: {group['address']}\n"
                    f"فعالیت: {group['activity']}\n\n"
                    f"توضیحات:\n{group['description']}\n\n"
                    f"کارکنان:\n{employee_text}"
                )
            )

        except Exception as error:
            print("MANAGE GROUP ERROR:", error)
            NiceMessageBox.error(
                self, "خطا",
                "در دریافت اطلاعات مجموعه مشکلی به وجود آمد."
            )

    def get_group_employee_names(self, complex_id):

        try:
            rows = self.db.fetch_all(
                """
                SELECT u.userId, u.name
                FROM complex_members cm
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                  AND cm.isActive = '1'
                  AND cm.role IN ('employee', 'both')
                ORDER BY u.name ASC
                """,
                (complex_id,)
            )

            return [row["name"] or "بدون نام" for row in rows]

        except Exception as error:
            print("GET GROUP EMPLOYEES ERROR:", error)
            return []

    # =====================================================
    # CONFIRM DELETE
    # =====================================================

    def confirm_delete_group(self, group):

        dialog = QFrame(self, Qt.Dialog)
        dialog.setWindowTitle("حذف مجموعه")
        dialog.setObjectName("confirmDialog")
        dialog.setFixedSize(440, 300)
        dialog.setLayoutDirection(Qt.RightToLeft)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("حذف مجموعه")
        title.setObjectName("dialogTitle")
        title.setWordWrap(True)

        description = QLabel(
            f"آیا مطمئن هستید که می‌خواهید مجموعه "
            f"«{group['name']}» را حذف کنید؟\n"
            f"این عمل قابل بازگشت نیست."
        )
        description.setObjectName("dialogDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

        buttons = QHBoxLayout()

        cancel = QPushButton("انصراف")
        cancel.setObjectName("dialogCancel")
        cancel.setCursor(Qt.PointingHandCursor)

        delete = QPushButton("حذف")
        delete.setObjectName("dialogDelete")
        delete.setCursor(Qt.PointingHandCursor)

        buttons.addWidget(cancel)
        buttons.addWidget(delete)

        layout.addLayout(buttons)

        cancel.clicked.connect(dialog.close)

        def do_delete():
            dialog.close()
            self.delete_group(group)

        delete.clicked.connect(do_delete)

        dialog.show()

    # =====================================================
    # DELETE GROUP
    # =====================================================

    def delete_group(self, group):

        try:
            complex_id = group["complexId"]

            print("========================================")
            print("DELETING GROUP:", complex_id, group["name"])
            print("========================================")

            exists = self.db.fetch_one(
                """
                SELECT complexId
                FROM complexes
                WHERE complexId = %s
                """,
                (complex_id,)
            )

            if not exists:
                NiceMessageBox.error(
                    self, "خطا",
                    "این مجموعه در دیتابیس پیدا نشد."
                )
                return

            self.db.execute("SET FOREIGN_KEY_CHECKS = 0")

            self.db.execute(
                """
                DELETE FROM loan_installments
                WHERE loanId IN (
                    SELECT loanId FROM loans
                    WHERE memberId IN (
                        SELECT memberId FROM complex_members
                        WHERE complexId = %s
                    )
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM loans
                WHERE memberId IN (
                    SELECT memberId FROM complex_members
                    WHERE complexId = %s
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM job_approvals
                WHERE employeeJobId IN (
                    SELECT employeeJobId FROM employee_jobs
                    WHERE memberId IN (
                        SELECT memberId FROM complex_members
                        WHERE complexId = %s
                    )
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM employee_jobs
                WHERE memberId IN (
                    SELECT memberId FROM complex_members
                    WHERE complexId = %s
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM bonuses
                WHERE memberId IN (
                    SELECT memberId FROM complex_members
                    WHERE complexId = %s
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM deductions
                WHERE memberId IN (
                    SELECT memberId FROM complex_members
                    WHERE complexId = %s
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM payments
                WHERE memberId IN (
                    SELECT memberId FROM complex_members
                    WHERE complexId = %s
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM salaries
                WHERE memberId IN (
                    SELECT memberId FROM complex_members
                    WHERE complexId = %s
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM attendance
                WHERE memberId IN (
                    SELECT memberId FROM complex_members
                    WHERE complexId = %s
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM leaves
                WHERE memberId IN (
                    SELECT memberId FROM complex_members
                    WHERE complexId = %s
                )
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM complex_members
                WHERE complexId = %s
                """,
                (complex_id,)
            )

            self.db.execute(
                """
                DELETE FROM complexes
                WHERE complexId = %s
                """,
                (complex_id,)
            )

            self.db.execute("SET FOREIGN_KEY_CHECKS = 1")

            still_exists = self.db.fetch_one(
                """
                SELECT complexId
                FROM complexes
                WHERE complexId = %s
                """,
                (complex_id,)
            )

            if still_exists:
                NiceMessageBox.error(
                    self, "خطا",
                    "حذف انجام نشد. لطفاً دوباره تلاش کنید."
                )
                return

            self.load_groups()
            self.refresh_groups()

            if self.parent_window:
                if hasattr(self.parent_window, "refresh_groups_from_database"):
                    self.parent_window.refresh_groups_from_database()

            NiceMessageBox.success(
                self,
                "حذف موفق",
                f"مجموعه «{group['name']}» با موفقیت حذف شد."
            )

        except Exception as error:
            print("========================================")
            print("DELETE GROUP ERROR")
            print("TYPE:", type(error).__name__)
            print("ERROR:", error)
            print("========================================")

            try:
                self.db.execute("SET FOREIGN_KEY_CHECKS = 1")
            except Exception:
                pass

            NiceMessageBox.error(
                self, "خطا",
                "در حذف مجموعه مشکلی به وجود آمد."
            )

    # =====================================================
    # ADD GROUP
    # =====================================================

    def add_group(self):

        dialog = QFrame(self, Qt.Dialog)
        dialog.setWindowTitle("افزودن مجموعه")
        dialog.setObjectName("groupDialog")
        dialog.setFixedSize(500, 580)
        dialog.setLayoutDirection(Qt.RightToLeft)

        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.setContentsMargins(26, 26, 26, 26)
        dialog_layout.setSpacing(6)

        title = QLabel("افزودن مجموعه جدید")
        title.setObjectName("dialogTitle")
        title.setWordWrap(True)

        description = QLabel("اطلاعات مجموعه را وارد کنید.")
        description.setObjectName("dialogDescription")
        description.setWordWrap(True)

        name_input = QLineEdit()
        name_input.setPlaceholderText("نام مجموعه")
        name_input.setObjectName("dialogInput")
        name_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        name_input.setLayoutDirection(Qt.RightToLeft)

        name_error = QLabel()
        name_error.setObjectName("errorLabel")
        name_error.setWordWrap(True)
        name_error.hide()

        address_input = QLineEdit()
        address_input.setPlaceholderText("آدرس مجموعه")
        address_input.setObjectName("dialogInput")
        address_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        address_input.setLayoutDirection(Qt.RightToLeft)

        address_error = QLabel()
        address_error.setObjectName("errorLabel")
        address_error.setWordWrap(True)
        address_error.hide()

        activity_input = QLineEdit()
        activity_input.setPlaceholderText("در مجموعه چه کار انجام می‌دهید؟")
        activity_input.setObjectName("dialogInput")
        activity_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        activity_input.setLayoutDirection(Qt.RightToLeft)

        activity_error = QLabel()
        activity_error.setObjectName("errorLabel")
        activity_error.setWordWrap(True)
        activity_error.hide()

        details_input = QTextEdit()
        details_input.setPlaceholderText("توضیحات بیشتر درباره مجموعه")
        details_input.setObjectName("dialogInput")
        details_input.setFixedHeight(90)
        details_input.setLayoutDirection(Qt.RightToLeft)
        details_input.document().setDefaultTextOption(
            QTextOption(Qt.AlignRight | Qt.AlignAbsolute)
        )

        buttons = QHBoxLayout()

        cancel = QPushButton("انصراف")
        cancel.setObjectName("dialogCancel")
        cancel.setCursor(Qt.PointingHandCursor)

        save = QPushButton("افزودن")
        save.setObjectName("dialogSave")
        save.setCursor(Qt.PointingHandCursor)

        buttons.addWidget(cancel)
        buttons.addWidget(save)

        dialog_layout.addWidget(title)
        dialog_layout.addWidget(description)
        dialog_layout.addWidget(name_input)
        dialog_layout.addWidget(name_error)
        dialog_layout.addWidget(address_input)
        dialog_layout.addWidget(address_error)
        dialog_layout.addWidget(activity_input)
        dialog_layout.addWidget(activity_error)
        dialog_layout.addWidget(details_input)
        dialog_layout.addStretch()
        dialog_layout.addLayout(buttons)

        cancel.clicked.connect(dialog.close)

        def clear_name_error():
            name_error.clear()
            name_error.hide()
            name_input.setStyleSheet("")

        def clear_address_error():
            address_error.clear()
            address_error.hide()
            address_input.setStyleSheet("")

        def clear_activity_error():
            activity_error.clear()
            activity_error.hide()
            activity_input.setStyleSheet("")

        name_input.textChanged.connect(clear_name_error)
        address_input.textChanged.connect(clear_address_error)
        activity_input.textChanged.connect(clear_activity_error)

        error_style = """
            QLineEdit {
                background-color: #FFF8F8;
                border: 1px solid #D93025;
                border-radius: 11px;
                padding: 10px 14px;
                color: #25364A;
                font-size: 12px;
            }
        """

        def save_group():

            name = name_input.text().strip()
            address = address_input.text().strip()
            activity = activity_input.text().strip()
            description_text = details_input.toPlainText().strip()

            has_error = False

            if not name:
                name_error.setText("لطفاً نام مجموعه را وارد کنید.")
                name_error.show()
                name_input.setStyleSheet(error_style)
                has_error = True
            elif contains_digit(name):
                name_error.setText("نام مجموعه نباید شامل عدد باشد.")
                name_error.show()
                name_input.setStyleSheet(error_style)
                has_error = True
            elif count_letters(name) < 4:
                name_error.setText("نام مجموعه باید حداقل ۴ حرف داشته باشد.")
                name_error.show()
                name_input.setStyleSheet(error_style)
                has_error = True

            if not address:
                address_error.setText("لطفاً آدرس مجموعه را وارد کنید.")
                address_error.show()
                address_input.setStyleSheet(error_style)
                has_error = True
            elif contains_digit(address):
                address_error.setText("آدرس نباید شامل عدد باشد.")
                address_error.show()
                address_input.setStyleSheet(error_style)
                has_error = True
            elif count_letters(address) < 5:
                address_error.setText("آدرس باید حداقل ۵ حرف داشته باشد.")
                address_error.show()
                address_input.setStyleSheet(error_style)
                has_error = True

            if not activity:
                activity_error.setText("لطفاً نوع فعالیت مجموعه را وارد کنید.")
                activity_error.show()
                activity_input.setStyleSheet(error_style)
                has_error = True
            elif contains_digit(activity):
                activity_error.setText("فعالیت نباید شامل عدد باشد.")
                activity_error.show()
                activity_input.setStyleSheet(error_style)
                has_error = True
            elif count_letters(activity) < 4:
                activity_error.setText("فعالیت باید حداقل ۴ حرف داشته باشد.")
                activity_error.show()
                activity_input.setStyleSheet(error_style)
                has_error = True

            if has_error:
                return

            try:
                complex_id = self.db.execute(
                    """
                    INSERT INTO complexes
                    (
                        name,
                        address,
                        description,
                        activity,
                        ownerId,
                        createdDate,
                        isActive
                    )
                    VALUES
                    (
                        %s, %s, %s, %s, %s, NOW(), '1'
                    )
                    """,
                    (
                        name,
                        address,
                        description_text or None,
                        activity,
                        self.user_id
                    )
                )

                if not complex_id:
                    NiceMessageBox.error(
                        dialog, "خطا",
                        "ثبت مجموعه انجام نشد."
                    )
                    return

                member_id = self.db.execute(
                    """
                    INSERT INTO complex_members
                    (
                        complexId,
                        userId,
                        role,
                        joinedDate,
                        isActive
                    )
                    VALUES
                    (
                        %s, %s, 'owner', NOW(), '1'
                    )
                    """,
                    (complex_id, self.user_id)
                )

                if not member_id:
                    self.db.execute(
                        "DELETE FROM complexes WHERE complexId = %s",
                        (complex_id,)
                    )

                    NiceMessageBox.error(
                        dialog, "خطا",
                        "عضویت مالک در مجموعه ثبت نشد."
                    )
                    return

                self.load_groups()
                self.refresh_groups()

                if self.parent_window:
                    if hasattr(self.parent_window, "refresh_groups_from_database"):
                        self.parent_window.refresh_groups_from_database()

                dialog.close()

                NiceMessageBox.success(
                    self, "افزودن موفق",
                    "مجموعه با موفقیت ایجاد شد."
                )

            except Exception as error:
                print("ADD GROUP ERROR:", error)
                NiceMessageBox.error(
                    dialog, "خطا",
                    "در ثبت مجموعه مشکلی به وجود آمد."
                )

        save.clicked.connect(save_group)

        dialog.show()