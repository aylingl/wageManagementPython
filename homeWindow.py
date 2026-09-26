import os

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMenu,
    QScrollArea
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class HomeWindow(QWidget):

    def __init__(self, phone_number, username, avatar):
        super().__init__()

        self.phone_number = phone_number
        self.username = username
        self.avatar = avatar

        self.current_group = "پیچک"
        self.current_role = "مالک"

        self.setWindowTitle("WageManagement")
        self.resize(1200, 750)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

    # =========================================================
    # UI
    # =========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            35, 25, 35, 20
        )

        main_layout.setSpacing(18)

        # =====================================================
        # TOP
        # =====================================================

        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)

        # -----------------------------------------------------
        # GROUP CARD
        # -----------------------------------------------------

        self.group_card = QFrame()
        self.group_card.setObjectName("groupCard")
        self.group_card.setFixedHeight(72)

        group_layout = QHBoxLayout(
            self.group_card
        )

        group_layout.setContentsMargins(
            18, 10, 18, 10
        )

        group_layout.setSpacing(12)

        group_icon = QLabel("🏢")
        group_icon.setFixedSize(42, 42)
        group_icon.setAlignment(Qt.AlignCenter)
        group_icon.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        group_icon.setStyleSheet("""
            background-color: #EAF3FF;
            border-radius: 14px;
            font-size: 20px;
            border: none;
        """)

        group_text_layout = QVBoxLayout()
        group_text_layout.setSpacing(2)

        group_title = QLabel("مجموعه")
        group_title.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        group_title.setStyleSheet("""
            color: #7A8A9D;
            font-size: 11px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)

        self.group_name_label = QLabel(
            f"{self.current_group}   •   {self.current_role}"
        )

        self.group_name_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        self.group_name_label.setStyleSheet("""
            color: #1961C7;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        group_text_layout.addWidget(
            group_title
        )

        group_text_layout.addWidget(
            self.group_name_label
        )

        group_arrow = QLabel("⌄")
        group_arrow.setFixedWidth(28)
        group_arrow.setAlignment(Qt.AlignCenter)
        group_arrow.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        group_arrow.setStyleSheet("""
            color: #4589E8;
            background: transparent;
            border: none;
            font-size: 20px;
        """)

        group_layout.addWidget(group_icon)
        group_layout.addLayout(group_text_layout)
        group_layout.addStretch()
        group_layout.addWidget(group_arrow)

        self.group_card.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        # دکمه روی کل کارت
        self.group_click_button = QPushButton(
            self.group_card
        )

        self.group_click_button.setObjectName(
            "groupClickButton"
        )

        self.group_click_button.setCursor(
            Qt.PointingHandCursor
        )

        self.group_click_button.clicked.connect(
            self.show_group_menu
        )

        # -----------------------------------------------------
        # PROFILE CARD
        # -----------------------------------------------------

        profile_card = QFrame()
        profile_card.setObjectName(
            "profileCard"
        )

        profile_card.setFixedHeight(72)

        profile_layout = QHBoxLayout(
            profile_card
        )

        profile_layout.setContentsMargins(
            18, 10, 12, 10
        )

        profile_layout.setSpacing(12)

        avatar_label = QLabel()
        avatar_label.setFixedSize(42, 42)
        avatar_label.setAlignment(Qt.AlignCenter)

        avatar_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "avatars",
            self.avatar
        )

        pixmap = QPixmap(avatar_path)

        if not pixmap.isNull():

            pixmap = pixmap.scaled(
                42,
                42,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            avatar_label.setPixmap(
                pixmap
            )

        else:
            avatar_label.setText("👤")

        avatar_label.setStyleSheet("""
            background-color: #EAF3FF;
            border-radius: 14px;
            font-size: 20px;
            border: none;
        """)

        profile_text_layout = QVBoxLayout()
        profile_text_layout.setSpacing(2)

        profile_title = QLabel(
            "پروفایل من"
        )

        profile_title.setStyleSheet("""
            color: #7A8A9D;
            font-size: 11px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)

        profile_name = QLabel(
            self.username
        )

        profile_name.setStyleSheet("""
            color: #1961C7;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        profile_text_layout.addWidget(
            profile_title
        )

        profile_text_layout.addWidget(
            profile_name
        )

        edit_button = QPushButton("✎")
        edit_button.setObjectName(
            "profileEditButton"
        )

        edit_button.setFixedSize(38, 38)
        edit_button.setCursor(
            Qt.PointingHandCursor
        )

        edit_button.setToolTip(
            "ویرایش پروفایل"
        )

        edit_button.clicked.connect(
            self.edit_profile
        )

        profile_layout.addWidget(
            avatar_label
        )

        profile_layout.addLayout(
            profile_text_layout
        )

        profile_layout.addStretch()

        profile_layout.addWidget(
            edit_button
        )

        top_layout.addWidget(
            self.group_card,
            1
        )

        top_layout.addWidget(
            profile_card,
            1
        )

        main_layout.addLayout(
            top_layout
        )

        # =====================================================
        # WELCOME
        # =====================================================

        welcome = QLabel(
            f"خوش آمدید {self.username} 👋"
        )

        welcome.setObjectName(
            "welcome"
        )

        description = QLabel(
            "به سامانه مدیریت کارکنان خوش آمدید"
        )

        description.setObjectName(
            "description"
        )

        main_layout.addWidget(
            welcome
        )

        main_layout.addWidget(
            description
        )

        # =====================================================
        # SERVICES
        # =====================================================

        services_box = QFrame()
        services_box.setObjectName(
            "servicesBox"
        )

        services_layout = QVBoxLayout(
            services_box
        )

        services_layout.setContentsMargins(
            18, 16, 18, 12
        )

        services_layout.setSpacing(10)

        services_title = QLabel(
            "دسترسی سریع"
        )

        services_title.setObjectName(
            "servicesTitle"
        )

        services_layout.addWidget(
            services_title
        )

        self.scroll = QScrollArea()

        self.scroll.setObjectName(
            "servicesScroll"
        )

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOn
        )

        self.scroll.setFixedHeight(
            245
        )

        self.scroll.setFocusPolicy(
            Qt.StrongFocus
        )

        scroll_content = QWidget()

        scroll_content.setObjectName(
            "scrollContent"
        )

        self.scroll_layout = QVBoxLayout(
            scroll_content
        )

        self.scroll_layout.setContentsMargins(
            8, 4, 18, 4
        )

        self.scroll_layout.setSpacing(
            8
        )

        self.scroll.setWidget(
            scroll_content
        )

        services_layout.addWidget(
            self.scroll
        )

        main_layout.addWidget(
            services_box
        )

        # ابتدا سرویس‌ها ساخته شوند
        self.update_services()

        main_layout.addStretch()

        # =====================================================
        # BOTTOM NAVIGATION
        # =====================================================

        nav_frame = QFrame()

        nav_frame.setObjectName(
            "navFrame"
        )

        nav_frame.setFixedHeight(
            78
        )

        nav_layout = QHBoxLayout(
            nav_frame
        )

        nav_layout.setContentsMargins(
            12, 7, 12, 7
        )

        nav_layout.setSpacing(
            4
        )

        settings_button = self.create_nav_button(
            "⚙",
            "تنظیمات"
        )

        group_button = self.create_nav_button(
            "🏢",
            "مجموعه"
        )

        home_button = self.create_nav_button(
            "⌂",
            "خانه"
        )

        messages_button = self.create_nav_button(
            "💬",
            "پیام"
        )

        settings_button.clicked.connect(
            self.open_settings
        )

        group_button.clicked.connect(
            self.open_groups
        )

        home_button.clicked.connect(
            lambda: None
        )

        messages_button.clicked.connect(
            self.open_messages
        )

        home_button.setObjectName(
            "activeNav"
        )

        nav_layout.addWidget(
            settings_button,
            1
        )

        nav_layout.addWidget(
            group_button,
            1
        )

        nav_layout.addWidget(
            home_button,
            1
        )

        nav_layout.addWidget(
            messages_button,
            1
        )

        main_layout.addWidget(
            nav_frame
        )

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }

            /* ================= GROUP ================= */

            QFrame#groupCard,
            QFrame#profileCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QFrame#groupCard:hover,
            QFrame#profileCard:hover {
                background-color: #EAF3FF;
                border: 1px solid #4589E8;
            }

            QPushButton#groupClickButton {
                background-color: transparent;
                border: none;
                border-radius: 28px;
            }

            QPushButton#groupClickButton:hover {
                background-color: transparent;
                border: none;
            }

            /* ================= PROFILE ================= */

            QPushButton#profileEditButton {
                background-color: #EAF3FF;
                color: #4589E8;
                border: none;
                border-radius: 13px;
                font-size: 20px;
                padding: 0px;
            }

            QPushButton#profileEditButton:hover {
                background-color: #DCEBFF;
                color: #1961C7;
            }

            /* ================= WELCOME ================= */

            QLabel#welcome {
                color: #1961C7;
                font-size: 25px;
                font-weight: 700;
                background: transparent;
                border: none;
            }

            QLabel#description {
                color: #7A8A9D;
                font-size: 13px;
                background: transparent;
                border: none;
            }

            /* ================= SERVICES ================= */

            QFrame#servicesBox {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QLabel#servicesTitle {
                color: #25364A;
                font-size: 17px;
                font-weight: 700;
                background: transparent;
                border: none;
            }

            QScrollArea#servicesScroll {
                background: transparent;
                border: none;
            }

            QWidget#scrollContent {
                background: transparent;
                border: none;
            }

            QFrame#serviceCard {
                background-color: #F8FAFD;
                border: 1px solid #E7EDF5;
                border-radius: 15px;
            }

            QFrame#serviceCard:hover {
                background-color: #EAF3FF;
                border: 1px solid #4589E8;
            }

            QLabel#serviceIcon {
                background-color: #EAF3FF;
                border-radius: 11px;
                font-size: 19px;
                border: none;
            }

            QLabel#serviceName {
                color: #25364A;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                border: none;
            }

            QLabel#serviceArrow {
                color: #4589E8;
                font-size: 25px;
                background: transparent;
                border: none;
            }

            QPushButton#serviceClickButton {
                background-color: transparent;
                border: none;
                border-radius: 15px;
            }

            QPushButton#serviceClickButton:hover {
                background-color: transparent;
                border: none;
            }

            /* ================= NAV ================= */

            QFrame#navFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QPushButton#navButton {
                background-color: transparent;
                border: none;
                border-radius: 20px;
                color: #7A8A9D;
                font-size: 12px;
                padding: 0px;
            }

            QPushButton#navButton:hover {
                background-color: #F3F7FC;
                color: #1961C7;
            }

            QPushButton#activeNav {
                background-color: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 20px;
            }

            /* ================= SCROLLBAR ================= */

            QScrollBar:vertical {
            width: 10px;
            background: #E8EEF6;
            border: none;
            border-radius: 5px;
            margin: 2px 0;
            }

            QScrollBar::handle:vertical {
            background: #4589E8;
            border: none;
            border-radius: 5px;
            min-height: 45px;
            margin: 0;
            }

            QScrollBar::handle:vertical:hover {
                background: #1961C7;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
                border: none;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
            }

            /* ================= MENU ================= */

            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 14px;
                padding: 6px;
                font-family: "Vazirmatn";
                font-size: 13px;
            }

            QMenu::item {
                padding: 11px 20px;
                border-radius: 8px;
            }

            QMenu::item:selected {
                background-color: #EAF3FF;
                color: #1961C7;
            }
        """)

        self.group_click_button.setGeometry(
            self.group_card.rect()
        )

    # =========================================================
    # SERVICES
    # =========================================================

    def update_services(self):

        while self.scroll_layout.count():

            item = self.scroll_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        # حضور و غیاب
        self.scroll_layout.addWidget(
            self.create_service_card(
                "👥",
                "حضور و غیاب"
            )
        )

        # امور مالی
        self.scroll_layout.addWidget(
            self.create_service_card(
                "💰",
                "امور مالی"
            )
        )

        # فقط برای مالک
        if self.current_role == "مالک":

            self.scroll_layout.addWidget(
                self.create_service_card(
                    "👨‍💼",
                    "کارمندان"
                )
            )

        # رویدادها
        self.scroll_layout.addWidget(
            self.create_service_card(
                "📋",
                "رویدادها و سوابق"
            )
        )

        # گزارش‌ها
        self.scroll_layout.addWidget(
            self.create_service_card(
                "📊",
                "گزارش‌ها"
            )
        )

        self.scroll_layout.addStretch()

        self.scroll.verticalScrollBar().setValue(
            0
        )

    # =========================================================
    # SERVICE CARD
    # =========================================================

    def create_service_card(
        self,
        icon,
        title
    ):

        card = QFrame()

        card.setObjectName(
            "serviceCard"
        )

        card.setFixedHeight(
            55
        )

        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            12, 5, 12, 5
        )

        layout.setSpacing(
            12
        )

        icon_label = QLabel(icon)

        icon_label.setObjectName(
            "serviceIcon"
        )

        icon_label.setFixedSize(
            42,
            42
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        name_label = QLabel(title)

        name_label.setObjectName(
            "serviceName"
        )

        name_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        arrow_label = QLabel("‹")

        arrow_label.setObjectName(
            "serviceArrow"
        )

        arrow_label.setFixedWidth(
            30
        )

        arrow_label.setAlignment(
            Qt.AlignCenter
        )

        arrow_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        layout.addWidget(
            icon_label
        )

        layout.addWidget(
            name_label
        )

        layout.addStretch()

        layout.addWidget(
            arrow_label
        )

        # دکمه شفاف روی کل کارت
        click_button = QPushButton(card)

        click_button.setObjectName(
            "serviceClickButton"
        )

        click_button.setCursor(
            Qt.PointingHandCursor
        )

        click_button.setGeometry(
            card.rect()
        )

        if title == "حضور و غیاب":

            click_button.clicked.connect(
                self.open_attendance
            )

        elif title == "امور مالی":

            click_button.clicked.connect(
                self.open_finance
            )

        elif title == "کارمندان":

            click_button.clicked.connect(
                self.open_employees
            )

        elif title == "رویدادها و سوابق":

            click_button.clicked.connect(
                self.open_events
            )

        elif title == "گزارش‌ها":

            click_button.clicked.connect(
                self.open_reports
            )

        click_button.raise_()

        return card

    # =========================================================
    # GROUP MENU
    # =========================================================

    def show_group_menu(self):

        menu = QMenu(self)

        menu.setLayoutDirection(
            Qt.RightToLeft
        )

        group_owner = menu.addAction(
            "پیچک   •   مالک"
        )

        group_employee = menu.addAction(
            "مجموعه کارمند   •   کارمند"
        )

        selected = menu.exec()

        if selected == group_owner:

            self.current_group = "پیچک"
            self.current_role = "مالک"

        elif selected == group_employee:

            self.current_group = "مجموعه کارمند"
            self.current_role = "کارمند"

        else:
            return

        self.group_name_label.setText(
            f"{self.current_group}   •   {self.current_role}"
        )

        self.update_services()

    # =========================================================
    # EDIT PROFILE
    # =========================================================

    def edit_profile(self):

        try:

            from editProfileWindow import EditProfileWindow

            self.edit_profile_window = EditProfileWindow(
                self.phone_number,
                self.username,
                self.avatar
            )

            self.edit_profile_window.show()

        except Exception as e:

            print(
                "Edit Profile Error:",
                e
            )

    # =========================================================
    # NAV BUTTON
    # =========================================================

    def create_nav_button(
        self,
        icon,
        title
    ):

        button = QPushButton()

        button.setObjectName(
            "navButton"
        )

        button.setFixedHeight(
            62
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        layout = QVBoxLayout(
            button
        )

        layout.setContentsMargins(
            5, 3, 5, 3
        )

        layout.setSpacing(
            2
        )

        icon_label = QLabel(icon)

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        icon_label.setStyleSheet("""
            background: transparent;
            border: none;
            font-size: 23px;
        """)

        text_label = QLabel(title)

        text_label.setAlignment(
            Qt.AlignCenter
        )

        text_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        text_label.setStyleSheet("""
            background: transparent;
            border: none;
            font-size: 11px;
        """)

        layout.addWidget(
            icon_label
        )

        layout.addWidget(
            text_label
        )

        return button

    # =========================================================
    # ATTENDANCE
    # =========================================================

    def open_attendance(self):

        print(
            "حضور و غیاب کلیک شد"
        )

        from attendanceWindow import AttendanceWindow

        self.attendance_window = AttendanceWindow(
            self.phone_number
        )

        self.attendance_window.show()

    # =========================================================
    # FINANCE
    # =========================================================

    def open_finance(self):

        from financeWindow import FinanceWindow

        self.finance_window = FinanceWindow(self.phone_number)


        self.finance_window.show()

    # =========================================================
    # EMPLOYEES
    # =========================================================

    def open_employees(self):

        print(
            "کارمندان کلیک شد"
        )

        try:

            from employeesWindow import EmployeesWindow

            self.employees_window = EmployeesWindow(
                self.phone_number
            )

            self.employees_window.show()

        except Exception as e:

            print(
                "Employees Error:",
                e
            )

    # =========================================================
    # EVENTS
    # =========================================================

    def open_events(self):

        print(
            "رویدادها و سوابق کلیک شد"
        )

        try:

            from eventsWindow import EventsWindow

            self.events_window = EventsWindow(
                self.phone_number
            )

            self.events_window.show()

        except Exception as e:

            print(
                "Events Error:",
                e
            )

    # =========================================================
    # REPORTS
    # =========================================================

    def open_reports(self):

        print(
            "گزارش‌ها کلیک شد"
        )

        try:

            from reportsWindow import ReportsWindow

            self.reports_window = ReportsWindow(
                self.phone_number
            )

            self.reports_window.show()

        except Exception as e:

            print(
                "Reports Error:",
                e
            )

    # =========================================================
    # SETTINGS
    # =========================================================

    def open_settings(self):

        print(
            "تنظیمات کلیک شد"
        )

        try:

            from settingsWindow import SettingsWindow

            self.settings_window = SettingsWindow(
                self.phone_number
            )

            self.settings_window.show()

        except Exception as e:

            print(
                "Settings Error:",
                e
            )

    # =========================================================
    # GROUPS
    # =========================================================

    def open_groups(self):

        print(
            "مجموعه کلیک شد"
        )

        try:

            from groupsWindow import GroupsWindow

            self.groups_window = GroupsWindow(
                self.phone_number
            )

            self.groups_window.show()

        except Exception as e:

            print(
                "Groups Error:",
                e
            )

    # =========================================================
    # MESSAGES
    # =========================================================

    def open_messages(self):

        print(
            "پیام کلیک شد"
        )

        try:

            from messagesWindow import MessagesWindow

            self.messages_window = MessagesWindow(
                self.phone_number
            )

            self.messages_window.show()

        except Exception as e:

            print(
                "Messages Error:",
                e
            )

    # =========================================================
    # RESIZE
    # =========================================================

    def resizeEvent(self, event):

        super().resizeEvent(
            event
        )

        if hasattr(
            self,
            "group_click_button"
        ):

            self.group_click_button.setGeometry(
                self.group_card.rect()
            )

        # اندازه دکمه‌های سرویس
        if hasattr(
            self,
            "scroll_layout"
        ):

            for i in range(
                self.scroll_layout.count()
            ):

                item = self.scroll_layout.itemAt(i)

                widget = item.widget()

                if widget and widget.objectName() == "serviceCard":

                    for child in widget.findChildren(
                        QPushButton,
                        "serviceClickButton"
                    ):

                        child.setGeometry(
                            widget.rect()
                        )