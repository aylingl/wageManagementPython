from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QLineEdit, QDialog,
    QComboBox, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, Property, QPoint, QSize
)
from PySide6.QtGui import QPainter, QColor, QBrush

import hashlib
import re

from database import Database
from theme import theme_manager
from signals import signals
from i18n import tr, set_language, get_language

# =====================================================
# HASH / VALIDATION
# =====================================================

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# =====================================================
# ROUND SCROLL BAR
# =====================================================

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

# =====================================================
# TOGGLE SWITCH
# =====================================================

class ToggleSwitch(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(56, 30)
        self.setCursor(Qt.PointingHandCursor)

        self._checked = False
        self._position = 0.0
        self._circle_color = QColor("#FFFFFF")
        self._bg_off = QColor("#DCE5EF")
        self._bg_on = QColor("#4589E8")

        self._animation = QPropertyAnimation(self, b"position")
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)

        self._callback = None

    def get_position(self):
        return self._position

    def set_position(self, value):
        self._position = value
        self.update()

    position = Property(float, get_position, set_position)

    def isChecked(self):
        return self._checked

    def setChecked(self, value, animate=True):
        self._checked = bool(value)
        target = 1.0 if self._checked else 0.0
        self._animation.stop()
        if animate:
            self._animation.setStartValue(self._position)
            self._animation.setEndValue(target)
            self._animation.start()
        else:
            self._position = target
            self.update()

    def set_on_toggle(self, callback):
        self._callback = callback

    def set_colors(self, bg_off=None, bg_on=None, circle=None):
        if bg_off:
            self._bg_off = QColor(bg_off)
        if bg_on:
            self._bg_on = QColor(bg_on)
        if circle:
            self._circle_color = QColor(circle)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        radius = h / 2
        margin = 3

        bg_color = QColor(
            int(self._bg_off.red() + (self._bg_on.red() - self._bg_off.red()) * self._position),
            int(self._bg_off.green() + (self._bg_on.green() - self._bg_off.green()) * self._position),
            int(self._bg_off.blue() + (self._bg_on.blue() - self._bg_off.blue()) * self._position),
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, w, h, radius, radius)

        circle_size = h - margin * 2
        x_off = margin + (w - circle_size - margin * 2) * self._position
        y_off = margin

        painter.setBrush(QBrush(self._circle_color))
        painter.drawEllipse(int(x_off), int(y_off), circle_size, circle_size)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._checked = not self._checked
            target = 1.0 if self._checked else 0.0
            self._animation.stop()
            self._animation.setStartValue(self._position)
            self._animation.setEndValue(target)
            self._animation.start()
            if self._callback:
                self._callback(self._checked)
            event.accept()

# =====================================================
# ROUNDED COMBO BOX
# =====================================================

class RoundedComboBox(QComboBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._popup = None
        self._list = None

    def showPopup(self):
        if self._popup is not None:
            self.hidePopup()
            return

        self._popup = QFrame(None)
        self._popup.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self._popup.setAttribute(Qt.WA_TranslucentBackground, True)

        outer = QVBoxLayout(self._popup)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("comboCard")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)

        outer.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self._list = QListWidget()
        self._list.setFrameShape(QFrame.NoFrame)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._list.setFocusPolicy(Qt.NoFocus)

        c = theme_manager.colors()

        self._list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
                padding: 6px;
                color: {c['text_main']};
                font-family: "Vazirmatn";
                font-size: 13px;
            }}
            QListWidget::item {{
                background: transparent;
                color: {c['text_main']};
                border-radius: 10px;
                padding: 10px 16px;
                margin: 2px 4px;
                min-height: 20px;
            }}
            QListWidget::item:hover {{
                background-color: {c['bg_hover']};
                color: {c['accent']};
            }}
            QListWidget::item:selected {{
                background-color: {c['accent']};
                color: white;
            }}
            QScrollBar:vertical {{
                width: 8px;
                background: transparent;
                border: none;
                margin: 6px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {c['accent']};
                border-radius: 4px;
                min-height: 24px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

        for i in range(self.count()):
            item = QListWidgetItem(self.itemText(i))
            item.setData(Qt.UserRole, i)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setSizeHint(QSize(0, 42))
            self._list.addItem(item)
            if i == self.currentIndex():
                self._list.setCurrentItem(item)

        self._list.itemClicked.connect(self._on_item_clicked)
        card_layout.addWidget(self._list)

        self._popup.setStyleSheet(f"""
            QFrame#comboCard {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 18px;
            }}
        """)

        count = max(self.count(), 1)
        item_h = 42
        list_padding = 12
        margins = 20
        content_h = count * item_h + list_padding + margins
        popup_w = max(self.width(), 160)
        popup_h = min(content_h, 220)

        self._popup.setFixedWidth(popup_w)
        self._popup.setFixedHeight(popup_h)

        pos = self.mapToGlobal(QPoint(0, self.height() + 4))
        self._popup.move(pos)
        self._popup.show()

    def hidePopup(self):
        if self._popup is not None:
            self._popup.close()
            self._popup.deleteLater()
            self._popup = None
            self._list = None

    def _on_item_clicked(self, item):
        idx = item.data(Qt.UserRole)
        if idx is not None:
            self.setCurrentIndex(idx)
        self.hidePopup()

# =====================================================
# NICE MESSAGE BOX
# =====================================================

class NiceMessageDialog(QDialog):

    def __init__(self, parent, title, text, kind="info", yes_no=False):
        super().__init__(parent)

        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedSize(400, 280)

        self.result_value = False
        c = theme_manager.colors()

        if kind == "success":
            icon_char, color, bg = "✓", "#16A34A", "#DCFCE7"
        elif kind == "error":
            icon_char, color, bg = "✕", "#D93025", "#FEE2E2"
        elif kind == "warning":
            icon_char, color, bg = "!", "#F59E0B", "#FEF3C7"
        elif kind == "question":
            icon_char, color, bg = "?", "#1961C7", "#DBEAFE"
        else:
            icon_char, color, bg = "i", "#1961C7", "#DBEAFE"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("niceMsgCard")
        card.setStyleSheet(f"""
            QFrame#niceMsgCard {{
                background-color: {c['bg_card']};
                border-radius: 22px;
                border: 1px solid {c['border']};
            }}
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
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_main']};
                font-size: 16px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_dim']};
                font-size: 12px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(text_label)
        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        if yes_no:
            no_btn = QPushButton(tr("no"))
            no_btn.setFixedHeight(42)
            no_btn.setMinimumWidth(110)
            no_btn.setCursor(Qt.PointingHandCursor)
            no_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['bg_input']};
                    color: {c['text_dim']};
                    border: 1px solid {c['border']};
                    border-radius: 12px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 0 20px;
                }}
                QPushButton:hover {{ background-color: {c['bg_hover']}; }}
            """)
            no_btn.clicked.connect(self.reject)
            btn_row.addWidget(no_btn)

        yes_btn = QPushButton(tr("yes") if yes_no else tr("ok"))
        yes_btn.setFixedHeight(42)
        yes_btn.setMinimumWidth(120)
        yes_btn.setCursor(Qt.PointingHandCursor)
        yes_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 24px;
            }}
        """)

        def on_yes():
            self.result_value = True
            self.accept()

        yes_btn.clicked.connect(on_yes)
        btn_row.addWidget(yes_btn)
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

    @staticmethod
    def ask(parent, title, text):
        dialog = NiceMessageDialog(parent, title, text, "question", yes_no=True)
        dialog.exec()
        return dialog.result_value

# =====================================================
# SETTINGS WINDOW
# =====================================================

class SettingsWindow(QWidget):

    def __init__(self, parent_window=None):
        super().__init__()

        self.parent_window = parent_window
        self.db = Database()

        self.user_id = None
        if parent_window is not None:
            self.user_id = getattr(parent_window, "user_id", None)

        self.load_user_language()

        self.translatable = []
        self.email_desc_label = None

        self.setWindowTitle(tr("settings_title"))
        self.setMinimumSize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()
        self.retranslate_ui()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed_signal)

    # =====================================================
    # LOAD / SAVE LANGUAGE
    # =====================================================

    def load_user_language(self):
        if not self.user_id:
            set_language("fa")
            return
        try:
            row = self.db.fetch_one(
                "SELECT language FROM user_settings WHERE userId = %s LIMIT 1",
                (self.user_id,)
            )
            if row and row.get("language"):
                set_language(row["language"])
            else:
                set_language("fa")
        except Exception as e:
            print("LOAD LANGUAGE ERROR:", e)
            set_language("fa")

    def save_user_language(self, lang):
        if not self.user_id:
            return
        try:
            existing = self.db.fetch_one(
                "SELECT settingId FROM user_settings WHERE userId = %s LIMIT 1",
                (self.user_id,)
            )
            if existing:
                self.db.execute(
                    "UPDATE user_settings SET language = %s WHERE userId = %s",
                    (lang, self.user_id)
                )
            else:
                self.db.execute(
                    "INSERT INTO user_settings (userId, language) VALUES (%s, %s)",
                    (self.user_id, lang)
                )
        except Exception as e:
            print("SAVE LANGUAGE ERROR:", e)

    # =====================================================
    # THEME / LANGUAGE
    # =====================================================

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

        if hasattr(self, "dark_mode_switch"):
            is_dark = (theme_name == "dark")
            if self.dark_mode_switch.isChecked() != is_dark:
                self.dark_mode_switch.setChecked(is_dark)

    def on_language_changed_signal(self, lang):
        set_language(lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        # آپدیت عنوان پنجره
        self.setWindowTitle(tr("settings_title"))

        # آپدیت همه widgetهای ثبت‌شده
        for widget, key in self.translatable:
            try:
                widget.setText(tr(key))
            except Exception as e:
                print("RETRANSLATE ERROR:", e)

        # آپدیت متن ایمیل
        if self.email_desc_label is not None:
            current_email = self.get_user_email()
            if current_email:
                self.email_desc_label.setText(
                    tr("email_active") + " — " + current_email
                )
                self.email_desc_label.setStyleSheet("""
                    color: #16A34A;
                    font-size: 11px;
                    background: transparent;
                """)
            else:
                self.email_desc_label.setText(tr("email_not_set"))
                self.email_desc_label.setStyleSheet("""
                    color: #B87900;
                    font-size: 11px;
                    background: transparent;
                """)

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        # HEADER
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel(tr("settings_title"))
        title.setObjectName("title")
        # ← این خط مهمه: اضافه کردن به translatable
        self.translatable.append((title, "settings_title"))

        subtitle = QLabel(tr("settings_subtitle"))
        subtitle.setObjectName("subtitle")
        # ← این خط مهمه
        self.translatable.append((subtitle, "settings_subtitle"))

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # SCROLL
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        round_bar = RoundScrollBar(Qt.Vertical)
        scroll.setVerticalScrollBar(round_bar)

        content = QWidget()
        content.setObjectName("scrollContent")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 12, 0)
        content_layout.setSpacing(14)

        scroll.setWidget(content)

        # ACCOUNT
        account_box = QFrame()
        account_box.setObjectName("settingsBox")

        account_layout = QVBoxLayout(account_box)
        account_layout.setContentsMargins(16, 16, 16, 16)
        account_layout.setSpacing(10)

        account_title = QLabel(tr("account"))
        account_title.setObjectName("sectionTitle")
        self.translatable.append((account_title, "account"))
        account_layout.addWidget(account_title)

        # پروفایل
        profile_item = self.make_setting_item(
            "👤",
            tr("profile_info"),
            tr("profile_desc"),
            self.open_profile_edit
        )
        self.translatable.append((profile_item["title"], "profile_info"))
        self.translatable.append((profile_item["desc"], "profile_desc"))
        account_layout.addWidget(profile_item["btn"])

        # ایمیل
        email_item = self.make_setting_item(
            "📧",
            tr("login_email"),
            "",
            self.open_email_dialog
        )
        self.translatable.append((email_item["title"], "login_email"))
        self.email_desc_label = email_item["desc"]
        account_layout.addWidget(email_item["btn"])

        # امنیت
        security_item = self.make_setting_item(
            "🔒",
            tr("account_security"),
            tr("security_desc"),
            self.open_change_password_dialog
        )
        self.translatable.append((security_item["title"], "account_security"))
        self.translatable.append((security_item["desc"], "security_desc"))
        account_layout.addWidget(security_item["btn"])

        content_layout.addWidget(account_box)

        # APPEARANCE
        appearance_box = QFrame()
        appearance_box.setObjectName("settingsBox")

        appearance_layout = QVBoxLayout(appearance_box)
        appearance_layout.setContentsMargins(16, 16, 16, 16)
        appearance_layout.setSpacing(10)

        appearance_title = QLabel(tr("appearance"))
        appearance_title.setObjectName("sectionTitle")
        self.translatable.append((appearance_title, "appearance"))
        appearance_layout.addWidget(appearance_title)

        # دارک مود
        theme_row = QFrame()
        theme_row.setObjectName("settingRow")
        theme_layout = QHBoxLayout(theme_row)
        theme_layout.setContentsMargins(14, 10, 14, 10)
        theme_layout.setSpacing(12)

        theme_icon = QLabel("🌙")
        theme_icon.setObjectName("settingIcon")
        theme_icon.setFixedSize(42, 42)
        theme_icon.setAlignment(Qt.AlignCenter)

        theme_text_layout = QVBoxLayout()
        theme_text_layout.setSpacing(3)

        theme_title = QLabel(tr("dark_mode"))
        theme_title.setObjectName("itemTitle")
        self.translatable.append((theme_title, "dark_mode"))

        theme_desc = QLabel(tr("dark_mode_desc"))
        theme_desc.setObjectName("itemDescription")
        self.translatable.append((theme_desc, "dark_mode_desc"))

        theme_text_layout.addWidget(theme_title)
        theme_text_layout.addWidget(theme_desc)

        self.dark_mode_switch = ToggleSwitch()
        self.dark_mode_switch.setChecked(theme_manager.is_dark(), animate=False)
        self.dark_mode_switch.set_on_toggle(self.on_dark_mode_toggled)

        theme_layout.addWidget(theme_icon)
        theme_layout.addLayout(theme_text_layout, 1)
        theme_layout.addWidget(self.dark_mode_switch)

        appearance_layout.addWidget(theme_row)

        # زبان
        language_row = QFrame()
        language_row.setObjectName("settingRow")
        language_layout = QHBoxLayout(language_row)
        language_layout.setContentsMargins(14, 10, 14, 10)
        language_layout.setSpacing(12)

        language_icon = QLabel("文")
        language_icon.setObjectName("settingIcon")
        language_icon.setFixedSize(42, 42)
        language_icon.setAlignment(Qt.AlignCenter)

        language_text_layout = QVBoxLayout()
        language_text_layout.setSpacing(3)

        language_title = QLabel(tr("language"))
        language_title.setObjectName("itemTitle")
        self.translatable.append((language_title, "language"))

        language_desc = QLabel(tr("language_desc"))
        language_desc.setObjectName("itemDescription")
        self.translatable.append((language_desc, "language_desc"))

        language_text_layout.addWidget(language_title)
        language_text_layout.addWidget(language_desc)

        self.language_combo = RoundedComboBox()
        self.language_combo.setObjectName("settingCombo")
        self.language_combo.setFixedHeight(42)
        self.language_combo.setMinimumWidth(130)
        self.language_combo.setCursor(Qt.PointingHandCursor)

        self.language_combo.addItem("فارسی", "fa")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("العربية", "ar")

        current_lang = get_language()
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_lang:
                self.language_combo.setCurrentIndex(i)
                break

        self.language_combo.currentIndexChanged.connect(self.on_language_changed)

        language_layout.addWidget(language_icon)
        language_layout.addLayout(language_text_layout, 1)
        language_layout.addWidget(self.language_combo)

        appearance_layout.addWidget(language_row)
        content_layout.addWidget(appearance_box)

        # LOGOUT
        self.logout_button = QPushButton(tr("logout"))
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.setCursor(Qt.PointingHandCursor)
        self.logout_button.clicked.connect(self.logout)
        self.translatable.append((self.logout_button, "logout"))

        content_layout.addWidget(self.logout_button)
        content_layout.addStretch()

        main_layout.addWidget(scroll)

        self.apply_stylesheet()

    # =====================================================
    # MAKE SETTING ITEM
    # =====================================================

    def make_setting_item(self, icon, title, desc, callback):

        btn = QPushButton()
        btn.setObjectName("settingItem")
        btn.setMinimumHeight(70)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)

        layout = QHBoxLayout(btn)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setObjectName("settingIcon")
        icon_label.setFixedSize(42, 42)
        icon_label.setAlignment(Qt.AlignCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        title_label = QLabel(title)
        title_label.setObjectName("itemTitle")

        desc_label = QLabel(desc)
        desc_label.setObjectName("itemDescription")

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)

        arrow = QLabel("‹")
        arrow.setObjectName("itemArrow")
        arrow.setAlignment(Qt.AlignCenter)
        arrow.setFixedWidth(25)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)
        layout.addWidget(arrow)

        return {
            "btn": btn,
            "title": title_label,
            "desc": desc_label
        }

    # =====================================================
    # APPLY STYLESHEET
    # =====================================================

    def apply_stylesheet(self):

        c = theme_manager.colors()

        self.setStyleSheet(f"""

            QWidget {{
                background-color: {c['bg_main']};
                font-family: Vazirmatn;
                color: {c['text_main']};
            }}

            QLabel#title {{
                color: {c['text_main']};
                font-size: 24px;
                font-weight: 700;
                background-color: transparent;
                border: none;
            }}

            QLabel#subtitle {{
                color: {c['text_dim']};
                font-size: 13px;
                background-color: transparent;
                border: none;
            }}

            QPushButton#backButton {{
                background-color: {c['bg_card']};
                color: {c['accent']};
                border: 1px solid {c['border']};
                border-radius: 14px;
                font-size: 20px;
                font-weight: 600;
            }}

            QPushButton#backButton:hover {{
                background-color: {c['accent_light']};
                border-color: {c['border_hover']};
            }}

            QScrollArea {{
                background-color: transparent;
                border: none;
            }}

            QScrollArea::viewport {{
                background-color: transparent;
                border: none;
            }}

            QWidget#scrollContent {{
                background-color: transparent;
            }}

            QFrame#settingsBox {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 20px;
            }}

            QLabel#sectionTitle {{
                color: {c['text_main']};
                background-color: transparent;
                border: none;
                font-size: 16px;
                font-weight: 700;
                padding-bottom: 4px;
            }}

            QPushButton#settingItem {{
                background-color: {c['bg_card']};
                color: {c['text_main']};
                border: 1px solid {c['border']};
                border-radius: 14px;
                text-align: right;
            }}

            QPushButton#settingItem:hover {{
                background-color: {c['bg_hover']};
                border-color: {c['border_hover']};
            }}

            QFrame#settingRow {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: 14px;
            }}

            QFrame#settingRow:hover {{
                border-color: {c['border_hover']};
            }}

            QLabel#settingIcon {{
                background-color: {c['accent_light']};
                color: {c['accent']};
                border: none;
                border-radius: 12px;
                font-size: 17px;
            }}

            QLabel#itemTitle {{
                color: {c['text_main']};
                background-color: transparent;
                border: none;
                font-size: 13px;
                font-weight: 700;
            }}

            QLabel#itemDescription {{
                color: {c['text_dim']};
                background-color: transparent;
                border: none;
                font-size: 11px;
            }}

            QLabel#itemArrow {{
                color: {c['text_dim']};
                background-color: transparent;
                border: none;
                font-size: 23px;
            }}

            QPushButton#logoutButton {{
                background-color: {c['bg_card']};
                color: {c['danger']};
                border: 1px solid {c['border']};
                border-radius: 14px;
                padding: 13px;
                font-size: 13px;
                font-weight: 600;
            }}

            QPushButton#logoutButton:hover {{
                background-color: {c['danger_bg']};
                border-color: {c['danger']};
            }}

            QComboBox#settingCombo {{
                background-color: {c['bg_input']};
                border: 1px solid {c['border']};
                border-radius: 21px;
                padding: 0 18px;
                color: {c['text_main']};
                font-size: 12px;
                font-weight: 600;
            }}

            QComboBox#settingCombo:hover {{
                border-color: {c['accent']};
                background-color: {c['bg_hover']};
            }}

            QComboBox#settingCombo:focus {{
                border: 2px solid {c['accent']};
            }}

            QComboBox#settingCombo::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border: none;
                background: transparent;
            }}

            QComboBox#settingCombo::down-arrow {{
                image: none;
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {c['accent']};
                margin-right: 10px;
            }}
        """)

        if hasattr(self, "dark_mode_switch"):
            if theme_manager.is_dark():
                self.dark_mode_switch.set_colors(
                    bg_off="#3C4043",
                    bg_on="#4589E8",
                    circle="#E8EAED"
                )
            else:
                self.dark_mode_switch.set_colors(
                    bg_off="#DCE5EF",
                    bg_on="#4589E8",
                    circle="#FFFFFF"
                )

    # =====================================================
    # DARK MODE / LANGUAGE
    # =====================================================

    def on_dark_mode_toggled(self, is_on):
        theme_name = "dark" if is_on else "light"
        theme_manager.apply(
            theme_name,
            save_to_db=True,
            user_id=self.user_id
        )

    def on_language_changed(self, index):
        lang = self.language_combo.itemData(index)
        if not lang:
            return
        if lang == get_language():
            return
        self.save_user_language(lang)
        signals.language_changed.emit(lang)

    # =====================================================
    # HELPERS
    # =====================================================

    def get_user_email(self):
        if not self.user_id:
            return None
        row = self.db.fetch_one(
            "SELECT email FROM users WHERE userId = %s LIMIT 1",
            (self.user_id,)
        )
        if row and row.get("email"):
            return row["email"]
        return None

    def open_profile_edit(self):
        try:
            from editProfileWindow import EditProfileWindow
            phone = None
            username = ""
            avatar = ""
            if self.parent_window is not None:
                phone = getattr(self.parent_window, "phone_number", None)
                username = getattr(self.parent_window, "username", "")
                avatar = getattr(self.parent_window, "avatar", "")
            self.edit_window = EditProfileWindow(
                self,
                phone_number=phone,
                username=username,
                national_code="",
                avatar=avatar
            )
            self.edit_window.resize(self.size())
            self.edit_window.move(self.pos())
            self.edit_window.show()
            self.edit_window.raise_()
        except Exception as e:
            print("OPEN PROFILE EDIT ERROR:", e)
            NiceMessageBox.error(self, tr("error"), "editProfileWindow.py not found.")

    def open_email_dialog(self):
        if not self.user_id:
            NiceMessageBox.error(self, tr("error"), "User not found.")
            return

        user = self.db.fetch_one(
            "SELECT email, passwordHash FROM users WHERE userId = %s LIMIT 1",
            (self.user_id,)
        )
        if not user:
            return

        current_email = user.get("email") or ""
        title_text = tr("edit_email") if current_email else tr("add_email")

        dialog = QDialog(self)
        dialog.setWindowTitle(title_text)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(460)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel(title_text)
        title.setStyleSheet("color: #17324D; font-size: 17px; font-weight: 800; background: transparent;")
        layout.addWidget(title)

        email_input = QLineEdit()
        email_input.setPlaceholderText("name@example.com")
        email_input.setFixedHeight(46)
        email_input.setLayoutDirection(Qt.LeftToRight)
        email_input.setText(current_email)
        email_input.setStyleSheet("""
            QLineEdit {
                background-color: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 12px;
                padding: 0 14px;
                color: #17324D;
                font-size: 13px;
            }
            QLineEdit:focus { background: #FFFFFF; border: 2px solid #4589E8; }
        """)
        layout.addWidget(email_input)

        pw_input = QLineEdit()
        pw_input.setPlaceholderText("Password")
        pw_input.setEchoMode(QLineEdit.Password)
        pw_input.setFixedHeight(46)
        pw_input.setStyleSheet(email_input.styleSheet())
        layout.addWidget(pw_input)

        cf_input = QLineEdit()
        cf_input.setPlaceholderText("Repeat")
        cf_input.setEchoMode(QLineEdit.Password)
        cf_input.setFixedHeight(46)
        cf_input.setStyleSheet(email_input.styleSheet())
        layout.addWidget(cf_input)

        btns = QHBoxLayout()
        cancel_btn = QPushButton(tr("cancel"))
        cancel_btn.setFixedHeight(44)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F8FC; color: #526273;
                border: 1px solid #E2EAF4; border-radius: 14px;
                padding: 0 24px; font-size: 13px; font-weight: 600;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)

        save_btn = QPushButton(tr("save"))
        save_btn.setFixedHeight(44)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1961C7; color: white;
                border: none; border-radius: 14px;
                padding: 0 28px; font-size: 13px; font-weight: 700;
            }
        """)

        def on_save():
            email_value = email_input.text().strip()
            pwd = pw_input.text().strip()
            pwd_confirm = cf_input.text().strip()

            if not is_valid_email(email_value):
                NiceMessageBox.warning(dialog, tr("error"), tr("err_invalid_email"))
                return
            if len(pwd) < 6:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_pwd_min"))
                return
            if pwd != pwd_confirm:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_pwd_match"))
                return

            password_hash = hash_password(pwd)
            self.db.execute(
                "UPDATE users SET email = %s, passwordHash = %s WHERE userId = %s",
                (email_value, password_hash, self.user_id)
            )
            dialog.accept()
            NiceMessageBox.success(self, tr("saved"), tr("saved_successfully"))
            self.retranslate_ui()

        save_btn.clicked.connect(on_save)
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)
        dialog.exec()

    def open_change_password_dialog(self):
        if not self.user_id:
            return
        user = self.db.fetch_one(
            "SELECT passwordHash FROM users WHERE userId = %s LIMIT 1",
            (self.user_id,)
        )
        if not user or not user.get("passwordHash"):
            NiceMessageBox.info(self, tr("change_password"), "Set password first.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("change_password"))
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(440)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel(tr("change_password"))
        title.setStyleSheet("color: #17324D; font-size: 17px; font-weight: 800; background: transparent;")
        layout.addWidget(title)

        inp_style = """
            QLineEdit {
                background-color: #F7F9FC; border: 1px solid #DCE6F2;
                border-radius: 12px; padding: 0 14px;
                color: #17324D; font-size: 13px;
            }
        """

        current_input = QLineEdit()
        current_input.setPlaceholderText(tr("current_password"))
        current_input.setEchoMode(QLineEdit.Password)
        current_input.setFixedHeight(46)
        current_input.setStyleSheet(inp_style)
        layout.addWidget(current_input)

        new_input = QLineEdit()
        new_input.setPlaceholderText(tr("new_password"))
        new_input.setEchoMode(QLineEdit.Password)
        new_input.setFixedHeight(46)
        new_input.setStyleSheet(inp_style)
        layout.addWidget(new_input)

        confirm_input = QLineEdit()
        confirm_input.setPlaceholderText(tr("repeat_password"))
        confirm_input.setEchoMode(QLineEdit.Password)
        confirm_input.setFixedHeight(46)
        confirm_input.setStyleSheet(inp_style)
        layout.addWidget(confirm_input)

        btns = QHBoxLayout()
        cancel_btn = QPushButton(tr("cancel"))
        cancel_btn.setFixedHeight(44)
        cancel_btn.clicked.connect(dialog.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F8FC; color: #526273;
                border: 1px solid #E2EAF4; border-radius: 14px;
                padding: 0 24px; font-size: 13px; font-weight: 600;
            }
        """)

        save_btn = QPushButton(tr("save"))
        save_btn.setFixedHeight(44)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1961C7; color: white;
                border: none; border-radius: 14px;
                padding: 0 28px; font-size: 13px; font-weight: 700;
            }
        """)

        def on_save():
            if hash_password(current_input.text().strip()) != user.get("passwordHash"):
                NiceMessageBox.warning(dialog, tr("error"), tr("err_pwd_wrong"))
                return
            if len(new_input.text().strip()) < 6:
                NiceMessageBox.warning(dialog, tr("error"), tr("err_pwd_min"))
                return
            if new_input.text().strip() != confirm_input.text().strip():
                NiceMessageBox.warning(dialog, tr("error"), tr("err_pwd_match"))
                return

            new_hash = hash_password(new_input.text().strip())
            self.db.execute(
                "UPDATE users SET passwordHash = %s WHERE userId = %s",
                (new_hash, self.user_id)
            )
            dialog.accept()
            NiceMessageBox.success(self, tr("saved"), tr("saved_successfully"))

        save_btn.clicked.connect(on_save)
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)
        dialog.exec()

    def logout(self):
        confirmed = NiceMessageBox.ask(
            self, tr("logout"), tr("logout_confirm")
        )
        if not confirmed:
            return
        try:
            set_language("fa")
            if self.user_id:
                self.save_user_language("fa")

            theme_manager.apply("light")

            if self.parent_window is not None:
                self.parent_window.close()

            self.close()

            from main import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
        except Exception as e:
            print("LOGOUT ERROR:", e)