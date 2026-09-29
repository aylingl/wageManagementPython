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
        self.employees = []
        self.selected_group = None
        self.user_id = None

        self.setWindowTitle("مجموعه‌ها")
        self.setMinimumSize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()
        self.load_data()

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

                NiceMessageBox.warning(
                    self, "خطا",
                    "اطلاعات کاربر پیدا نشد."
                )
                return

            self.user_id = user["userId"]

            self.load_groups()
            self.load_employees()

            self.refresh_groups()
            self.refresh_employees()

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
                    AND cm.isActive = 1
                WHERE c.isActive = 1
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
                      AND isActive = 1
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

                employees = self.get_group_employee_names(row["complexId"])

                self.groups.append(
                    {
                        "complexId": row["complexId"],
                        "name": row["name"],
                        "address": row["address"] or "بدون آدرس",
                        "activity": row["activity"] or "بدون فعالیت",
                        "description": row["description"] or "بدون توضیحات",
                        "role": role_text,
                        "roleValue": role,
                        "employees": employees,
                        "employeeCount": count
                    }
                )

        except Exception as error:

            print("LOAD GROUPS ERROR:", error)

    # =====================================================
    # LOAD EMPLOYEES
    # =====================================================

    def load_employees(self):

        self.employees = []

        try:

            rows = self.db.fetch_all(
                """
                SELECT userId, name, phoneNumber
                FROM users
                WHERE userId <> %s
                ORDER BY userId DESC
                """,
                (self.user_id,)
            )

            for row in rows:

                self.employees.append(
                    {
                        "userId": row["userId"],
                        "name": row["name"] or "بدون نام",
                        "phoneNumber": row["phoneNumber"]
                    }
                )

        except Exception as error:

            print("LOAD EMPLOYEES ERROR:", error)

    # =====================================================
    # GET GROUP EMPLOYEES
    # =====================================================

    def get_group_employee_names(self, complex_id):

        try:

            rows = self.db.fetch_all(
                """
                SELECT u.userId, u.name
                FROM complex_members cm
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                  AND cm.isActive = 1
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
    # SETUP UI
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
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.go_back)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("مجموعه‌ها")
        title.setObjectName("title")

        subtitle = QLabel("مجموعه‌های خودت را مدیریت و کارکنانت را اضافه کن")
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

        # SCROLL
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("scrollContent")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 12, 20, 12)
        content_layout.setSpacing(18)

        scroll.setWidget(content)

        groups_title = QLabel("مجموعه‌های من")
        groups_title.setObjectName("sectionTitle")

        content_layout.addWidget(groups_title)

        self.groups_container = QVBoxLayout()
        self.groups_container.setSpacing(10)

        content_layout.addLayout(self.groups_container)

        employees_title = QLabel("کارکنان")
        employees_title.setObjectName("sectionTitle")

        content_layout.addWidget(employees_title)

        employees_description = QLabel(
            "کارکنان خود را ببین و آن‌ها را به مجموعه موردنظر اضافه کن."
        )
        employees_description.setObjectName("description")

        content_layout.addWidget(employees_description)

        self.employees_container = QVBoxLayout()
        self.employees_container.setSpacing(10)

        content_layout.addLayout(self.employees_container)

        content_layout.addStretch()

        main_layout.addWidget(scroll)

        # STYLE
        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
                color: #25364A;
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

            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea::viewport {
                background: transparent;
                border: none;
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

            QLabel#sectionTitle {
                background: transparent;
                border: none;
                color: #25364A;
                font-size: 16px;
                font-weight: 700;
                padding-top: 5px;
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
                border-radius: 10px;
                padding: 5px, 9px, 0px, 0px ;
                font-size: 10px;
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

            QPushButton#employeeRoleButton {
                background-color: #F1F6FD;
                color: #1961C7;
                border: none;
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 10px;
                font-weight: 600;
            }

            QFrame#employeeCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 18px;
            }

            QFrame#employeeCard:hover {
                border-color: #C9DDF5;
                background-color: #FBFDFF;
            }

            QLabel#employeeAvatar {
                background-color: #EAF3FF;
                border: none;
                border-radius: 20px;
                color: #1961C7;
                font-size: 16px;
            }

            QLabel#employeeName {
                background: transparent;
                border: none;
                color: #25364A;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#employeeStatus {
                background: transparent;
                border: none;
                color: #8290A1;
                font-size: 10px;
            }

            QPushButton#addEmployeeButton {
                background-color: #EAF3FF;
                color: #1961C7;
                border: 1px solid #C9DDF5;
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 10px;
                font-weight: 600;
            }

            QPushButton#addEmployeeButton:hover {
                background-color: #DDEEFF;
            }

            QFrame#groupDialog,
            QFrame#employeeDialog,
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

            QPushButton#groupSelectButton {
                background-color: #F5F8FC;
                color: #25364A;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                padding: 10px;
                text-align: right;
                font-size: 12px;
            }

            QPushButton#groupSelectButton:hover {
                background-color: #EAF3FF;
                border-color: #4589E8;
            }

            QPushButton#registerEmployeeButton {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#registerEmployeeButton:hover {
                background-color: #4589E8;
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
        count.setFixedHeight(26)
        count.setFixedWidth(60)

        layout.addWidget(icon)
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(count)

        if group["role"] == "مالک":

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

        else:

            role_button = QPushButton("کارمند")
            role_button.setObjectName("employeeRoleButton")
            role_button.setEnabled(False)

            layout.addWidget(role_button)

        return card

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

            print("DELETING GROUP:", complex_id, group["name"])

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

                if hasattr(
                    self.parent_window,
                    "refresh_groups_from_database"
                ):
                    self.parent_window.refresh_groups_from_database()

            NiceMessageBox.success(
                self,
                "حذف موفق",
                f"مجموعه «{group['name']}» با موفقیت حذف شد."
            )

        except Exception as error:

            print("DELETE GROUP ERROR:", error)

            NiceMessageBox.error(
                self, "خطا",
                "در حذف مجموعه مشکلی به وجود آمد."
            )

    # =====================================================
    # REFRESH EMPLOYEES
    # =====================================================

    def refresh_employees(self):

        while self.employees_container.count():

            item = self.employees_container.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        for employee in self.employees:

            card = self.create_employee_card(employee)
            self.employees_container.addWidget(card)

    # =====================================================
    # EMPLOYEE CARD
    # =====================================================

    def create_employee_card(self, employee):

        card = QFrame()
        card.setObjectName("employeeCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setFixedHeight(70)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        avatar = QLabel("👤")
        avatar.setObjectName("employeeAvatar")
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        name = QLabel(employee["name"])
        name.setObjectName("employeeName")
        name.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        status = QLabel("کاربر")
        status.setObjectName("employeeStatus")
        status.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        text_layout.addWidget(name)
        text_layout.addWidget(status)

        add_button = QPushButton("افزودن به مجموعه")
        add_button.setObjectName("addEmployeeButton")
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.clicked.connect(
            lambda checked=False, e=employee: self.add_employee_to_group(e)
        )

        layout.addWidget(avatar)
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(add_button)

        return card

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

        # NAME
        name_input = QLineEdit()
        name_input.setPlaceholderText("نام مجموعه")
        name_input.setObjectName("dialogInput")
        name_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        name_input.setLayoutDirection(Qt.RightToLeft)

        name_error = QLabel()
        name_error.setObjectName("errorLabel")
        name_error.setWordWrap(True)
        name_error.hide()

        # ADDRESS
        address_input = QLineEdit()
        address_input.setPlaceholderText("آدرس مجموعه")
        address_input.setObjectName("dialogInput")
        address_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        address_input.setLayoutDirection(Qt.RightToLeft)

        address_error = QLabel()
        address_error.setObjectName("errorLabel")
        address_error.setWordWrap(True)
        address_error.hide()

        # ACTIVITY
        activity_input = QLineEdit()
        activity_input.setPlaceholderText("در مجموعه چه کار انجام می‌دهید؟")
        activity_input.setObjectName("dialogInput")
        activity_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        activity_input.setLayoutDirection(Qt.RightToLeft)

        activity_error = QLabel()
        activity_error.setObjectName("errorLabel")
        activity_error.setWordWrap(True)
        activity_error.hide()

        # DESCRIPTION
        details_input = QTextEdit()
        details_input.setPlaceholderText("توضیحات بیشتر درباره مجموعه")
        details_input.setObjectName("dialogInput")
        details_input.setFixedHeight(90)
        details_input.setLayoutDirection(Qt.RightToLeft)
        details_input.document().setDefaultTextOption(
            QTextOption(Qt.AlignRight | Qt.AlignAbsolute)
        )

        # BUTTONS
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

            # NAME
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

            # ADDRESS
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

            # ACTIVITY
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
                        %s, %s, %s, %s, %s, NOW(), 1
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
                        %s, %s, 'owner', NOW(), 1
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
                    if hasattr(
                        self.parent_window,
                        "refresh_groups_from_database"
                    ):
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

    # =====================================================
    # ADD EMPLOYEE
    # =====================================================

    def add_employee_to_group(self, employee):

        owner_groups = [
            g for g in self.groups
            if g["role"] in ("مالک", "مالک و کارمند")
        ]

        if not owner_groups:

            NiceMessageBox.warning(
                self, "مجموعه",
                "شما مالک هیچ مجموعه‌ای نیستید."
            )
            return

        dialog = QFrame(self, Qt.Dialog)
        dialog.setWindowTitle("افزودن کارمند")
        dialog.setObjectName("employeeDialog")
        dialog.setFixedSize(440, 380)
        dialog.setLayoutDirection(Qt.RightToLeft)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        title = QLabel(f"افزودن «{employee['name']}» به مجموعه")
        title.setObjectName("dialogTitle")
        title.setWordWrap(True)

        layout.addWidget(title)

        description = QLabel("مجموعه موردنظر را انتخاب کنید.")
        description.setObjectName("dialogDescription")
        description.setWordWrap(True)

        layout.addWidget(description)

        self.selected_group = None

        for group in owner_groups:

            button = QPushButton(f"🏢  {group['name']}")
            button.setObjectName("groupSelectButton")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, g=group, b=button:
                self.select_group_button(g, b)
            )

            layout.addWidget(button)

        layout.addStretch()

        buttons = QHBoxLayout()

        cancel = QPushButton("انصراف")
        cancel.setObjectName("dialogCancel")
        cancel.setCursor(Qt.PointingHandCursor)

        register = QPushButton("ثبت")
        register.setObjectName("registerEmployeeButton")
        register.setCursor(Qt.PointingHandCursor)

        buttons.addWidget(cancel)
        buttons.addWidget(register)

        layout.addLayout(buttons)

        cancel.clicked.connect(dialog.close)

        register.clicked.connect(
            lambda: self.register_employee_to_group(employee, dialog)
        )

        dialog.show()

    # =====================================================
    # SELECT GROUP BUTTON
    # =====================================================

    def select_group_button(self, group, button):

        self.selected_group = group

        button.setStyleSheet("""
            QPushButton {
                background-color: #EAF3FF;
                color: #1961C7;
                border: 1px solid #1961C7;
                border-radius: 11px;
                padding: 10px;
                text-align: right;
                font-size: 12px;
            }
        """)

    # =====================================================
    # REGISTER EMPLOYEE
    # =====================================================

    def register_employee_to_group(self, employee, dialog):

        if self.selected_group is None:

            NiceMessageBox.warning(
                dialog, "خطا",
                "لطفاً ابتدا یک مجموعه را انتخاب کنید."
            )
            return

        group = self.selected_group

        try:

            existing = self.db.fetch_one(
                """
                SELECT memberId, role, isActive
                FROM complex_members
                WHERE complexId = %s AND userId = %s
                LIMIT 1
                """,
                (group["complexId"], employee["userId"])
            )

            if existing:

                if existing["isActive"] == 1:

                    NiceMessageBox.warning(
                        dialog, "خطا",
                        f"{employee['name']} قبلاً عضو این مجموعه است."
                    )
                    return

                self.db.execute(
                    """
                    UPDATE complex_members
                    SET role = 'employee',
                        isActive = 1,
                        joinedDate = NOW()
                    WHERE memberId = %s
                    """,
                    (existing["memberId"],)
                )

            else:

                self.db.execute(
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
                        %s, %s, 'employee', NOW(), 1
                    )
                    """,
                    (group["complexId"], employee["userId"])
                )

            self.load_groups()
            self.load_employees()
            self.refresh_groups()

            dialog.close()

            NiceMessageBox.success(
                self, "افزودن موفق",
                f"{employee['name']} به مجموعه «{group['name']}» اضافه شد."
            )

        except Exception as error:

            print("REGISTER EMPLOYEE ERROR:", error)

            NiceMessageBox.error(
                dialog, "خطا",
                "در ثبت کارمند مشکلی به وجود آمد."
            )

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