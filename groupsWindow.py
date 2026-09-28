from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QLineEdit,
    QMessageBox,
    QTextEdit
)

from PySide6.QtCore import Qt

class GroupsWindow(QWidget):

    def __init__(
        self,
        parent_window=None,
        phone_number="09123456789"
    ):
        super().__init__()

        self.parent_window = parent_window
        self.phone_number = phone_number

        self.setWindowTitle(
            "مجموعه‌ها"
        )

        self.setMinimumSize(
            900,
            620
        )

        self.setLayoutDirection(
            Qt.RightToLeft
        )

        # =================================================
        # SAMPLE DATA
        # =================================================

        self.groups = [
            {
                "name": "پیچک",
                "address": "تهران",
                "activity": "فروش و خدمات",
                "description": "مدیریت سفارش‌ها و ارائه خدمات",
                "role": "مالک",
                "employees": [
                    "علی رضایی",
                    "سارا محمدی"
                ]
            },
            {
                "name": "مجموعه کارمند",
                "address": "چابهار",
                "activity": "خدمات و پشتیبانی",
                "description": "انجام امور مربوط به خدمات مجموعه",
                "role": "کارمند",
                "employees": [
                    "محمد احمدی"
                ]
            }
        ]

        self.employees = [
            "علی رضایی",
            "سارا محمدی",
            "محمد احمدی",
            "نگار کریمی"
        ]

        self.setup_ui()

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            28,
            22,
            28,
            22
        )

        main_layout.setSpacing(
            16
        )

        # =================================================
        # HEADER
        # =================================================

        header_layout = QHBoxLayout()

        header_layout.setSpacing(
            12
        )

        back_button = QPushButton(
            "›"
        )

        back_button.setObjectName(
            "backButton"
        )

        back_button.setFixedSize(
            42,
            42
        )

        back_button.setCursor(
            Qt.PointingHandCursor
        )

        back_button.clicked.connect(
            self.go_back
        )

        header_layout.addWidget(
            back_button
        )

        title_layout = QVBoxLayout()

        title_layout.setSpacing(
            3
        )

        title = QLabel(
            "مجموعه‌ها"
        )

        title.setObjectName(
            "title"
        )

        subtitle = QLabel(
            "مجموعه‌های خودت را مدیریت و کارکنانت را اضافه کن"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        header_layout.addLayout(
            title_layout
        )

        header_layout.addStretch()

        add_group_button = QPushButton(
            "+  افزودن مجموعه"
        )

        add_group_button.setObjectName(
            "addGroupButton"
        )

        add_group_button.setCursor(
            Qt.PointingHandCursor
        )

        add_group_button.clicked.connect(
            self.add_group
        )

        header_layout.addWidget(
            add_group_button
        )

        main_layout.addLayout(
            header_layout
        )

        # =================================================
        # SCROLL
        # =================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        content = QWidget()

        content.setObjectName(
            "scrollContent"
        )

        content_layout = QVBoxLayout(
            content
        )

        # فاصله بیشتر از اطراف اسکرول
        content_layout.setContentsMargins(
            8,
            12,
            20,
            12
        )

        content_layout.setSpacing(
            18
        )

        scroll.setWidget(
            content
        )

        # =================================================
        # GROUPS TITLE
        # =================================================

        groups_title = QLabel(
            "مجموعه‌های من"
        )

        groups_title.setObjectName(
            "sectionTitle"
        )

        content_layout.addWidget(
            groups_title
        )

        # =================================================
        # GROUPS
        # =================================================

        self.groups_container = QVBoxLayout()

        self.groups_container.setSpacing(
            10
        )

        content_layout.addLayout(
            self.groups_container
        )

        # =================================================
        # EMPLOYEES TITLE
        # =================================================

        employees_title = QLabel(
            "کارکنان"
        )

        employees_title.setObjectName(
            "sectionTitle"
        )

        content_layout.addWidget(
            employees_title
        )

        employees_description = QLabel(
            "کارکنان خود را ببین و آن‌ها را به مجموعه موردنظر اضافه کن."
        )

        employees_description.setObjectName(
            "description"
        )

        content_layout.addWidget(
            employees_description
        )

        # =================================================
        # EMPLOYEES
        # =================================================

        self.employees_container = QVBoxLayout()

        self.employees_container.setSpacing(
            10
        )

        content_layout.addLayout(
            self.employees_container
        )

        content_layout.addStretch()

        main_layout.addWidget(
            scroll
        )

        # =================================================
        # INITIAL DATA
        # =================================================

        self.refresh_groups()

        self.refresh_employees()

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
                color: #25364A;
            }

            /* =============================================
               HEADER
            ============================================= */

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

            /* =============================================
               SCROLL
            ============================================= */

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

            /* =============================================
               SECTION
            ============================================= */

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

            /* =============================================
               GROUP CARD
            ============================================= */

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
                padding: 5px 9px;
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

            QPushButton#employeeRoleButton {
                background-color: #F1F6FD;
                color: #1961C7;
                border: none;
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 10px;
                font-weight: 600;
            }

            /* =============================================
               EMPLOYEE CARD
            ============================================= */

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

            /* =============================================
               DIALOG
            ============================================= */

            QFrame#groupDialog,
            QFrame#employeeDialog {
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
            }

            QLabel#dialogDescription {
                background: transparent;
                border: none;
                color: #8290A1;
                font-size: 11px;
            }

            QLineEdit#dialogInput,
            QTextEdit#dialogInput {
                background-color: #F5F8FC;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                padding: 10px;
                color: #25364A;
                font-size: 11px;
            }

            QLineEdit#dialogInput:focus,
            QTextEdit#dialogInput:focus {
                border-color: #4589E8;
            }

            QPushButton#dialogCancel {
                background-color: #F5F8FC;
                color: #526273;
                border: 1px solid #E2EAF4;
                border-radius: 10px;
                padding: 10px;
            }

            QPushButton#dialogSave {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }

            QPushButton#groupSelectButton {
                background-color: #F5F8FC;
                color: #25364A;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                padding: 10px;
                text-align: right;
            }

            QPushButton#groupSelectButton:hover {
                background-color: #EAF3FF;
                border-color: #4589E8;
            }

            QPushButton#groupSelectButton:selected {
                background-color: #EAF3FF;
                border-color: #1961C7;
            }

            QPushButton#registerEmployeeButton {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 11px;
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

    # =====================================================
    # REFRESH GROUPS
    # =====================================================

    def refresh_groups(self):

        while self.groups_container.count():

            item = self.groups_container.takeAt(
                0
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

        for group in self.groups:

            card = self.create_group_card(
                group
            )

            self.groups_container.addWidget(
                card
            )

    # =====================================================
    # GROUP CARD
    # =====================================================

    def create_group_card(
        self,
        group
    ):

        card = QFrame()

        card.setObjectName(
            "groupCard"
        )

        card.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        card.setFixedHeight(
            100
        )

        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            14,
            10,
            14,
            10
        )

        layout.setSpacing(
            12
        )

        # =================================================
        # ICON
        # =================================================

        icon = QLabel(
            "🏢"
        )

        icon.setObjectName(
            "groupIcon"
        )

        icon.setFixedSize(
            42,
            42
        )

        icon.setAlignment(
            Qt.AlignCenter
        )

        # =================================================
        # TEXT
        # =================================================

        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            2
        )

        name = QLabel(
            group["name"]
        )

        name.setObjectName(
            "groupName"
        )

        address = QLabel(
            f"آدرس: {group['address']}"
        )

        address.setObjectName(
            "groupAddress"
        )

        activity = QLabel(
            f"فعالیت: {group['activity']}"
        )

        activity.setObjectName(
            "groupActivity"
        )

        text_layout.addWidget(
            name
        )

        text_layout.addWidget(
            address
        )

        text_layout.addWidget(
            activity
        )

        # =================================================
        # EMPLOYEE COUNT
        # =================================================

        count = QLabel(
            f"{len(group['employees'])} کارمند"
        )

        count.setObjectName(
            "employeeCount"
        )

        count.setAlignment(
            Qt.AlignCenter
        )

        # =================================================
        # ROLE BUTTON
        # =================================================

        if group["role"] == "مالک":

            action_button = QPushButton(
                "مدیریت"
            )

            action_button.setObjectName(
                "manageButton"
            )

            action_button.setCursor(
                Qt.PointingHandCursor
            )

            action_button.clicked.connect(
                lambda checked=False,
                g=group: self.manage_group(g)
            )

        else:

            action_button = QPushButton(
                "کارمند"
            )

            action_button.setObjectName(
                "employeeRoleButton"
            )

            action_button.setEnabled(
                False
            )

        # =================================================
        # ADD TO CARD
        # =================================================

        layout.addWidget(
            icon
        )

        layout.addLayout(
            text_layout
        )

        layout.addStretch()

        layout.addWidget(
            count
        )

        layout.addWidget(
            action_button
        )

        return card

    # =====================================================
    # REFRESH EMPLOYEES
    # =====================================================

    def refresh_employees(self):

        while self.employees_container.count():

            item = self.employees_container.takeAt(
                0
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

        for employee in self.employees:

            card = self.create_employee_card(
                employee
            )

            self.employees_container.addWidget(
                card
            )

    # =====================================================
    # EMPLOYEE CARD
    # =====================================================

    def create_employee_card(
        self,
        employee
    ):

        card = QFrame()

        card.setObjectName(
            "employeeCard"
        )

        card.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        card.setFixedHeight(
            70
        )

        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            12,
            8,
            12,
            8
        )

        layout.setSpacing(
            10
        )

        avatar = QLabel(
            "👤"
        )

        avatar.setObjectName(
            "employeeAvatar"
        )

        avatar.setFixedSize(
            40,
            40
        )

        avatar.setAlignment(
            Qt.AlignCenter
        )

        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            2
        )

        name = QLabel(
            employee
        )

        name.setObjectName(
            "employeeName"
        )

        status = QLabel(
            "کارمند"
        )

        status.setObjectName(
            "employeeStatus"
        )

        text_layout.addWidget(
            name
        )

        text_layout.addWidget(
            status
        )

        add_button = QPushButton(
            "افزودن به مجموعه"
        )

        add_button.setObjectName(
            "addEmployeeButton"
        )

        add_button.setCursor(
            Qt.PointingHandCursor
        )

        add_button.clicked.connect(
            lambda checked=False,
            e=employee: self.add_employee_to_group(e)
        )

        layout.addWidget(
            avatar
        )

        layout.addLayout(
            text_layout
        )

        layout.addStretch()

        layout.addWidget(
            add_button
        )

        return card

    # =====================================================
    # ADD GROUP
    # =====================================================

    def add_group(self):

        dialog = QFrame(
            self,
            Qt.Dialog
        )

        dialog.setWindowTitle(
            "افزودن مجموعه"
        )

        dialog.setObjectName(
            "groupDialog"
        )

        dialog.setFixedSize(
            460,
            420
        )

        dialog_layout = QVBoxLayout(
            dialog
        )

        dialog_layout.setContentsMargins(
            24,
            24,
            24,
            24
        )

        dialog_layout.setSpacing(
            10
        )

        title = QLabel(
            "افزودن مجموعه جدید"
        )

        title.setObjectName(
            "dialogTitle"
        )

        description = QLabel(
            "اطلاعات مجموعه را وارد کنید."
        )

        description.setObjectName(
            "dialogDescription"
        )

        name_input = QLineEdit()

        name_input.setPlaceholderText(
            "نام مجموعه"
        )

        name_input.setObjectName(
            "dialogInput"
        )

        address_input = QLineEdit()

        address_input.setPlaceholderText(
            "آدرس مجموعه"
        )

        address_input.setObjectName(
            "dialogInput"
        )

        activity_input = QLineEdit()

        activity_input.setPlaceholderText(
            "داخل مجموعه چه کاری انجام می‌شود؟"
        )

        activity_input.setObjectName(
            "dialogInput"
        )

        details_input = QTextEdit()

        details_input.setPlaceholderText(
            "توضیحات بیشتر درباره مجموعه"
        )

        details_input.setObjectName(
            "dialogInput"
        )

        details_input.setFixedHeight(
            80
        )

        buttons = QHBoxLayout()

        cancel = QPushButton(
            "انصراف"
        )

        cancel.setObjectName(
            "dialogCancel"
        )

        save = QPushButton(
            "افزودن"
        )

        save.setObjectName(
            "dialogSave"
        )

        buttons.addWidget(
            cancel
        )

        buttons.addWidget(
            save
        )

        dialog_layout.addWidget(
            title
        )

        dialog_layout.addWidget(
            description
        )

        dialog_layout.addWidget(
            name_input
        )

        dialog_layout.addWidget(
            address_input
        )

        dialog_layout.addWidget(
            activity_input
        )

        dialog_layout.addWidget(
            details_input
        )

        dialog_layout.addStretch()

        dialog_layout.addLayout(
            buttons
        )

        cancel.clicked.connect(
            dialog.close
        )

        def save_group():

            name = (
                name_input
                .text()
                .strip()
            )

            address = (
                address_input
                .text()
                .strip()
            )

            activity = (
                activity_input
                .text()
                .strip()
            )

            description_text = (
                details_input
                .toPlainText()
                .strip()
            )

            if not name:

                QMessageBox.warning(
                    dialog,
                    "خطا",
                    "لطفاً نام مجموعه را وارد کنید."
                )

                return

            if not activity:

                QMessageBox.warning(
                    dialog,
                    "خطا",
                    "لطفاً نوع فعالیت مجموعه را وارد کنید."
                )

                return

            self.groups.append(
                {
                    "name": name,
                    "address": address or "بدون آدرس",
                    "activity": activity,
                    "description": description_text or "بدون توضیحات",
                    "role": "مالک",
                    "employees": []
                }
            )

            self.refresh_groups()

            dialog.close()

        save.clicked.connect(
            save_group
        )

        dialog.show()

    # =====================================================
    # ADD EMPLOYEE TO GROUP
    # =====================================================

    def add_employee_to_group(
        self,
        employee
    ):

        # فقط مجموعه‌هایی که کاربر مالک آن‌هاست
        owner_groups = [
            group
            for group in self.groups
            if group["role"] == "مالک"
        ]

        if not owner_groups:

            QMessageBox.warning(
                self,
                "مجموعه",
                "شما مالک هیچ مجموعه‌ای نیستید."
            )

            return

        dialog = QFrame(
            self,
            Qt.Dialog
        )

        dialog.setWindowTitle(
            "افزودن کارمند"
        )

        dialog.setObjectName(
            "employeeDialog"
        )

        dialog.setFixedSize(
            400,
            320
        )

        layout = QVBoxLayout(
            dialog
        )

        layout.setContentsMargins(
            22,
            22,
            22,
            22
        )

        layout.setSpacing(
            10
        )

        title = QLabel(
            f"افزودن «{employee}» به مجموعه"
        )

        title.setObjectName(
            "dialogTitle"
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "مجموعه موردنظر را انتخاب کنید."
        )

        description.setObjectName(
            "dialogDescription"
        )

        layout.addWidget(
            description
        )

        # مجموعه انتخاب‌شده
        self.selected_group = None

        for group in owner_groups:

            button = QPushButton(
                f"🏢  {group['name']}"
            )

            button.setObjectName(
                "groupSelectButton"
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.clicked.connect(
                lambda checked=False,
                g=group,
                b=button:
                self.select_group_button(
                    g,
                    b
                )
            )

            layout.addWidget(
                button
            )

        layout.addStretch()

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        cancel = QPushButton(
            "انصراف"
        )

        cancel.setObjectName(
            "dialogCancel"
        )

        register = QPushButton(
            "ثبت"
        )

        register.setObjectName(
            "registerEmployeeButton"
        )

        buttons.addWidget(
            cancel
        )

        buttons.addWidget(
            register
        )

        layout.addLayout(
            buttons
        )

        cancel.clicked.connect(
            dialog.close
        )

        register.clicked.connect(
            lambda: self.register_employee_to_group(
                employee,
                dialog
            )
        )

        dialog.show()

    # =====================================================
    # SELECT GROUP BUTTON
    # =====================================================

    def select_group_button(
        self,
        group,
        button
    ):

        self.selected_group = group

        button.setStyleSheet("""
            QPushButton {
                background-color: #EAF3FF;
                color: #1961C7;
                border: 1px solid #1961C7;
                border-radius: 11px;
                padding: 10px;
                text-align: right;
            }
        """)

    # =====================================================
    # REGISTER EMPLOYEE
    # =====================================================

    def register_employee_to_group(
        self,
        employee,
        dialog
    ):

        if self.selected_group is None:

            QMessageBox.warning(
                dialog,
                "خطا",
                "لطفاً ابتدا یک مجموعه را انتخاب کنید."
            )

            return

        group = self.selected_group

        if employee not in group["employees"]:

            group["employees"].append(
                employee
            )

        self.refresh_groups()

        dialog.close()

        QMessageBox.information(
            self,
            "انجام شد",
            f"{employee} به مجموعه «{group['name']}» اضافه شد."
        )

    # =====================================================
    # SELECT GROUP
    # =====================================================

    def select_group_for_employee(
        self,
        employee,
        group,
        dialog
    ):

        if employee not in group["employees"]:

            group["employees"].append(
                employee
            )

        self.refresh_groups()

        dialog.close()

        QMessageBox.information(
            self,
            "انجام شد",
            f"{employee} به مجموعه «{group['name']}» اضافه شد."
        )

    # =====================================================
    # MANAGE GROUP
    # =====================================================

    def manage_group(
        self,
        group
    ):

        employees = group["employees"]

        if employees:

            employee_text = "\n".join(
                f"• {employee}"
                for employee in employees
            )

        else:

            employee_text = (
                "هنوز کارمندی به این مجموعه اضافه نشده است."
            )

        QMessageBox.information(
            self,
            group["name"],
            (
                f"مجموعه: {group['name']}\n"
                f"آدرس: {group['address']}\n"
                f"فعالیت: {group['activity']}\n\n"
                f"توضیحات:\n"
                f"{group['description']}\n\n"
                f"کارکنان:\n\n"
                f"{employee_text}"
            )
        )