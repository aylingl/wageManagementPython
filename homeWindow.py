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

from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPainterPath

from database import Database
from theme import theme_manager
from signals import signals
from i18n import tr, set_language, get_language

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

        self.current_group = "—"
        self.current_role_key = "user_role"

        self.groups = []

        self.group_menu = None

        self.translatable = []

        self.load_user_information()

        self.setWindowTitle(tr("home_title"))
        self.resize(900, 620)
        self.setMinimumSize(500, 450)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)

    # =====================================================
    # THEME
    # =====================================================

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    # =====================================================
    # LANGUAGE
    # =====================================================

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("home_title"))
        self.retranslate_ui()

    def retranslate_ui(self):
        for widget, key in self.translatable:
            try:
                widget.setText(tr(key))
            except Exception as e:
                print("RETRANSLATE ERROR:", e)

        # آپدیت دکمه‌های نوار پایین
        if hasattr(self, "settings_btn"):
            self.settings_btn.setText(f"⚙   {tr('nav_settings')}")
            self.group_btn.setText(f"🏢   {tr('nav_group')}")
            self.home_btn.setText(f"⌂   {tr('nav_home')}")
            self.message_btn.setText(f"✉   {tr('nav_message')}")

        # آپدیت پیام خوش‌آمد (چون وابسته به username)
        if hasattr(self, "welcome_label"):
            self.welcome_label.setText(f"{tr('welcome')} {self.username} 👋")

        # گروه و نقش
        self.update_group_text()

        # سرویس‌ها
        self.update_services()

    # =====================================================
    # LOAD USER
    # =====================================================

    def load_user_information(self):

        try:
            if self.email:
                user = self.db.fetch_one(
                    """
                    SELECT userId, name, imageBase64
                    FROM users
                    WHERE email = %s
                    LIMIT 1
                    """,
                    (self.email,)
                )
            else:
                user = self.db.fetch_one(
                    """
                    SELECT userId, name, imageBase64
                    FROM users
                    WHERE phoneNumber = %s
                    LIMIT 1
                    """,
                    (self.phone_number,)
                )

            if not user:
                return

            self.user_id = user["userId"]

            theme_manager.load_for_user(self.user_id)
            self.load_user_language()

            if user.get("name"):
                self.username = user["name"]

            if user.get("imageBase64"):
                self.avatar = user["imageBase64"]

            self.groups = self.load_groups_from_database()

            if self.groups:
                first_group = self.groups[0]
                self.current_group = first_group["name"] or "—"
                rv = first_group.get("role", "employee")
                self.current_role_key = self.get_role_key(rv)

        except Exception as e:
            print("Error loading home information:", e)

    def load_user_language(self):
        if not self.user_id:
            return
        try:
            row = self.db.fetch_one(
                "SELECT language FROM user_settings WHERE userId = %s LIMIT 1",
                (self.user_id,)
            )
            if row and row.get("language"):
                set_language(row["language"])
        except Exception as e:
            print("LOAD LANGUAGE ERROR:", e)

    # =====================================================
    # GROUPS
    # =====================================================

    def load_groups_from_database(self):
        if not self.user_id:
            return []
        try:
            groups = self.db.fetch_all(
                """
                SELECT c.complexId, c.name, c.address, c.ownerId, cm.role
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
            return groups or []
        except Exception as error:
            print("LOAD HOME GROUPS ERROR:", error)
            return []

    def get_current_complex_id(self):
        for group in self.groups:
            if (group.get("name") or "—") == self.current_group:
                return group.get("complexId")
        if self.groups:
            return self.groups[0].get("complexId")
        return None

    def close_group_menu(self):
        if self.group_menu is not None:
            try:
                self.group_menu.close()
                self.group_menu.deleteLater()
            except Exception as error:
                print("GROUP MENU CLOSE ERROR:", error)
            self.group_menu = None

    def get_role_key(self, role_value):
        if role_value == "owner":
            return "owner_role"
        elif role_value == "employee":
            return "employee_role"
        elif role_value == "both":
            return "both_role"
        else:
            return "user_role"

    def refresh_groups_from_database(self):
        try:
            if not self.user_id:
                return

            popup_was_visible = False
            if self.group_menu is not None:
                popup_was_visible = self.group_menu.isVisible()
                self.close_group_menu()

            self.groups = self.load_groups_from_database()

            if self.groups:
                current_exists = any(
                    (group["name"] or "—") == self.current_group
                    for group in self.groups
                )
                if not current_exists:
                    first_group = self.groups[0]
                    self.current_group = first_group["name"] or "—"
                    rv = first_group.get("role", "employee")
                    self.current_role_key = self.get_role_key(rv)
            else:
                self.current_group = "—"
                self.current_role_key = "user_role"

            self.update_group_text()
            self.update_services()

            if popup_was_visible:
                self.show_group_menu()

        except Exception as error:
            print("HOME GROUP REFRESH ERROR:", error)

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        self.translatable = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(14)

        # TOP
        top_layout = QHBoxLayout()
        top_layout.setSpacing(14)

        # PROFILE CARD
        self.profile_card = QFrame()
        self.profile_card.setObjectName("profileCard")
        self.profile_card.setAttribute(Qt.WA_StyledBackground, True)

        profile_layout = QHBoxLayout(self.profile_card)
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

        profile_title = QLabel(tr("my_profile"))
        profile_title.setObjectName("profileTitle")
        self.translatable.append((profile_title, "my_profile"))

        username_label = QLabel(self.username)
        username_label.setObjectName("usernameLabel")

        profile_text.addWidget(profile_title)
        profile_text.addWidget(username_label)

        profile_edit = QPushButton("✎")
        profile_edit.setObjectName("profileEdit")
        profile_edit.setFixedSize(34, 34)
        profile_edit.setCursor(Qt.PointingHandCursor)
        profile_edit.setAttribute(Qt.WA_StyledBackground, True)
        profile_edit.clicked.connect(self.open_profile)

        profile_layout.addWidget(avatar)
        profile_layout.addLayout(profile_text)
        profile_layout.addStretch()
        profile_layout.addWidget(profile_edit)

        # GROUP CARD
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

        self.group_subtitle = QLabel(tr("active_group"))
        self.group_subtitle.setObjectName("groupSubtitle")
        self.group_subtitle.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.translatable.append((self.group_subtitle, "active_group"))

        group_text.addWidget(self.group_name_label)
        group_text.addWidget(self.group_subtitle)

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

        top_layout.addWidget(self.profile_card, 1)
        top_layout.addWidget(self.group_card, 1)

        main_layout.addLayout(top_layout)

        # WELCOME
        welcome_layout = QVBoxLayout()
        welcome_layout.setContentsMargins(4, 5, 4, 4)
        welcome_layout.setSpacing(2)

        self.welcome_label = QLabel(f"{tr('welcome')} {self.username} 👋")
        self.welcome_label.setObjectName("welcome")
        self.welcome_label.setFixedHeight(28)

        self.welcome_sub = QLabel(tr("welcome_sub"))
        self.welcome_sub.setObjectName("welcomeSub")
        self.welcome_sub.setFixedHeight(20)
        self.translatable.append((self.welcome_sub, "welcome_sub"))

        welcome_layout.addWidget(self.welcome_label)
        welcome_layout.addWidget(self.welcome_sub)

        main_layout.addLayout(welcome_layout)

        # SERVICES BOX
        self.services_box = QFrame()
        self.services_box.setObjectName("servicesBox")
        self.services_box.setAttribute(Qt.WA_StyledBackground, True)
        self.services_box.setMinimumHeight(200)

        services_layout = QVBoxLayout(self.services_box)
        services_layout.setContentsMargins(18, 14, 18, 14)
        services_layout.setSpacing(6)

        self.services_title = QLabel(tr("quick_access"))
        self.services_title.setObjectName("servicesTitle")
        self.translatable.append((self.services_title, "quick_access"))

        services_layout.addWidget(self.services_title)
        services_layout.addSpacing(4)

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

        main_layout.addWidget(self.services_box, 1)

        # BOTTOM NAV
        nav_box = QFrame()
        nav_box.setObjectName("navBox")
        nav_box.setAttribute(Qt.WA_StyledBackground, True)
        nav_box.setFixedHeight(76)

        nav_layout = QHBoxLayout(nav_box)
        nav_layout.setContentsMargins(12, 8, 12, 8)
        nav_layout.setSpacing(8)

        self.settings_btn = self.create_nav_button("⚙", tr("nav_settings"), self.open_settings)
        self.group_btn = self.create_nav_button("🏢", tr("nav_group"), self.Open_groups)
        self.home_btn = self.create_nav_button("⌂", tr("nav_home"), lambda: None)
        self.message_btn = self.create_nav_button("✉", tr("nav_message"), self.open_messages)

        nav_layout.addWidget(self.settings_btn)
        nav_layout.addWidget(self.group_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.message_btn)

        main_layout.addWidget(nav_box)

        # INITIAL
        self.update_group_text()
        self.update_services()

        self.apply_stylesheet()

    # =====================================================
    # APPLY STYLESHEET
    # =====================================================

    def apply_stylesheet(self):

        c = theme_manager.colors()

        self.setStyleSheet(f"""

            QWidget {{
                background-color: {c['bg_main']};
                font-family: "Vazirmatn";
                color: {c['text_main']};
            }}

            QFrame#profileCard {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 28px;
            }}

            QLabel#profileTitle {{
                background: transparent;
                border: none;
                color: {c['text_main']};
                font-size: 13px;
                font-weight: 600;
            }}

            QLabel#usernameLabel {{
                background: transparent;
                border: none;
                color: {c['text_dim']};
                font-size: 11px;
            }}

            QPushButton#profileEdit {{
                background-color: {c['accent_light']};
                color: {c['accent']};
                border: none;
                border-radius: 17px;
                font-size: 18px;
            }}

            QPushButton#profileEdit:hover {{
                background-color: {c['bg_hover']};
            }}

            QFrame#groupCard {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 28px;
            }}

            QFrame#groupCard:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid {c['accent']};
                border-radius: 28px;
            }}

            QLabel#groupIcon {{
                background-color: transparent;
                border: none;
                color: {c['accent']};
                font-size: 29px;
                font-weight: 700;
            }}

            QLabel#groupName {{
                background-color: transparent;
                border: none;
                color: {c['text_main']};
                font-size: 13px;
                font-weight: 600;
            }}

            QLabel#groupSubtitle {{
                background-color: transparent;
                border: none;
                color: {c['text_dim']};
                font-size: 10px;
            }}

            QLabel#groupArrow {{
                background-color: transparent;
                border: none;
                color: {c['accent']};
                font-size: 24px;
            }}

            QLabel#welcome {{
                background-color: transparent;
                border: none;
                color: {c['text_main']};
                font-size: 19px;
                font-weight: 700;
            }}

            QLabel#welcomeSub {{
                background-color: transparent;
                border: none;
                color: {c['text_dim']};
                font-size: 11px;
            }}

            QFrame#servicesBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 28px;
            }}

            QLabel#servicesTitle {{
                background-color: transparent;
                border: none;
                color: {c['text_main']};
                font-size: 14px;
                font-weight: 700;
            }}

            QScrollArea#servicesScroll {{
                background-color: transparent;
                border: none;
            }}

            QScrollArea#servicesScroll > QWidget {{
                background-color: transparent;
                border: none;
            }}

            QWidget#scrollContent {{
                background-color: transparent;
                border: none;
            }}

            QScrollBar:vertical {{
                width: 10px;
                background: {c['bg_input']};
                border: none;
                border-radius: 5px;
                margin: 5px 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {c['accent']};
                border: none;
                border-radius: 5px;
                min-height: 45px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {c['accent_hover']};
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                background: transparent;
                border: none;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
                border: none;
            }}

            QFrame#serviceCard {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 20px;
            }}

            QFrame#serviceCard:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid {c['accent']};
                border-radius: 20px;
            }}

            QLabel#serviceIcon {{
                background-color: {c['accent_light']};
                border: none;
                border-radius: 19px;
                color: {c['accent']};
                font-size: 18px;
            }}

            QLabel#serviceTitle {{
                background-color: transparent;
                border: none;
                color: {c['text_main']};
                font-size: 12px;
                font-weight: 600;
            }}

            QLabel#serviceArrow {{
                background-color: transparent;
                border: none;
                color: {c['text_dim']};
                font-size: 22px;
            }}

            QFrame#navBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 24px;
            }}

            QPushButton#navButton {{
                background-color: transparent;
                color: {c['text_dim']};
                border: none;
                border-radius: 16px;
                padding: 8px;
                font-size: 16px;
                font-weight: 500;
                min-height: 48px;
            }}

            QPushButton#navButton:hover {{
                background-color: {c['bg_hover']};
                color: {c['accent']};
            }}

            QFrame#groupPopup {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 22px;
            }}

            QFrame#groupOption {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 15px;
            }}

            QFrame#groupOption:hover {{
                background-color: {c['bg_hover']};
                border: 1px solid {c['accent']};
                border-radius: 15px;
            }}

            QLabel#groupOptionLabel {{
                background-color: transparent;
                border: none;
                color: {c['text_main']};
                font-size: 13px;
            }}

            QScrollArea#groupPopupScroll {{
                background: transparent;
                border: none;
            }}

            QScrollArea#groupPopupScroll > QWidget {{
                background: transparent;
                border: none;
            }}

            QWidget#groupPopupContent {{
                background: transparent;
                border: none;
            }}
        """)

    # =====================================================
    # GROUP TEXT
    # =====================================================

    def update_group_text(self):
        self.group_name_label.setText(
            f"{self.current_group}   •   {tr(self.current_role_key)}"
        )

    # =====================================================
    # GROUP MENU
    # =====================================================

    def show_group_menu(self):

        try:
            if self.group_menu is not None:
                self.close_group_menu()

            if self.user_id:
                self.groups = self.load_groups_from_database()

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

                    group_name = group["name"] or "—"
                    role_value = group.get("role", "employee")
                    role_key = self.get_role_key(role_value)
                    role_text = tr(role_key)

                    group_label = QLabel(f"{group_name}   •   {role_text}")
                    group_label.setObjectName("groupOptionLabel")
                    group_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                    group_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    group_layout.addWidget(group_label)

                    def select_group(event, selected_group=group):
                        self.current_group = selected_group["name"] or "—"
                        rv = selected_group.get("role", "employee")
                        self.current_role_key = self.get_role_key(rv)
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

                empty_label = QLabel(tr("no_group"))
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

        except Exception as error:
            print("SHOW GROUP MENU ERROR:", error)

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
            self.create_service_card("🕒", tr("attendance"), self.open_attendance)
        )

        self.scroll_layout.addWidget(
            self.create_service_card("💰", tr("finance"), self.open_finance)
        )

        if self.current_role_key in ("owner_role", "both_role"):
            self.scroll_layout.addWidget(
                self.create_service_card("👥", tr("employees"), self.open_employees)
            )
            self.scroll_layout.addWidget(
                self.create_service_card("📥", tr("cartable"), self.open_cartable)
            )

        self.scroll_layout.addWidget(
            self.create_service_card("📅", tr("events"), self.open_events)
        )

        self.scroll_layout.addWidget(
            self.create_service_card("📊", tr("reports"), self.open_reports)
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
        try:
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
        except Exception as e:
            print("OPEN PROFILE ERROR:", e)

    def open_attendance(self):
        from attendanceWindow import AttendanceWindow
        complex_id = self.get_current_complex_id()
        self.attendance_window = AttendanceWindow(self.phone_number, complex_id)
        self.attendance_window.resize(self.size())
        self.attendance_window.move(self.pos())
        self.attendance_window.show()

    def open_finance(self):
        from financeWindow import FinanceWindow
        complex_id = self.get_current_complex_id()
        self.finance_window = FinanceWindow(self.phone_number, complex_id)
        self.finance_window.resize(self.size())
        self.finance_window.move(self.pos())
        self.finance_window.show()

    def open_employees(self):
        from employeesWindow import EmployeesWindow
        complex_id = self.get_current_complex_id()
        self.employees_window = EmployeesWindow(self.phone_number, complex_id)
        self.employees_window.resize(self.size())
        self.employees_window.move(self.pos())
        self.employees_window.show()

    def open_events(self):
        from eventsWindow import EventsWindow
        complex_id = self.get_current_complex_id()
        self.events_window = EventsWindow(self,phone_number = self.phone_number,
        complex_id = complex_id)
        self.events_window.resize(self.size())
        self.events_window.move(self.pos())
        self.events_window.show()
        self.events_window.raise_()

    def open_reports(self):
        from reportsWindow import ReportsWindow
        complex_id = self.get_current_complex_id()
        self.reports_window = ReportsWindow(self, phone_number = self.phone_number, complex_id = complex_id)
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
        complex_id = self.get_current_complex_id()
        self.cartable_window = CartableWindow(self, phone_number = self.phone_number, complex_id = complex_id)
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