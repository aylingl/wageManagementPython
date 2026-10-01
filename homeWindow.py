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

from database import Database

# =========================================================
# ROUNDED AVATAR
# =========================================================

class RoundedAvatar(QLabel):

    def __init__(self, size=48, parent=None):
        super().__init__(parent)

        self.avatar_size = size

        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def set_avatar(self, pixmap):

        if pixmap is None or pixmap.isNull():
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
# HOME WINDOW
# =========================================================

class HomeWindow(QWidget):

    def __init__(
        self,
        phone_number=None,
        username="",
        avatar="",
        email=None
    ):

        super().__init__()

        self.phone_number = phone_number
        self.email = email
        self.username = username
        self.avatar = avatar

        self.db = Database()

        self.user_id = None

        self.current_group = "بدون مجموعه"
        self.current_role = "کاربر"

        self.groups = []

        self.group_menu = None

        self.load_user_information()

        self.setWindowTitle("خانه")
        self.resize(900, 620)
        self.setMinimumSize(500, 450)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

    # =====================================================
    # LOAD USER INFORMATION
    # =====================================================

    def load_user_information(self):

        try:

            if self.email:

                user = self.db.fetch_one(
                    """
                    SELECT
                        userId,
                        name,
                        imageBase64
                    FROM users
                    WHERE email = %s
                    LIMIT 1
                    """,
                    (self.email,)
                )

            else:

                user = self.db.fetch_one(
                    """
                    SELECT
                        userId,
                        name,
                        imageBase64
                    FROM users
                    WHERE phoneNumber = %s
                    LIMIT 1
                    """,
                    (self.phone_number,)
                )

            if not user:
                return

            self.user_id = user["userId"]

            if user.get("name"):
                self.username = user["name"]

            if user.get("imageBase64"):
                self.avatar = user["imageBase64"]

            self.groups = self.load_groups_from_database()

            if self.groups:

                first_group = self.groups[0]

                self.current_group = first_group["name"] or "بدون نام"

                rv = first_group.get("role", "employee")

                if rv == "owner":
                    self.current_role = "مالک"
                elif rv == "employee":
                    self.current_role = "کارمند"
                elif rv == "both":
                    self.current_role = "مالک و کارمند"
                else:
                    self.current_role = "کاربر"

        except Exception as e:

            print("Error loading home information:", e)

    # =====================================================
    # LOAD GROUPS FROM DATABASE
    # =====================================================

    def load_groups_from_database(self):

        if not self.user_id:
            return []

        try:

            groups = self.db.fetch_all(
                """
                SELECT
                    c.complexId,
                    c.name,
                    c.address,
                    c.ownerId,
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

            print("========================================")
            print("LOAD HOME GROUPS")
            print("USER ID:", self.user_id)
            print("GROUPS FROM DATABASE:", groups)
            print("GROUP COUNT:", len(groups))
            print("========================================")

            return groups or []

        except Exception as error:

            print("LOAD HOME GROUPS ERROR:")
            print(type(error).__name__)
            print(error)

            return []

    # =====================================================
    # GET CURRENT COMPLEX ID
    # =====================================================

    def get_current_complex_id(self):

        for group in self.groups:

            if (group.get("name") or "بدون نام") == self.current_group:

                return group.get("complexId")

        if self.groups:
            return self.groups[0].get("complexId")

        return None

    # =====================================================
    # CLOSE GROUP MENU
    # =====================================================

    def close_group_menu(self):

        if self.group_menu is not None:

            try:
                self.group_menu.close()
                self.group_menu.deleteLater()

            except Exception as error:
                print("GROUP MENU CLOSE ERROR:", error)

            self.group_menu = None

    # =====================================================
    # ROLE HELPER
    # =====================================================

    def get_role_text(self, role_value):

        if role_value == "owner":
            return "مالک"
        elif role_value == "employee":
            return "کارمند"
        elif role_value == "both":
            return "مالک و کارمند"
        else:
            return "کاربر"

    # =====================================================
    # REFRESH GROUPS FROM DATABASE
    # =====================================================

    def refresh_groups_from_database(self):

        try:

            if not self.user_id:
                print("HOME REFRESH: USER ID IS NONE")
                return

            print("========================================")
            print("START HOME GROUP REFRESH")

            popup_was_visible = False

            if self.group_menu is not None:
                popup_was_visible = self.group_menu.isVisible()
                self.close_group_menu()

            self.groups = self.load_groups_from_database()

            if self.groups:

                current_exists = any(
                    (group["name"] or "بدون نام") == self.current_group
                    for group in self.groups
                )

                if not current_exists:

                    first_group = self.groups[0]

                    self.current_group = first_group["name"] or "بدون نام"

                    rv = first_group.get("role", "employee")

                    self.current_role = self.get_role_text(rv)

            else:

                self.current_group = "بدون مجموعه"
                self.current_role = "کاربر"

            self.update_group_text()
            self.update_services()

            print("NEW GROUPS:", self.groups)
            print("NEW CURRENT GROUP:", self.current_group)
            print("========================================")

            if popup_was_visible:
                self.show_group_menu()

        except Exception as error:

            print("HOME GROUP REFRESH ERROR")
            print(type(error).__name__)
            print(error)

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(14)

        # ---------------------------------------------
        # TOP
        # ---------------------------------------------

        top_layout = QHBoxLayout()
        top_layout.setSpacing(14)

        # ---------------------------------------------
        # PROFILE CARD
        # ---------------------------------------------

        profile_card = QFrame()
        profile_card.setObjectName("profileCard")
        profile_card.setAttribute(Qt.WA_StyledBackground, True)

        profile_layout = QHBoxLayout(profile_card)
        profile_layout.setContentsMargins(16, 10, 16, 10)
        profile_layout.setSpacing(12)

        avatar = RoundedAvatar(48)

        avatar_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "avatars",
            self.avatar
        )

        if os.path.exists(avatar_path):
            avatar.set_avatar(QPixmap(avatar_path))

        profile_text = QVBoxLayout()
        profile_text.setContentsMargins(0, 0, 0, 0)
        profile_text.setSpacing(2)

        profile_title = QLabel("پروفایل من")
        profile_title.setObjectName("profileTitle")

        username_label = QLabel(self.username)
        username_label.setObjectName("usernameLabel")

        profile_text.addWidget(profile_title)
        profile_text.addWidget(username_label)

        profile_edit = QPushButton("✎")
        profile_edit.setObjectName("profileEdit")
        profile_edit.setFixedSize(34, 34)
        profile_edit.clicked.connect(self.open_profile)

        profile_layout.addWidget(avatar)
        profile_layout.addLayout(profile_text)
        profile_layout.addStretch()
        profile_layout.addWidget(profile_edit)

        # ---------------------------------------------
        # GROUP CARD
        # ---------------------------------------------

        self.group_card = QFrame()
        self.group_card.setObjectName("groupCard")
        self.group_card.setAttribute(Qt.WA_StyledBackground, True)
        self.group_card.setCursor(Qt.PointingHandCursor)
        self.group_card.setFixedHeight(72)

        group_layout = QHBoxLayout(self.group_card)
        group_layout.setContentsMargins(18, 8, 18, 8)
        group_layout.setSpacing(12)

        group_icon = QLabel("🏢")
        group_icon.setObjectName("groupIcon")
        group_icon.setFixedSize(44, 44)
        group_icon.setAlignment(Qt.AlignCenter)
        group_icon.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        group_text = QVBoxLayout()
        group_text.setContentsMargins(0, 0, 0, 0)
        group_text.setSpacing(2)

        self.group_name_label = QLabel()
        self.group_name_label.setObjectName("groupName")
        self.group_name_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        group_subtitle = QLabel("مجموعه فعال")
        group_subtitle.setObjectName("groupSubtitle")
        group_subtitle.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        group_text.addWidget(self.group_name_label)
        group_text.addWidget(group_subtitle)

        group_arrow = QLabel("‹")
        group_arrow.setObjectName("groupArrow")
        group_arrow.setFixedWidth(20)
        group_arrow.setAlignment(Qt.AlignCenter)
        group_arrow.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        group_layout.addWidget(group_icon)
        group_layout.addLayout(group_text)
        group_layout.addStretch()
        group_layout.addWidget(group_arrow)

        def group_clicked(event):
            self.show_group_menu()
            event.accept()

        self.group_card.mousePressEvent = group_clicked

        top_layout.addWidget(profile_card, 1)
        top_layout.addWidget(self.group_card, 1)

        main_layout.addLayout(top_layout)

        # ---------------------------------------------
        # WELCOME
        # ---------------------------------------------

        welcome_layout = QVBoxLayout()
        welcome_layout.setContentsMargins(4, 5, 4, 4)
        welcome_layout.setSpacing(2)

        welcome = QLabel(f"خوش آمدید {self.username} 👋")
        welcome.setObjectName("welcome")
        welcome.setFixedHeight(28)

        welcome_sub = QLabel("به سامانه مدیریت کارکنان خوش آمدید")
        welcome_sub.setObjectName("welcomeSub")
        welcome_sub.setFixedHeight(20)

        welcome_layout.addWidget(welcome)
        welcome_layout.addWidget(welcome_sub)

        main_layout.addLayout(welcome_layout)

        # ---------------------------------------------
        # SERVICES BOX
        # ---------------------------------------------

        services_box = QFrame()
        services_box.setObjectName("servicesBox")
        services_box.setAttribute(Qt.WA_StyledBackground, True)
        services_box.setMinimumHeight(200)

        services_layout = QVBoxLayout(services_box)
        services_layout.setContentsMargins(18, 14, 18, 14)
        services_layout.setSpacing(6)

        services_title = QLabel("دسترسی سریع")
        services_title.setObjectName("servicesTitle")

        services_layout.addWidget(services_title)
        services_layout.addSpacing(4)

        # SCROLL
        self.scroll = QScrollArea()
        self.scroll.setObjectName("servicesScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setAttribute(Qt.WA_TranslucentBackground, True)

        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(8, 6, 8, 6)
        self.scroll_layout.setSpacing(8)

        self.scroll.setWidget(scroll_content)

        services_layout.addWidget(self.scroll)

        main_layout.addWidget(services_box, 1)

        # ---------------------------------------------
        # BOTTOM NAV
        # ---------------------------------------------

        nav_box = QFrame()
        nav_box.setObjectName("navBox")
        nav_box.setAttribute(Qt.WA_StyledBackground, True)
        nav_box.setFixedHeight(76)

        nav_layout = QHBoxLayout(nav_box)
        nav_layout.setContentsMargins(12, 8, 12, 8)
        nav_layout.setSpacing(8)

        settings_btn = self.create_nav_button("⚙", "تنظیمات", self.open_settings)
        group_btn = self.create_nav_button("🏢", "مجموعه", self.Open_groups)
        home_btn = self.create_nav_button("⌂", "خانه", lambda: None)
        message_btn = self.create_nav_button("✉", "پیام", self.open_messages)

        nav_layout.addWidget(settings_btn)
        nav_layout.addWidget(group_btn)
        nav_layout.addWidget(home_btn)
        nav_layout.addWidget(message_btn)

        main_layout.addWidget(nav_box)

        # ---------------------------------------------
        # INITIAL
        # ---------------------------------------------

        self.update_group_text()
        self.update_services()

        # ---------------------------------------------
        # STYLE
        # ---------------------------------------------

        self.setStyleSheet("""

            QWidget {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
                color: #25364A;
            }

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
            }

            QLabel#usernameLabel {
                background: transparent;
                border: none;
                color: #718096;
                font-size: 11px;
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
            }

            QLabel#groupName {
                background-color: transparent;
                border: none;
                color: #25364A;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#groupSubtitle {
                background-color: transparent;
                border: none;
                color: #8997A8;
                font-size: 10px;
            }

            QLabel#groupArrow {
                background-color: transparent;
                border: none;
                color: #4589E8;
                font-size: 24px;
            }

            QLabel#welcome {
                background-color: transparent;
                border: none;
                color: #1E2F43;
                font-size: 19px;
                font-weight: 700;
            }

            QLabel#welcomeSub {
                background-color: transparent;
                border: none;
                color: #8290A1;
                font-size: 11px;
            }

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
            }

            QLabel#serviceTitle {
                background-color: transparent;
                border: none;
                color: #25364A;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#serviceArrow {
                background-color: transparent;
                border: none;
                color: #8A98A9;
                font-size: 22px;
            }

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
            }

            QScrollArea#groupPopupScroll {
                background: transparent;
                border: none;
            }

            QScrollArea#groupPopupScroll > QWidget {
                background: transparent;
                border: none;
            }

            QWidget#groupPopupContent {
                background: transparent;
                border: none;
            }

            QScrollArea#groupPopupScroll QScrollBar:vertical {
                width: 6px;
                background: #EEF3FA;
                border: none;
                border-radius: 3px;
                margin: 4px 0px;
            }

            QScrollArea#groupPopupScroll QScrollBar::handle:vertical {
                background: #4589E8;
                border: none;
                border-radius: 3px;
                min-height: 24px;
            }

            QScrollArea#groupPopupScroll QScrollBar::handle:vertical:hover {
                background: #1961C7;
            }

            QScrollArea#groupPopupScroll QScrollBar::add-line:vertical,
            QScrollArea#groupPopupScroll QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
                border: none;
            }

            QScrollArea#groupPopupScroll QScrollBar::add-page:vertical,
            QScrollArea#groupPopupScroll QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
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

        try:

            print("OPEN GROUP MENU")

            if self.group_menu is not None:
                self.close_group_menu()

            if self.user_id:
                self.groups = self.load_groups_from_database()

            print("GROUPS USED FOR POPUP:", self.groups)

            menu = QFrame(self)
            menu.setObjectName("groupPopup")
            menu.setAttribute(Qt.WA_StyledBackground, True)
            menu.setFixedWidth(250)
            menu.setLayoutDirection(Qt.RightToLeft)

            menu_layout = QVBoxLayout(menu)
            menu_layout.setContentsMargins(8, 8, 8, 8)
            menu_layout.setSpacing(0)

            scroll = QScrollArea()
            scroll.setObjectName("groupPopupScroll")
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            scroll_content = QWidget()
            scroll_content.setObjectName("groupPopupContent")
            scroll_content.setAttribute(Qt.WA_TranslucentBackground, True)

            layout = QVBoxLayout(scroll_content)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(8)

            if self.groups:

                for group in self.groups:

                    group_button = QFrame()
                    group_button.setObjectName("groupOption")
                    group_button.setAttribute(Qt.WA_StyledBackground, True)
                    group_button.setCursor(Qt.PointingHandCursor)
                    group_button.setFixedHeight(46)

                    group_layout = QHBoxLayout(group_button)
                    group_layout.setContentsMargins(14, 0, 14, 0)

                    group_name = group["name"] or "بدون نام"

                    role_value = group.get("role", "employee")
                    role_text = self.get_role_text(role_value)

                    group_label = QLabel(
                        f"{group_name}   •   {role_text}"
                    )
                    group_label.setObjectName("groupOptionLabel")
                    group_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                    group_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    group_layout.addWidget(group_label)

                    def select_group(event, selected_group=group):

                        self.current_group = selected_group["name"] or "بدون نام"

                        rv = selected_group.get("role", "employee")

                        self.current_role = self.get_role_text(rv)

                        self.update_group_text()
                        self.update_services()
                        self.close_group_menu()

                        event.accept()

                    group_button.mousePressEvent = select_group

                    layout.addWidget(group_button)

            else:

                empty_option = QFrame()
                empty_option.setObjectName("groupOption")
                empty_option.setAttribute(Qt.WA_StyledBackground, True)
                empty_option.setFixedHeight(46)

                empty_layout = QHBoxLayout(empty_option)
                empty_layout.setContentsMargins(14, 0, 14, 0)

                empty_label = QLabel("هنوز مجموعه‌ای ثبت نشده")
                empty_label.setObjectName("groupOptionLabel")
                empty_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                empty_layout.addWidget(empty_label)
                layout.addWidget(empty_option)

            layout.addStretch()

            scroll.setWidget(scroll_content)
            menu_layout.addWidget(scroll)

            item_height = 54
            items_count = max(len(self.groups), 1)

            content_height = items_count * item_height + 16
            menu_height = min(content_height, 300)

            menu.setFixedHeight(menu_height)

            menu.adjustSize()

            pos = self.group_card.mapToGlobal(
                QPoint(
                    self.group_card.width() - menu.width(),
                    self.group_card.height() + 8
                )
            )

            local_pos = self.mapFromGlobal(pos)
            menu.move(local_pos)

            self.group_menu = menu

            menu.show()
            menu.raise_()

            print("GROUP POPUP CREATED SUCCESSFULLY")

        except Exception as error:

            print("SHOW GROUP MENU ERROR")
            print(type(error).__name__)
            print(error)

    # =====================================================
    # SERVICES
    # =====================================================

    def update_services(self):

        while self.scroll_layout.count():

            item = self.scroll_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.scroll_layout.addWidget(
            self.create_service_card("🕒", "حضور و غیاب", self.open_attendance)
        )

        self.scroll_layout.addWidget(
            self.create_service_card("💰", "امور مالی", self.open_finance)
        )

        if self.current_role in ("مالک", "مالک و کارمند"):

            self.scroll_layout.addWidget(
                self.create_service_card("👥", "کارمندان", self.open_employees)
            )

            self.scroll_layout.addWidget(
                self.create_service_card("📥", "کارتابل", self.open_cartable)
            )

        self.scroll_layout.addWidget(
            self.create_service_card("📅", "رویدادها و سوابق", self.open_events)
        )

        self.scroll_layout.addWidget(
            self.create_service_card("📊", "گزارش‌ها", self.open_reports)
        )

        self.scroll_layout.addStretch()

    # =====================================================
    # SERVICE CARD
    # =====================================================

    def create_service_card(self, icon, title, callback):

        card = QFrame()
        card.setObjectName("serviceCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setCursor(Qt.PointingHandCursor)
        card.setFixedHeight(58)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setObjectName("serviceIcon")
        icon_label.setFixedSize(38, 38)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        title_label = QLabel(title)
        title_label.setObjectName("serviceTitle")
        title_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        arrow = QLabel("‹")
        arrow.setObjectName("serviceArrow")
        arrow.setFixedWidth(20)
        arrow.setAlignment(Qt.AlignCenter)
        arrow.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(arrow)

        def clicked(event):
            callback()
            event.accept()

        card.mousePressEvent = clicked

        return card

    # =====================================================
    # NAV BUTTON
    # =====================================================

    def create_nav_button(self, icon, text, callback):

        button = QPushButton()
        button.setObjectName("navButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setText(f"{icon}   {text}")
        button.clicked.connect(callback)

        return button

    # =====================================================
    # OPEN WINDOWS
    # =====================================================

    def open_profile(self):

        from editProfileWindow import EditProfileWindow

        self.edit_profile_window = EditProfileWindow(
            self,
            phone_number=self.phone_number,
            username=self.username,
            national_code="",
            avatar=self.avatar
        )

        self.edit_profile_window.resize(self.size())
        self.edit_profile_window.move(self.pos())
        self.edit_profile_window.show()
        self.edit_profile_window.raise_()

    def open_attendance(self):

        from attendanceWindow import AttendanceWindow

        complex_id = self.get_current_complex_id()

        self.attendance_window = AttendanceWindow(
            self.phone_number,
            complex_id
        )

        self.attendance_window.resize(self.size())
        self.attendance_window.move(self.pos())
        self.attendance_window.show()

    def open_finance(self):

        from financeWindow import FinanceWindow

        complex_id = self.get_current_complex_id()

        self.finance_window = FinanceWindow(
            self.phone_number,
            complex_id
        )

        self.finance_window.resize(self.size())
        self.finance_window.move(self.pos())
        self.finance_window.show()

    def open_employees(self):

        from employeesWindow import EmployeesWindow

        complex_id = self.get_current_complex_id()

        self.employees_window = EmployeesWindow(
            self.phone_number,
            complex_id
        )

        self.employees_window.resize(self.size())
        self.employees_window.move(self.pos())
        self.employees_window.show()

    def open_events(self):

        from eventsWindow import EventsWindow
        self.events_window = EventsWindow(self)
        self.events_window.resize(self.size())
        self.events_window.move(self.pos())
        self.events_window.show()
        self.events_window.raise_()

    def open_reports(self):

        from reportsWindow import ReportsWindow
        self.reports_window = ReportsWindow(self, self.phone_number)
        self.reports_window.resize(self.size())
        self.reports_window.move(self.pos())
        self.reports_window.show()
        self.reports_window.raise_()

    def open_settings(self):

        from settingsWindow import SettingsWindow
        self.settings_window = SettingsWindow(self)
        self.settings_window.resize(self.size())
        self.settings_window.move(self.pos())
        self.settings_window.show()
        self.settings_window.raise_()

    def open_messages(self):

        from messagesWindow import MessagesWindow
        self.messages_window = MessagesWindow(self)
        self.messages_window.resize(self.size())
        self.messages_window.move(self.pos())
        self.messages_window.show()
        self.messages_window.raise_()

    def open_cartable(self):

        from cartableWindow import CartableWindow
        self.cartable_window = CartableWindow(self)
        self.cartable_window.resize(self.size())
        self.cartable_window.move(self.pos())
        self.cartable_window.show()
        self.cartable_window.raise_()

    def Open_groups(self):

        from groupsWindow import GroupsWindow

        self.groups_window = GroupsWindow(self, self.phone_number)
        self.groups_window.resize(self.size())
        self.groups_window.move(self.pos())
        self.groups_window.show()