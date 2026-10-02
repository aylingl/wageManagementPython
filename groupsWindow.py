import os

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QLineEdit, QTextEdit,
    QDialog, QGraphicsDropShadowEffect
)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QTextOption
)

from database import Database
from signals import signals
from theme import theme_manager
from i18n import tr, set_language, get_language

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

        c = theme_manager.colors()

        if kind == "success":
            icon_char, color, bg = "✓", "#16A34A", "#DCFCE7"
        elif kind == "error":
            icon_char, color, bg = "✕", "#D93025", "#FEE2E2"
        elif kind == "warning":
            icon_char, color, bg = "!", "#F59E0B", "#FEF3C7"
        else:
            icon_char, color, bg = "i", "#1961C7", "#DBEAFE"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['bg_card']};"
            f"border-radius: 22px;"
            f"border: 1px solid {c['border']};"
        )
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)

        icon_label = QLabel(icon_char)
        icon_label.setFixedSize(56, 56)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(
            f"background-color: {bg};color: {color};"
            f"border-radius: 28px;font-size: 26px;font-weight: 700;"
        )

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()
        layout.addLayout(icon_row)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            f"color: {c['text_main']};font-size: 16px;"
            f"font-weight: 700;background: transparent;border: none;"
        )
        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(
            f"color: {c['text_dim']};font-size: 12px;"
            f"background: transparent;border: none;"
        )
        layout.addWidget(text_label)
        layout.addStretch()

        btn = QPushButton(tr("ok"))
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(120)
        btn.setStyleSheet(
            f"background-color: {color};color: white;"
            f"border: none;border-radius: 12px;font-size: 12px;"
            f"font-weight: 600;padding: 0px 24px;"
        )
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

        self.setWindowTitle(tr("groups_title"))
        self.setMinimumSize(700, 550)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("groupsWindow")

        self.setup_ui()
        self.load_data()

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
        self.refresh_groups()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("groups_title"))
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
        self.load_groups()
        self.refresh_groups()

    def on_employee_changed(self, complex_id):
        self.load_groups()
        self.refresh_groups()

    # =====================================================
    # LOAD DATA
    # =====================================================

    def load_data(self):
        try:
            user = self.db.fetch_one(
                "SELECT userId, name FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if not user:
                NiceMessageBox.warning(self, tr("error"), tr("err_user_not_found"))
                return

            self.user_id = user["userId"]
            self.load_groups()
            self.refresh_groups()

        except Exception as error:
            print("GroupsWindow load error:", error)
            NiceMessageBox.error(self, tr("error"), tr("err_loading_groups"))

    # =====================================================
    # LOAD GROUPS
    # =====================================================

    def load_groups(self):
        self.groups = []

        if not self.user_id:
            return

        try:
            rows = self.db.fetch_all(
                """
                SELECT c.complexId, c.name, c.address, c.activity,
                       c.description, c.ownerId, c.createdDate, c.isActive,
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
                    role_text = tr("owner_role")
                elif role == "employee":
                    role_text = tr("employee_role")
                elif role == "both":
                    role_text = tr("both_role")
                else:
                    role_text = tr("user_role")

                self.groups.append({
                    "complexId": row["complexId"],
                    "name": row["name"],
                    "address": row["address"] or "-",
                    "activity": row["activity"] or "-",
                    "description": row["description"] or "-",
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
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.go_back)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel(tr("groups_title"))
        title.setObjectName("title")

        subtitle = QLabel(tr("groups_subtitle"))
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        add_group_button = QPushButton(tr("add_group"))
        add_group_button.setObjectName("addGroupButton")
        add_group_button.setCursor(Qt.PointingHandCursor)
        add_group_button.setAttribute(Qt.WA_StyledBackground, True)
        add_group_button.clicked.connect(self.add_group)

        header_layout.addWidget(add_group_button)

        main_layout.addLayout(header_layout)

        # CONTAINER
        groups_container_frame = QFrame()
        groups_container_frame.setObjectName("groupsContainer")
        groups_container_frame.setAttribute(Qt.WA_StyledBackground, True)

        container_layout = QVBoxLayout(groups_container_frame)
        container_layout.setContentsMargins(20, 18, 20, 18)
        container_layout.setSpacing(12)

        container_title = QLabel(tr("my_groups"))
        container_title.setObjectName("containerTitle")
        container_title.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        container_layout.addWidget(container_title)

        # SCROLL
        scroll = QScrollArea()
        scroll.setObjectName("groupsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        round_bar = RoundScrollBar(Qt.Vertical, scroll)
        scroll.setVerticalScrollBar(round_bar)

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

        self.apply_stylesheet()

    # =====================================================
    # APPLY STYLESHEET
    # =====================================================

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""

        QWidget#groupsWindow {{
            background-color: {c['bg_main']};
            font-family: "Vazirmatn";
            color: {c['text_main']};
        }}

        QLabel#title {{
            background: transparent;
            border: none;
            color: {c['text_main']};
            font-size: 21px;
            font-weight: 700;
        }}

        QLabel#subtitle {{
            background: transparent;
            border: none;
            color: {c['text_dim']};
            font-size: 11px;
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

        QPushButton#addGroupButton {{
            background-color: {c['accent']};
            color: white;
            border: none;
            border-radius: 22px;
            padding: 11px 20px;
            font-size: 12px;
            font-weight: 600;
            min-height: 44px;
        }}

        QPushButton#addGroupButton:hover {{
            background-color: {c['accent_hover']};
        }}

        QFrame#groupsContainer {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 24px;
        }}

        QLabel#containerTitle {{
            background: transparent;
            border: none;
            color: {c['text_main']};
            font-size: 14px;
            font-weight: 700;
            padding: 0px 4px;
        }}

        QScrollArea#groupsScroll {{
            background: transparent;
            border: none;
            border-radius: 16px;
        }}

        QScrollArea#groupsScroll::viewport {{
            background: transparent;
            border: none;
            border-radius: 16px;
        }}

        QWidget#scrollContent {{
            background: transparent;
            border: none;
        }}

        QLabel#description {{
            background: transparent;
            border: none;
            color: {c['text_dim']};
            font-size: 11px;
        }}

        QFrame#groupCard {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 20px;
        }}

        QFrame#groupCard:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['accent']};
        }}

        QLabel#groupIcon {{
            background-color: {c['accent_light']};
            border: none;
            border-radius: 20px;
            font-size: 20px;
        }}

        QLabel#groupName {{
            background: transparent;
            border: none;
            color: {c['text_main']};
            font-size: 13px;
            font-weight: 700;
        }}

        QLabel#groupAddress {{
            background: transparent;
            border: none;
            color: {c['text_dim']};
            font-size: 10px;
        }}

        QLabel#groupActivity {{
            background: transparent;
            border: none;
            color: {c['text_dim']};
            font-size: 10px;
        }}

        QLabel#employeeCount {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border: none;
            border-radius: 8px;
            padding: 2px 8px;
            font-size: 9px;
            font-weight: 600;
        }}

        QPushButton#manageButton {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border: none;
            border-radius: 10px;
            padding: 7px 12px;
            font-size: 10px;
            font-weight: 600;
            min-height: 24px;
        }}

        QPushButton#manageButton:hover {{
            background-color: {c['bg_hover']};
        }}

        QPushButton#deleteButton {{
            background-color: {c['danger_bg']};
            color: {c['danger']};
            border: none;
            border-radius: 10px;
            padding: 7px 12px;
            font-size: 10px;
            font-weight: 600;
            min-height: 24px;
        }}

        QPushButton#deleteButton:hover {{
            background-color: {c['bg_hover']};
        }}

        QFrame#groupDialog, QFrame#confirmDialog {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 20px;
        }}

        QLabel#dialogTitle {{
            background: transparent;
            border: none;
            color: {c['text_main']};
            font-size: 17px;
            font-weight: 700;
            qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
        }}

        QLabel#dialogDescription {{
            background: transparent;
            border: none;
            color: {c['text_dim']};
            font-size: 12px;
            qproperty-alignment: 'AlignRight | AlignAbsolute';
        }}

        QLabel#errorLabel {{
            color: {c['danger']};
            background: transparent;
            border: none;
            font-size: 11px;
            font-weight: 500;
            qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
        }}

        QLineEdit#dialogInput {{
            background-color: {c['bg_input']};
            border: 1px solid {c['border']};
            border-radius: 22px;
            padding: 10px 18px;
            color: {c['text_main']};
            font-size: 12px;
            min-height: 44px;
        }}

        QLineEdit#dialogInput:focus {{
            border: 2px solid {c['accent']};
            background-color: {c['bg_card']};
        }}

        QTextEdit#dialogInput {{
            background-color: {c['bg_input']};
            border: 1px solid {c['border']};
            border-radius: 16px;
            padding: 10px 14px;
            color: {c['text_main']};
            font-size: 12px;
        }}

        QTextEdit#dialogInput:focus {{
            border: 2px solid {c['accent']};
            background-color: {c['bg_card']};
        }}

        QPushButton#dialogCancel {{
            background-color: {c['bg_input']};
            color: {c['text_dim']};
            border: 1px solid {c['border']};
            border-radius: 22px;
            padding: 10px;
            font-size: 12px;
            font-weight: 600;
            min-height: 44px;
        }}

        QPushButton#dialogCancel:hover {{
            background-color: {c['bg_hover']};
        }}

        QPushButton#dialogSave {{
            background-color: {c['accent']};
            color: white;
            border: none;
            border-radius: 22px;
            padding: 10px;
            font-size: 12px;
            font-weight: 600;
            min-height: 44px;
        }}

        QPushButton#dialogSave:hover {{
            background-color: {c['accent_hover']};
        }}

        QPushButton#dialogDelete {{
            background-color: {c['danger']};
            color: white;
            border: none;
            border-radius: 22px;
            padding: 10px;
            font-size: 12px;
            font-weight: 600;
            min-height: 44px;
        }}

        QPushButton#dialogDelete:hover {{
            background-color: #B71C1C;
        }}

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
            empty_label = QLabel(tr("no_groups_yet"))
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

        address = QLabel(f"{tr('address')}: {group['address']}")
        address.setObjectName("groupAddress")
        address.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        activity = QLabel(f"{tr('activity')}: {group['activity']}")
        activity.setObjectName("groupActivity")
        activity.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        text_layout.addWidget(name)
        text_layout.addWidget(address)
        text_layout.addWidget(activity)

        count = QLabel(tr("employees_count_label", n=group['employeeCount']))
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
        role_label.setStyleSheet(
            f"background-color: {theme_manager.colors()['accent_light']};"
            f"color: {theme_manager.colors()['accent']};"
            f"border: none; border-radius: 8px;"
            f"padding: 2px 10px; font-size: 10px; font-weight: 600;"
        )

        layout.addWidget(role_label)

        if group["roleValue"] in ("owner", "both"):
            manage_button = QPushButton(tr("manage"))
            manage_button.setObjectName("manageButton")
            manage_button.setCursor(Qt.PointingHandCursor)
            manage_button.clicked.connect(
                lambda checked=False, g=group: self.manage_group(g)
            )

            delete_button = QPushButton(tr("delete"))
            delete_button.setObjectName("deleteButton")
            delete_button.setCursor(Qt.PointingHandCursor)
            delete_button.clicked.connect(
                lambda checked=False, g=group: self.confirm_delete_group(g)
            )

            layout.addWidget(manage_button)
            layout.addWidget(delete_button)

        return card

    # =====================================================
    # MANAGE
    # =====================================================

    def manage_group(self, group):
        try:
            employees = self.get_group_employee_names(group["complexId"])
            if employees:
                employee_text = "\n".join(f"• {e}" for e in employees)
            else:
                employee_text = tr("no_staff_yet")

            NiceMessageBox.info(
                self,
                group["name"],
                (
                    f"{tr('address')}: {group['address']}\n"
                    f"{tr('activity')}: {group['activity']}\n\n"
                    f"{tr('description_label')}:\n{group['description']}\n\n"
                    f"{tr('staff')}:\n{employee_text}"
                )
            )
        except Exception as error:
            print("MANAGE GROUP ERROR:", error)
            NiceMessageBox.error(self, tr("error"), tr("err_loading_groups"))

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
            return [row["name"] or tr("no_name") for row in rows]
        except Exception as error:
            print("GET GROUP EMPLOYEES ERROR:", error)
            return []

    # =====================================================
    # CONFIRM DELETE
    # =====================================================

    def confirm_delete_group(self, group):
        c = theme_manager.colors()

        dialog = QFrame(self, Qt.Dialog)
        dialog.setWindowTitle(tr("confirm_delete"))
        dialog.setObjectName("confirmDialog")
        dialog.setFixedSize(460, 300)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel(tr("confirm_delete"))
        title.setObjectName("dialogTitle")
        title.setWordWrap(True)

        description = QLabel(tr("confirm_delete_msg", name=group['name']))
        description.setObjectName("dialogDescription")
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        cancel = QPushButton(tr("cancel"))
        cancel.setObjectName("dialogCancel")
        cancel.setCursor(Qt.PointingHandCursor)

        delete = QPushButton(tr("delete"))
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

            exists = self.db.fetch_one(
                "SELECT complexId FROM complexes WHERE complexId = %s",
                (complex_id,)
            )

            if not exists:
                NiceMessageBox.error(self, tr("error"), tr("err_group_not_found"))
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
                "DELETE FROM complex_members WHERE complexId = %s",
                (complex_id,)
            )

            self.db.execute(
                "DELETE FROM complexes WHERE complexId = %s",
                (complex_id,)
            )

            self.db.execute("SET FOREIGN_KEY_CHECKS = 1")

            still_exists = self.db.fetch_one(
                "SELECT complexId FROM complexes WHERE complexId = %s",
                (complex_id,)
            )

            if still_exists:
                NiceMessageBox.error(self, tr("error"), tr("err_deleting_group"))
                return

            self.load_groups()
            self.refresh_groups()

            if self.parent_window:
                if hasattr(self.parent_window, "refresh_groups_from_database"):
                    self.parent_window.refresh_groups_from_database()

            NiceMessageBox.success(
                self,
                tr("deleted"),
                tr("deleted_msg_group", name=group['name'])
            )

        except Exception as error:
            print("DELETE GROUP ERROR:", error)
            try:
                self.db.execute("SET FOREIGN_KEY_CHECKS = 1")
            except Exception:
                pass
            NiceMessageBox.error(self, tr("error"), tr("err_deleting_group"))

    # =====================================================
    # ADD GROUP
    # =====================================================

    def add_group(self):
        c = theme_manager.colors()

        dialog = QFrame(self, Qt.Dialog)
        dialog.setWindowTitle(tr("add_group_title"))
        dialog.setObjectName("groupDialog")
        dialog.setFixedSize(520, 600)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setAttribute(Qt.WA_StyledBackground, True)

        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.setContentsMargins(26, 26, 26, 26)
        dialog_layout.setSpacing(6)

        title = QLabel(tr("add_group_title"))
        title.setObjectName("dialogTitle")
        title.setWordWrap(True)

        description = QLabel(tr("add_group_desc"))
        description.setObjectName("dialogDescription")
        description.setWordWrap(True)

        name_input = QLineEdit()
        name_input.setPlaceholderText(tr("group_name_ph"))
        name_input.setObjectName("dialogInput")
        name_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        name_input.setLayoutDirection(Qt.RightToLeft)

        name_error = QLabel()
        name_error.setObjectName("errorLabel")
        name_error.setWordWrap(True)
        name_error.hide()

        address_input = QLineEdit()
        address_input.setPlaceholderText(tr("address_ph"))
        address_input.setObjectName("dialogInput")
        address_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        address_input.setLayoutDirection(Qt.RightToLeft)

        address_error = QLabel()
        address_error.setObjectName("errorLabel")
        address_error.setWordWrap(True)
        address_error.hide()

        activity_input = QLineEdit()
        activity_input.setPlaceholderText(tr("activity_ph"))
        activity_input.setObjectName("dialogInput")
        activity_input.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        activity_input.setLayoutDirection(Qt.RightToLeft)

        activity_error = QLabel()
        activity_error.setObjectName("errorLabel")
        activity_error.setWordWrap(True)
        activity_error.hide()

        details_input = QTextEdit()
        details_input.setPlaceholderText(tr("description_group_ph"))
        details_input.setObjectName("dialogInput")
        details_input.setFixedHeight(100)
        details_input.setLayoutDirection(Qt.RightToLeft)
        details_input.document().setDefaultTextOption(
            QTextOption(Qt.AlignRight | Qt.AlignAbsolute)
        )

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        cancel = QPushButton(tr("cancel"))
        cancel.setObjectName("dialogCancel")
        cancel.setCursor(Qt.PointingHandCursor)

        save = QPushButton(tr("add"))
        save.setObjectName("dialogSave")
        save.setCursor(Qt.PointingHandCursor)

        buttons.addWidget(cancel)
        buttons.addWidget(save)

        dialog_layout.addWidget(title)
        dialog_layout.addWidget(description)
        dialog_layout.addSpacing(6)
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

        error_style = (
            f"QLineEdit {{"
            f"background-color: {c['danger_bg']};"
            f"border: 1px solid {c['danger']};"
            f"border-radius: 22px;"
            f"padding: 10px 18px;"
            f"color: {c['text_main']};"
            f"font-size: 12px;"
            f"min-height: 44px;"
            f"}}"
        )

        def save_group():
            name = name_input.text().strip()
            address = address_input.text().strip()
            activity = activity_input.text().strip()
            description_text = details_input.toPlainText().strip()

            has_error = False

            if not name:
                name_error.setText(tr("err_group_name"))
                name_error.show()
                name_input.setStyleSheet(error_style)
                has_error = True
            elif contains_digit(name):
                name_error.setText(tr("err_group_name_digit"))
                name_error.show()
                name_input.setStyleSheet(error_style)
                has_error = True
            elif count_letters(name) < 4:
                name_error.setText(tr("err_group_name_len"))
                name_error.show()
                name_input.setStyleSheet(error_style)
                has_error = True

            if not address:
                address_error.setText(tr("err_address"))
                address_error.show()
                address_input.setStyleSheet(error_style)
                has_error = True
            elif contains_digit(address):
                address_error.setText(tr("err_address_digit"))
                address_error.show()
                address_input.setStyleSheet(error_style)
                has_error = True
            elif count_letters(address) < 5:
                address_error.setText(tr("err_address_len"))
                address_error.show()
                address_input.setStyleSheet(error_style)
                has_error = True

            if not activity:
                activity_error.setText(tr("err_activity"))
                activity_error.show()
                activity_input.setStyleSheet(error_style)
                has_error = True
            elif contains_digit(activity):
                activity_error.setText(tr("err_activity_digit"))
                activity_error.show()
                activity_input.setStyleSheet(error_style)
                has_error = True
            elif count_letters(activity) < 4:
                activity_error.setText(tr("err_activity_len"))
                activity_error.show()
                activity_input.setStyleSheet(error_style)
                has_error = True

            if has_error:
                return

            try:
                complex_id = self.db.execute(
                    """
                    INSERT INTO complexes
                    (name, address, description, activity, ownerId, createdDate, isActive)
                    VALUES (%s, %s, %s, %s, %s, NOW(), '1')
                    """,
                    (name, address, description_text or None, activity, self.user_id)
                )

                if not complex_id:
                    NiceMessageBox.error(dialog, tr("error"), tr("err_saving_group"))
                    return

                member_id = self.db.execute(
                    """
                    INSERT INTO complex_members
                    (complexId, userId, role, joinedDate, isActive)
                    VALUES (%s, %s, 'owner', NOW(), '1')
                    """,
                    (complex_id, self.user_id)
                )

                if not member_id:
                    self.db.execute(
                        "DELETE FROM complexes WHERE complexId = %s",
                        (complex_id,)
                    )
                    NiceMessageBox.error(dialog, tr("error"), tr("err_saving_group"))
                    return

                self.load_groups()
                self.refresh_groups()

                if self.parent_window:
                    if hasattr(self.parent_window, "refresh_groups_from_database"):
                        self.parent_window.refresh_groups_from_database()

                dialog.close()
                NiceMessageBox.success(self, tr("added"), tr("added_msg_group"))

            except Exception as error:
                print("ADD GROUP ERROR:", error)
                NiceMessageBox.error(dialog, tr("error"), tr("err_saving_group"))

        save.clicked.connect(save_group)

        dialog.show()