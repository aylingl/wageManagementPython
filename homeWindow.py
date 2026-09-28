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

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap, QPainter, QPainterPath

# =========================================================
# ROUNDED AVATAR
# =========================================================

class RoundedAvatar(QLabel):

    def __init__(self, size=48, parent=None):
        super().__init__(parent)

        self.avatar_size = size

        self.setFixedSize(
            size,
            size
        )

        self.setAlignment(
            Qt.AlignCenter
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground,
            True
        )

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

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

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
# HOME
# =========================================================

class HomeWindow(QWidget):

    def __init__(
        self,
        phone_number,
        username,
        avatar
    ):

        super().__init__()

        self.phone_number = phone_number
        self.username = username
        self.avatar = avatar

        self.current_group = "پیچک"
        self.current_role = "مالک"

        self.group_menu = None

        self.setWindowTitle("خانه")

        self.setMinimumSize(
            900,
            620
        )

        self.setLayoutDirection(
            Qt.RightToLeft
        )

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
            14
        )

        # =================================================
        # TOP
        # =================================================

        top_layout = QHBoxLayout()

        top_layout.setSpacing(
            14
        )

        # =================================================
        # PROFILE CARD
        # =================================================

        profile_card = QFrame()

        profile_card.setObjectName(
            "profileCard"
        )

        profile_card.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        profile_layout = QHBoxLayout(
            profile_card
        )

        profile_layout.setContentsMargins(
            16,
            10,
            16,
            10
        )

        profile_layout.setSpacing(
            12
        )

        avatar = RoundedAvatar(48)

        avatar_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "avatars",
            self.avatar
        )

        if os.path.exists(avatar_path):

            avatar.set_avatar(
                QPixmap(avatar_path)
            )

        profile_text = QVBoxLayout()

        profile_text.setContentsMargins(
            0,
            0,
            0,
            0
        )

        profile_text.setSpacing(
            2
        )

        profile_title = QLabel(
            "پروفایل من"
        )

        profile_title.setObjectName(
            "profileTitle"
        )

        username_label = QLabel(
            self.username
        )

        username_label.setObjectName(
            "usernameLabel"
        )

        profile_text.addWidget(
            profile_title
        )

        profile_text.addWidget(
            username_label
        )

        profile_edit = QPushButton(
            "✎"
        )

        profile_edit.setObjectName(
            "profileEdit"
        )

        profile_edit.setFixedSize(
            34,
            34
        )

        profile_edit.clicked.connect(
            self.open_profile
        )

        profile_layout.addWidget(
            avatar
        )

        profile_layout.addLayout(
            profile_text
        )

        profile_layout.addStretch()

        profile_layout.addWidget(
            profile_edit
        )

        # =================================================
        # GROUP CARD
        # =================================================

        self.group_card = QFrame()

        self.group_card.setObjectName(
            "groupCard"
        )

        self.group_card.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        self.group_card.setCursor(
            Qt.PointingHandCursor
        )

        self.group_card.setFixedHeight(
            72
        )

        group_layout = QHBoxLayout(
            self.group_card
        )

        group_layout.setContentsMargins(
            18,
            8,
            18,
            8
        )

        group_layout.setSpacing(
            12
        )

        # =================================================
        # BUILDING ICON
        # =================================================

        group_icon = QLabel(
            "🏢"
        )

        group_icon.setObjectName(
            "groupIcon"
        )

        group_icon.setFixedSize(
            44,
            44
        )

        group_icon.setAlignment(
            Qt.AlignCenter
        )

        group_icon.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        # =================================================
        # GROUP TEXT
        # =================================================

        group_text = QVBoxLayout()

        group_text.setContentsMargins(
            0,
            0,
            0,
            0
        )

        group_text.setSpacing(
            2
        )

        self.group_name_label = QLabel()

        self.group_name_label.setObjectName(
            "groupName"
        )

        self.group_name_label.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        group_subtitle = QLabel(
            "مجموعه فعال"
        )

        group_subtitle.setObjectName(
            "groupSubtitle"
        )

        group_subtitle.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        group_text.addWidget(
            self.group_name_label
        )

        group_text.addWidget(
            group_subtitle
        )

        group_arrow = QLabel(
            "‹"
        )

        group_arrow.setObjectName(
            "groupArrow"
        )

        group_arrow.setFixedWidth(
            20
        )

        group_arrow.setAlignment(
            Qt.AlignCenter
        )

        group_arrow.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        group_layout.addWidget(
            group_icon
        )

        group_layout.addLayout(
            group_text
        )

        group_layout.addStretch()

        group_layout.addWidget(
            group_arrow
        )

        def group_clicked(event):

            self.show_group_menu()

            event.accept()

        self.group_card.mousePressEvent = group_clicked

        top_layout.addWidget(
            profile_card,
            1
        )

        top_layout.addWidget(
            self.group_card,
            1
        )

        main_layout.addLayout(
            top_layout
        )

        # =================================================
        # WELCOME
        # =================================================

        welcome_layout = QVBoxLayout()

        welcome_layout.setContentsMargins(
            4,
            5,
            4,
            4
        )

        welcome_layout.setSpacing(
            2
        )

        welcome = QLabel(
            f"خوش آمدید {self.username} 👋"
        )

        welcome.setObjectName(
            "welcome"
        )

        welcome.setFixedHeight(
            28
        )

        welcome_sub = QLabel(
            "به سامانه مدیریت کارکنان خوش آمدید"
        )

        welcome_sub.setObjectName(
            "welcomeSub"
        )

        welcome_sub.setFixedHeight(
            20
        )

        welcome_layout.addWidget(
            welcome
        )

        welcome_layout.addWidget(
            welcome_sub
        )

        main_layout.addLayout(
            welcome_layout
        )

        # =================================================
        # SERVICES BOX
        # =================================================

        services_box = QFrame()

        services_box.setObjectName(
            "servicesBox"
        )

        services_box.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        services_box.setFixedHeight(
            255
        )

        services_layout = QVBoxLayout(
            services_box
        )

        services_layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        services_layout.setSpacing(
            6
        )

        services_title = QLabel(
            "دسترسی سریع"
        )

        services_title.setObjectName(
            "servicesTitle"
        )

        services_layout.addWidget(
            services_title
        )

        services_layout.addSpacing(
            4
        )

        # =================================================
        # SCROLL
        # =================================================

        self.scroll = QScrollArea()

        self.scroll.setObjectName(
            "servicesScroll"
        )

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOn
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

        self.scroll_layout = QVBoxLayout(
            scroll_content
        )

        self.scroll_layout.setContentsMargins(
            8,
            6,
            8,
            6
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

        # =================================================
        # BOTTOM NAV
        # =================================================

        nav_box = QFrame()

        nav_box.setObjectName(
            "navBox"
        )

        nav_box.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        nav_box.setFixedHeight(
            76
        )

        nav_layout = QHBoxLayout(
            nav_box
        )

        nav_layout.setContentsMargins(
            12,
            8,
            12,
            8
        )

        nav_layout.setSpacing(
            8
        )

        settings_btn = self.create_nav_button(
            "⚙",
            "تنظیمات",
            self.open_settings
        )

        group_btn = self.create_nav_button(
            "🏢",
            "مجموعه",
            self.Open_groups
        )

        home_btn = self.create_nav_button(
            "⌂",
            "خانه",
            lambda: None
        )

        message_btn = self.create_nav_button(
            "✉",
            "پیام",
            self.open_messages
        )

        nav_layout.addWidget(
            settings_btn
        )

        nav_layout.addWidget(
            group_btn
        )

        nav_layout.addWidget(
            home_btn
        )

        nav_layout.addWidget(
            message_btn
        )

        main_layout.addWidget(
            nav_box
        )

        # =================================================
        # INITIAL
        # =================================================

        self.update_group_text()

        self.update_services()

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
               PROFILE
            ============================================= */

            QFrame#profileCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QLabel#profileTitle {
                background: transparent;
                border: none;
                color: #25364A;
                font-size: 13px;
                font-weight: 600;
                padding: 0px;
                margin: 0px;
            }

            QLabel#usernameLabel {
                background: transparent;
                border: none;
                color: #718096;
                font-size: 11px;
                padding: 0px;
                margin: 0px;
            }

            QPushButton#profileEdit {
                background-color: #F1F6FD;
                color: #1961C7;
                border: none;
                border-radius: 17px;
                font-size: 18px;
            }

            QPushButton#profileEdit:hover {
                background-color: #EAF3FF;
            }

            /* =============================================
               GROUP
            ============================================= */

            QFrame#groupCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QFrame#groupCard:hover {
                background-color: #EAF3FF;
                border: 1px solid #4589E8;
                border-radius: 28px;
            }

            QLabel#groupIcon {
                background-color: transparent;
                border: none;
                color: #1961C7;
                font-size: 29px;
                font-weight: 700;
                padding: 0px;
                margin: 0px;
            }

            QLabel#groupName {
                background-color: transparent;
                border: none;
                color: #25364A;
                font-size: 13px;
                font-weight: 600;
                padding: 0px;
                margin: 0px;
            }

            QLabel#groupSubtitle {
                background-color: transparent;
                border: none;
                color: #8997A8;
                font-size: 10px;
                padding: 0px;
                margin: 0px;
            }

            QLabel#groupArrow {
                background-color: transparent;
                border: none;
                color: #4589E8;
                font-size: 24px;
                padding: 0px;
                margin: 0px;
            }

            /* =============================================
               WELCOME
            ============================================= */

            QLabel#welcome {
                background-color: transparent;
                border: none;
                color: #1E2F43;
                font-size: 19px;
                font-weight: 700;
                padding: 0px;
                margin: 0px;
            }

            QLabel#welcomeSub {
                background-color: transparent;
                border: none;
                color: #8290A1;
                font-size: 11px;
                padding: 0px;
                margin: 0px;
            }

            /* =============================================
               SERVICES
            ============================================= */

            QFrame#servicesBox {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QLabel#servicesTitle {
                background-color: transparent;
                border: none;
                color: #25364A;
                font-size: 14px;
                font-weight: 700;
                padding: 0px;
                margin: 0px;
            }

            QScrollArea#servicesScroll {
                background-color: transparent;
                border: none;
            }

            QScrollArea#servicesScroll > QWidget {
                background-color: transparent;
                border: none;
            }

            QWidget#scrollContent {
                background-color: transparent;
                border: none;
            }

            /* =============================================
               SCROLLBAR
            ============================================= */

            QScrollBar:vertical {
                width: 10px;
                background: #E8EEF6;
                border: none;
                border-radius: 5px;
                margin: 5px 0px;
            }

            QScrollBar::handle:vertical {
                background: #4589E8;
                border: none;
                border-radius: 5px;
                min-height: 45px;
                margin: 0px;
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

            /* =============================================
               SERVICE CARD
            ============================================= */

            QFrame#serviceCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }

            QFrame#serviceCard:hover {
                background-color: #EAF3FF;
                border: 1px solid #4589E8;
                border-radius: 20px;
            }

            QLabel#serviceIcon {
                background-color: #EAF3FF;
                border: none;
                border-radius: 19px;
                color: #1961C7;
                font-size: 18px;
                padding: 0px;
                margin: 0px;
            }

            QLabel#serviceTitle {
                background-color: transparent;
                border: none;
                color: #25364A;
                font-size: 12px;
                font-weight: 600;
                padding: 0px;
                margin: 0px;
            }

            QLabel#serviceArrow {
                background-color: transparent;
                border: none;
                color: #8A98A9;
                font-size: 22px;
                padding: 0px;
                margin: 0px;
            }

            /* =============================================
               BOTTOM NAV
            ============================================= */

            QFrame#navBox {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 24px;
            }

            QPushButton#navButton {
                background-color: transparent;
                color: #718096;
                border: none;
                border-radius: 16px;
                padding: 8px;
                font-size: 16px;
                font-weight: 500;
                min-height: 48px;
            }

            QPushButton#navButton:hover {
                background-color: #EAF3FF;
                color: #1961C7;
            }

            /* =============================================
               GROUP POPUP
            ============================================= */

            QFrame#groupPopup {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 22px;
            }

            QFrame#groupOption {
                background-color: #F8FAFD;
                border: 1px solid #E7EDF5;
                border-radius: 15px;
            }

            QFrame#groupOption:hover {
                background-color: #EAF3FF;
                border: 1px solid #4589E8;
                border-radius: 15px;
            }

            QLabel#groupOptionLabel {
                background-color: transparent;
                border: none;
                color: #25364A;
                font-size: 13px;
                padding: 0px;
                margin: 0px;
            }
        """)

    # =====================================================
    # GROUP TEXT
    # =====================================================

    def update_group_text(self):

        self.group_name_label.setText(
            f"{self.current_group}   •   {self.current_role}"
        )

    # =====================================================
    # GROUP MENU
    # =====================================================

    def show_group_menu(self):

        # اگر popup باز است، دوباره بازش نکن
        if (
            self.group_menu is not None
            and self.group_menu.isVisible()
        ):
            return

        menu = QFrame(self)

        menu.setObjectName(
            "groupPopup"
        )

        menu.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        menu.setFixedWidth(
            250
        )

        layout = QVBoxLayout(
            menu
        )

        layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        layout.setSpacing(
            8
        )

        # =================================================
        # OWNER
        # =================================================

        owner_button = QFrame()

        owner_button.setObjectName(
            "groupOption"
        )

        owner_button.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        owner_button.setCursor(
            Qt.PointingHandCursor
        )

        owner_button.setFixedHeight(
            46
        )

        owner_layout = QHBoxLayout(
            owner_button
        )

        owner_layout.setContentsMargins(
            14,
            0,
            14,
            0
        )

        owner_label = QLabel(
            "پیچک   •   مالک"
        )

        owner_label.setObjectName(
            "groupOptionLabel"
        )

        owner_label.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        owner_layout.addWidget(
            owner_label
        )

        # =================================================
        # EMPLOYEE
        # =================================================

        employee_button = QFrame()

        employee_button.setObjectName(
            "groupOption"
        )

        employee_button.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        employee_button.setCursor(
            Qt.PointingHandCursor
        )

        employee_button.setFixedHeight(
            46
        )

        employee_layout = QHBoxLayout(
            employee_button
        )

        employee_layout.setContentsMargins(
            14,
            0,
            14,
            0
        )

        employee_label = QLabel(
            "مجموعه کارمند   •   کارمند"
        )

        employee_label.setObjectName(
            "groupOptionLabel"
        )

        employee_label.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        employee_layout.addWidget(
            employee_label
        )

        layout.addWidget(
            owner_button
        )

        layout.addWidget(
            employee_button
        )

        # =================================================
        # SELECT
        # =================================================

        def select_owner(event):

            self.current_group = "پیچک"
            self.current_role = "مالک"

            self.update_group_text()
            self.update_services()

            menu.close()

            self.group_menu = None

            event.accept()

        def select_employee(event):

            self.current_group = "مجموعه کارمند"
            self.current_role = "کارمند"

            self.update_group_text()
            self.update_services()

            menu.close()

            self.group_menu = None

            event.accept()

        owner_button.mousePressEvent = select_owner

        employee_button.mousePressEvent = select_employee

        # =================================================
        # SHOW
        # =================================================

        menu.adjustSize()

        pos = self.group_card.mapToGlobal(
            QPoint(
                self.group_card.width() - menu.width(),
                self.group_card.height() + 8
            )
        )

        local_pos = self.mapFromGlobal(
            pos
        )

        menu.move(
            local_pos
        )

        self.group_menu = menu

        menu.show()

        menu.raise_()

    # =====================================================
    # SERVICES
    # =====================================================

    def update_services(self):

        while self.scroll_layout.count():

            item = self.scroll_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.scroll_layout.addWidget(
            self.create_service_card(
                "🕒",
                "حضور و غیاب",
                self.open_attendance
            )
        )

        self.scroll_layout.addWidget(
            self.create_service_card(
                "💰",
                "امور مالی",
                self.open_finance
            )
        )

        if self.current_role == "مالک":

            self.scroll_layout.addWidget(
                self.create_service_card(
                    "👥",
                    "کارمندان",
                    self.open_employees
                )
            )
            self.scroll_layout.addWidget(
                self.create_service_card(
                    "📥",
                    "کارتابل",
                    self.open_cartable
                )
            )

        self.scroll_layout.addWidget(
            self.create_service_card(
                "📅",
                "رویدادها و سوابق",
                self.open_events
            )
        )

        self.scroll_layout.addWidget(
            self.create_service_card(
                "📊",
                "گزارش‌ها",
                self.open_reports
            )
        )

        self.scroll_layout.addStretch()

    # =====================================================
    # SERVICE CARD
    # =====================================================

    def create_service_card(
        self,
        icon,
        title,
        callback
    ):

        card = QFrame()

        card.setObjectName(
            "serviceCard"
        )

        card.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        card.setCursor(
            Qt.PointingHandCursor
        )

        card.setFixedHeight(
            58
        )

        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            12,
            6,
            12,
            6
        )

        layout.setSpacing(
            12
        )

        icon_label = QLabel(
            icon
        )

        icon_label.setObjectName(
            "serviceIcon"
        )

        icon_label.setFixedSize(
            38,
            38
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "serviceTitle"
        )

        title_label.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        arrow = QLabel(
            "‹"
        )

        arrow.setObjectName(
            "serviceArrow"
        )

        arrow.setFixedWidth(
            20
        )

        arrow.setAlignment(
            Qt.AlignCenter
        )

        arrow.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        layout.addWidget(
            icon_label
        )

        layout.addWidget(
            title_label
        )

        layout.addStretch()

        layout.addWidget(
            arrow
        )

        def clicked(event):

            callback()

            event.accept()

        card.mousePressEvent = clicked

        return card

    # =====================================================
    # NAV BUTTON
    # =====================================================

    def create_nav_button(
        self,
        icon,
        text,
        callback
    ):

        button = QPushButton()

        button.setObjectName(
            "navButton"
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.setText(
            f"{icon}   {text}"
        )

        button.clicked.connect(
            callback
        )

        return button

    # =====================================================
    # PROFILE
    # =====================================================

    def open_profile(self):
        from editProfileWindow import EditProfileWindow


        self.edit_profile_window = EditProfileWindow(

            self,
            phone_number=self.phone_number,
            username=self.username,
            avatar=self.avatar
        )


        self.edit_profile_window.resize(

            self.size()
        )
        
        self.edit_profile_window.move(
            self.pos()
        )
        self.edit_profile_window.show()
        self.edit_profile_window.raise_()
    # =====================================================
    # ATTENDANCE
    # =====================================================

    def open_attendance(self):

        from attendanceWindow import AttendanceWindow

        self.attendance_window = AttendanceWindow(
            self.phone_number
        )

        self.attendance_window.resize(
            self.size()
        )

        self.attendance_window.move(
            self.pos()
        )

        self.attendance_window.show()

    # =====================================================
    # FINANCE
    # =====================================================

    def open_finance(self):

        from financeWindow import FinanceWindow

        self.finance_window = FinanceWindow(
            self.phone_number
        )

        self.finance_window.resize(
            self.size()
        )

        self.finance_window.move(
            self.pos()
        )

        self.finance_window.show()

    # =====================================================
    # employees
    # =====================================================

    def open_employees(self):
        from employeesWindow import EmployeesWindow
        self.employees_window = EmployeesWindow(self.phone_number)
        self.employees_window.resize(
            self.size()
        )
        self.employees_window.move(
            self.pos()
        )
        self.employees_window.show()
    # =====================================================
    # events
    # =====================================================

    def open_events(self):
        from eventsWindow import EventsWindow
        self.events_window = EventsWindow(
            self
        )
        self.events_window.resize(
            self.size()
        )
        self.events_window.move(
            self.pos()
        )
        self.events_window.show()

        self.events_window.raise_()

        


      
    # =====================================================
    # gozaresh
    # =====================================================

    def open_reports(self):
        print("گزارش‌ها کلیک شد")
    # =====================================================
    # tanzimat
    # =====================================================

    def open_settings(self):
        from settingsWindow import  SettingsWindow
        self.settings_window = SettingsWindow(self)

        self.settings_window.resize(
            self.size()
        )
        self.settings_window.move(
            self.pos()
        )
        self.settings_window.show()
        self.settings_window.raise_()        
    # =====================================================
    # payam
    # =====================================================

    def open_messages(self):
        from messagesWindow import MessagesWindow
        self.messages_window = MessagesWindow(
            self
        )
        self.messages_window.resize(
            self.size()
        )
        self.messages_window.move(
            self.pos()

        )
        self.messages_window.show()

        self.messages_window.raise_()
    # =====================================================
    # cartable
    # =====================================================
    
    def open_cartable(self):
        from cartableWindow import CartableWindow
        self.cartable_window = CartableWindow(self)
        self.cartable_window.resize(
            self.size()
        )
        self.cartable_window.move(
            self.pos()
        )
        self.cartable_window.show()
    # =====================================================
    # GROUP
    # =====================================================
    def Open_groups(self):
        from groupsWindow import GroupsWindow
        self.groups_window = GroupsWindow(
            self,
            self.phone_number
        )

        self.groups_window.resize(
            self.size()
        )
        self.groups_window.move(
            self.pos()
        )

        self.groups_window.show()
        self.groups_window.raise_()