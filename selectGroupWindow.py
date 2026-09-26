from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame
)
from PySide6.QtCore import Qt

class SelectGroupWindow(QWidget):

    def __init__(self, phone_number):
        super().__init__()

        self.phone_number = phone_number

        self.setWindowTitle("مجموعه‌های من")
        self.resize(1200, 750)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

    def setup_ui(self):

        # =========================
        # Main Layout
        # =========================

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(80, 40, 80, 25)
        main_layout.setSpacing(20)

        # =========================
        # Header
        # =========================

        header = QHBoxLayout()
        header.setSpacing(15)

        user_info = QVBoxLayout()
        user_info.setSpacing(4)

        name = QLabel("دانش رضایی")
        name.setObjectName("userName")

        phone = QLabel(self.phone_number)
        phone.setObjectName("userPhone")

        user_info.addWidget(name)
        user_info.addWidget(phone)

        edit_button = QPushButton("✎")
        edit_button.setObjectName("editButton")
        edit_button.setFixedSize(42, 42)

        header.addLayout(user_info)
        header.addStretch()
        header.addWidget(edit_button)

        main_layout.addLayout(header)

        # =========================
        # Title
        # =========================

        title = QLabel("مجموعه‌های شما")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("مجموعه‌های تحت نظارت شما")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        main_layout.addSpacing(20)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # =========================
        # Groups
        # =========================

        groups_layout = QVBoxLayout()
        groups_layout.setSpacing(14)

        group1 = self.create_group_card(
            "مجموعه ۲",
            "مالک"
        )

        group2 = self.create_group_card(
            "مجموعه کارمند",
            "کارمند"
        )

        groups_layout.addWidget(group1)
        groups_layout.addWidget(group2)

        main_layout.addLayout(groups_layout)

        # =========================
        # Add Group
        # =========================

        add_button = QPushButton("+  افزودن مجموعه جدید")
        add_button.setObjectName("addButton")
        add_button.setFixedHeight(48)

        main_layout.addWidget(
            add_button,
            alignment=Qt.AlignCenter
        )

        main_layout.addStretch()

        # =========================
        # Bottom Menu
        # =========================

        bottom_box = QFrame()
        bottom_box.setObjectName("bottomBox")
        bottom_box.setFixedHeight(75)

        bottom_layout = QHBoxLayout(bottom_box)
        bottom_layout.setContentsMargins(15, 8, 15, 8)
        bottom_layout.setSpacing(8)

        settings_button = self.create_bottom_button(
            "⚙",
            "تنظیمات"
        )

        message_button = self.create_bottom_button(
            "💬",
            "پیام‌ها"
        )

        notification_button = self.create_bottom_button(
            "🔔",
            "اعلان‌ها"
        )

        profile_button = self.create_bottom_button(
            "👤",
            "پروفایل"
        )

        bottom_layout.addWidget(settings_button)
        bottom_layout.addWidget(message_button)
        bottom_layout.addWidget(notification_button)
        bottom_layout.addWidget(profile_button)

        main_layout.addWidget(bottom_box)

        self.setLayout(main_layout)

        # =========================
        # Style
        # =========================

        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }

            /* Header */

            #userName {
                color: #1D2939;
                font-size: 17px;
                font-weight: 600;
            }

            #userPhone {
                color: #98A2B3;
                font-size: 13px;
            }

            #editButton {
                background-color: white;
                color: #4589E8;
                border: 1px solid #E1EAF5;
                border-radius: 12px;
                font-size: 20px;
            }

            #editButton:hover {
                background-color: #EAF3FF;
                border: 1px solid #4589E8;
            }

            /* Title */

            #title {
                color: #1961C7;
                font-size: 25px;
                font-weight: 700;
            }

            #subtitle {
                color: #667085;
                font-size: 14px;
            }

            /* Group Card */

            #groupCard {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 16px;
            }

            #groupCard:hover {
                background-color: #EAF3FF;
                border: 1px solid #4589E8;
            }

            #groupName {
                color: #1D2939;
                font-size: 16px;
                font-weight: 600;
            }

            #groupRole {
                color: #667085;
                font-size: 13px;
            }

            #arrowButton {
                background-color: transparent;
                color: #4589E8;
                border: none;
                font-size: 27px;
            }

            /* Add */

            #addButton {
                background-color: white;
                color: #4589E8;
                border: 1px dashed #8CB8EE;
                border-radius: 13px;
                padding: 0 25px;
                font-size: 14px;
            }

            #addButton:hover {
                background-color: #EAF3FF;
                border: 1px dashed #4589E8;
            }

            /* Bottom Menu */

            #bottomBox {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 18px;
            }

            #bottomButton {
                background-color: transparent;
                color: #667085;
                border: none;
                border-radius: 12px;
                font-size: 13px;
            }

            #bottomButton:hover {
                background-color: #EAF3FF;
                color: #1961C7;
            }

        """)

    # =====================================
    # Create Group Card
    # =====================================

    def create_group_card(self, group_name, role):

        card = QFrame()
        card.setObjectName("groupCard")
        card.setFixedHeight(85)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 10, 15, 10)
        layout.setSpacing(15)

        information = QVBoxLayout()
        information.setSpacing(5)

        name = QLabel(group_name)
        name.setObjectName("groupName")

        role_label = QLabel(role)
        role_label.setObjectName("groupRole")

        information.addWidget(name)
        information.addWidget(role_label)

        arrow = QPushButton("‹")
        arrow.setObjectName("arrowButton")
        arrow.setFixedSize(40, 50)

        layout.addLayout(information)
        layout.addStretch()
        layout.addWidget(arrow)

        return card

    # =====================================
    # Create Bottom Button
    # =====================================

    def create_bottom_button(self, icon, text):

        button = QPushButton()

        button.setObjectName("bottomButton")
        button.setFixedHeight(58)

        layout = QVBoxLayout(button)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            background: transparent;
            border: none;
            font-size: 19px;
        """)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("""
            background: transparent;
            border: none;
            font-size: 11px;
            color: inherit;
        """)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)

        return button