import os
from datetime import datetime, date

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QDialog, QLineEdit,
    QComboBox, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect
)

from PySide6.QtCore import (
    Qt, QTimer, QDate, QPoint, QSize
)
from PySide6.QtGui import QPainter, QColor, QPixmap, QPainterPath

from database import Database
from signals import signals
from theme import theme_manager
from i18n import tr, set_language, get_language

# =========================================================
# ROUNDED AVATAR
# =========================================================

class RoundedAvatar(QLabel):

    def __init__(self, size=36, parent=None):
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
            0, 0,
            self.avatar_size, self.avatar_size,
            self.avatar_size / 2, self.avatar_size / 2
        )

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self.setPixmap(result)

# =========================================================
# ROUND SCROLL BAR
# =========================================================

class RoundScrollBar(QScrollBar):
    def __init__(self, orientation=Qt.Vertical, parent=None):
        super().__init__(orientation, parent)
        self.setFixedWidth(12)
        self.setStyleSheet("QScrollBar {background: transparent;border: none;margin: 0px;}")

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
        painter.drawRoundedRect(int(track_x), int(track_top), track_width, int(track_height), track_width/2, track_width/2)

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
        painter.drawRoundedRect(int(handle_x), int(handle_y), handle_width, int(handle_height), handle_width/2, handle_width/2)

# =========================================================
# ROUNDED COMBO BOX
# =========================================================

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
        self._popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self._popup.setAttribute(Qt.WA_TranslucentBackground, True)

        outer = QVBoxLayout(self._popup)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("comboCard")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
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
            QListWidget {{background: transparent;border: none;outline: none;padding: 6px;color: {c['text_main']};font-family: "Vazirmatn";font-size: 12px;}}
            QListWidget::item {{background: transparent;color: {c['text_main']};border-radius: 10px;padding: 10px 14px;margin: 2px 4px;min-height: 20px;}}
            QListWidget::item:hover {{background-color: {c['bg_hover']};color: {c['accent']};}}
            QListWidget::item:selected {{background-color: {c['accent']};color: white;}}
            QScrollBar:vertical {{width: 8px;background: transparent;border: none;margin: 6px 2px;}}
            QScrollBar::handle:vertical {{background: {c['accent']};border-radius: 4px;min-height: 24px;}}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{height: 0px;}}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{background: transparent;}}
        """)

        for i in range(self.count()):
            item = QListWidgetItem(self.itemText(i))
            item.setData(Qt.UserRole, i)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setSizeHint(QSize(0, 40))
            self._list.addItem(item)
            if i == self.currentIndex():
                self._list.setCurrentItem(item)

        self._list.itemClicked.connect(self._on_item_clicked)
        card_layout.addWidget(self._list)

        self._popup.setStyleSheet(f"QFrame#comboCard {{background-color: {c['bg_card']};border: 1px solid {c['border']};border-radius: 16px;}}")

        count = max(self.count(), 1)
        content_h = count * 40 + 32
        popup_w = max(self.width(), 180)
        popup_h = min(content_h, 240)
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

# =========================================================
# JALALI HELPERS
# =========================================================

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + (365*gy) + ((gy2+3)//4) - ((gy2+99)//100) + ((gy2+399)//400) + gd + g_d_m[gm-1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd

def jalali_datetime(d):
    if isinstance(d, datetime):
        jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
        return f"{jy:04d}/{jm:02d}/{jd:02d} - {d.strftime('%H:%M')}"
    if isinstance(d, date):
        jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
        return f"{jy:04d}/{jm:02d}/{jd:02d}"
    return str(d) if d else "-"

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
        self.setFixedSize(340, 230)

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
        card.setStyleSheet(f"background-color: {c['bg_card']};border-radius: 20px;border: 1px solid {c['border']};")
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(10)

        icon_label = QLabel(icon_char)
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"background-color: {bg};color: {color};border-radius: 24px;font-size: 22px;font-weight: 700;")

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()
        layout.addLayout(icon_row)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {c['text_main']};font-size: 14px;font-weight: 700;background: transparent;border: none;")
        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"color: {c['text_dim']};font-size: 11px;background: transparent;border: none;")
        layout.addWidget(text_label)
        layout.addStretch()

        btn = QPushButton(tr("ok"))
        btn.setFixedHeight(38)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(100)
        btn.setStyleSheet(f"background-color: {color};color: white;border: none;border-radius: 19px;font-size: 12px;font-weight: 600;padding: 0px 20px;")
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
# MESSAGES WINDOW
# =========================================================

class MessagesWindow(QWidget):

    def __init__(self, parent_window=None, phone_number=None, complex_id=None):
        super().__init__()

        self.parent_window = parent_window
        self.phone_number = phone_number
        self.complex_id = complex_id

        if self.phone_number is None and parent_window is not None:
            self.phone_number = getattr(parent_window, "phone_number", None)

        if self.complex_id is None and parent_window is not None:
            self.complex_id = getattr(parent_window, "complex_id", None)
            if not self.complex_id:
                getter = getattr(parent_window, "get_current_complex_id", None)
                if callable(getter):
                    self.complex_id = getter()

        self.db = Database()

        self.user_id = None
        self.my_name = "—"
        self.messages = []
        self.recipients = []

        self.setWindowTitle(tr("messages_title"))
        self.setMinimumSize(500, 400)
        self.resize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("messagesWindow")

        self.load_user_id()
        self.setup_ui()
        self.load_messages()
        self.load_recipients()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)
        signals.data_changed.connect(self.on_data_changed)
        signals.employee_added.connect(self.on_employee_changed)

    # =====================================================
    # THEME / LANGUAGE
    # =====================================================

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("messages_title"))
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
        self.load_messages()
        self.load_recipients()

    def on_data_changed(self, kind):
        self.load_messages()

    def on_employee_changed(self, complex_id):
        if complex_id == self.complex_id:
            self.load_recipients()

    # =====================================================
    # LOAD USER
    # =====================================================

    def load_user_id(self):
        if not self.phone_number:
            return
        try:
            user = self.db.fetch_one(
                "SELECT userId, name FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if user:
                self.user_id = user["userId"]
                self.my_name = user.get("name") or "—"
        except Exception as e:
            print("MESSAGES LOAD USER ID ERROR:", e)

    # =====================================================
    # LOAD MESSAGES
    # =====================================================

    def load_messages(self):
        self.messages = []

        if not self.user_id:
            self.refresh_messages()
            return

        try:
            rows = self.db.fetch_all(
                """
                SELECT m.messageId, m.senderId, m.receiverId, m.title,
                       m.message, m.sentDate, m.isRead,
                       su.name AS sender_name,
                       su.imageBase64 AS sender_image,
                       ru.name AS receiver_name,
                       ru.imageBase64 AS receiver_image
                FROM messages m
                LEFT JOIN users su ON su.userId = m.senderId
                LEFT JOIN users ru ON ru.userId = m.receiverId
                WHERE m.senderId = %s OR m.receiverId = %s
                ORDER BY m.sentDate DESC
                LIMIT 200
                """,
                (self.user_id, self.user_id)
            )

            for r in rows or []:
                is_outgoing = (r["senderId"] == self.user_id)

                self.messages.append({
                    "id": r["messageId"],
                    "sender_id": r["senderId"],
                    "receiver_id": r["receiverId"],
                    "sender_name": r.get("sender_name") or "—",
                    "sender_image": r.get("sender_image") or "",
                    "receiver_name": r.get("receiver_name") or "—",
                    "receiver_image": r.get("receiver_image") or "",
                    "title": r.get("title") or tr("new_message_title"),
                    "message": r.get("message") or "",
                    "sent_date": r.get("sentDate"),
                    "is_read": str(r.get("isRead") or "0") == "1",
                    "is_outgoing": is_outgoing,
                })

        except Exception as e:
            print("LOAD MESSAGES ERROR:", e)

        self.refresh_messages()

    # =====================================================
    # LOAD RECIPIENTS
    # =====================================================

    def load_recipients(self):
        self.recipients = []

        if not self.complex_id:
            self.update_recipients_combo()
            return

        try:
            rows = self.db.fetch_all(
                """
                SELECT cm.userId, u.name
                FROM complex_members cm
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                  AND cm.isActive = '1'
                  AND cm.userId <> %s
                ORDER BY u.name ASC
                """,
                (self.complex_id, self.user_id or 0)
            )

            for r in rows or []:
                self.recipients.append({
                    "user_id": r["userId"],
                    "name": r.get("name") or "—",
                })

        except Exception as e:
            print("LOAD RECIPIENTS ERROR:", e)

        self.update_recipients_combo()

    def update_recipients_combo(self):
        if not hasattr(self, "receiver_combo"):
            return

        self.receiver_combo.blockSignals(True)
        self.receiver_combo.clear()

        for r in self.recipients:
            self.receiver_combo.addItem(r["name"], r["user_id"])

        self.receiver_combo.blockSignals(False)

    # =====================================================
    # LOAD AVATAR PIXMAP (فقط آواتار پیش‌فرض)
    # =====================================================

    def load_avatar_pixmap(self, image_value):
        if not image_value:
            return None
        try:
            # ═══ اگه مسیر مطلق بود (عکس سفارشی) → نشون نده ═══
            if os.path.isabs(image_value):
                return None

            # ═══ فقط آواتار پیش‌فرض ═══
            path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "avatars",
                image_value
            )
            if os.path.exists(path):
                return QPixmap(path)
        except Exception as e:
            print("LOAD AVATAR ERROR:", e)
        return None

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(38, 38)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.go_back)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title = QLabel(tr("messages_title"))
        title.setObjectName("messagesTitle")

        subtitle = QLabel(tr("messages_subtitle"))
        subtitle.setObjectName("messagesSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        self.unread_label = QLabel()
        self.unread_label.setObjectName("unreadLabel")
        self.unread_label.setAlignment(Qt.AlignCenter)
        self.unread_label.hide()

        header_layout.addWidget(self.unread_label)

        mark_all_btn = QPushButton(tr("mark_all_read"))
        mark_all_btn.setObjectName("markAllBtn")
        mark_all_btn.setFixedHeight(36)
        mark_all_btn.setCursor(Qt.PointingHandCursor)
        mark_all_btn.setAttribute(Qt.WA_StyledBackground, True)
        mark_all_btn.clicked.connect(self.mark_all_read)

        header_layout.addWidget(mark_all_btn)

        main_layout.addLayout(header_layout)

        messages_box = QFrame()
        messages_box.setObjectName("messagesBox")
        messages_box.setAttribute(Qt.WA_StyledBackground, True)

        messages_layout = QVBoxLayout(messages_box)
        messages_layout.setContentsMargins(14, 14, 14, 14)
        messages_layout.setSpacing(8)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        round_bar = RoundScrollBar(Qt.Vertical, self.scroll)
        self.scroll.setVerticalScrollBar(round_bar)

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setAttribute(Qt.WA_TranslucentBackground, True)

        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setContentsMargins(4, 4, 8, 4)

        self.scroll.setWidget(scroll_content)
        messages_layout.addWidget(self.scroll)

        main_layout.addWidget(messages_box, 1)

        send_box = QFrame()
        send_box.setObjectName("sendBox")
        send_box.setAttribute(Qt.WA_StyledBackground, True)

        send_layout = QVBoxLayout(send_box)
        send_layout.setContentsMargins(14, 12, 14, 12)
        send_layout.setSpacing(8)

        send_title = QLabel(tr("send_message"))
        send_title.setObjectName("sendTitle")
        send_layout.addWidget(send_title)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(8)

        self.receiver_combo = RoundedComboBox()
        self.receiver_combo.setObjectName("receiverCombo")
        self.receiver_combo.setFixedHeight(38)
        self.receiver_combo.setMinimumWidth(180)
        self.receiver_combo.setCursor(Qt.PointingHandCursor)

        self.message_input = QLineEdit()
        self.message_input.setObjectName("messageInput")
        self.message_input.setPlaceholderText(tr("message_ph"))
        self.message_input.setFixedHeight(38)
        self.message_input.returnPressed.connect(self.send_message)

        send_button = QPushButton(tr("send"))
        send_button.setObjectName("sendButton")
        send_button.setFixedHeight(38)
        send_button.setCursor(Qt.PointingHandCursor)
        send_button.setAttribute(Qt.WA_StyledBackground, True)
        send_button.clicked.connect(self.send_message)

        row_layout.addWidget(self.receiver_combo)
        row_layout.addWidget(self.message_input, 1)
        row_layout.addWidget(send_button)

        send_layout.addLayout(row_layout)

        main_layout.addWidget(send_box)

        self.apply_stylesheet()
        self.refresh_unread_badge()

    # =====================================================
    # APPLY STYLESHEET
    # =====================================================

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""

        QWidget#messagesWindow {{
            background-color: {c['bg_main']};
            font-family: Vazirmatn;
            color: {c['text_main']};
        }}

        QLabel#messagesTitle {{
            color: {c['text_main']};
            font-size: 20px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#messagesSubtitle {{
            color: {c['text_dim']};
            font-size: 11px;
            background: transparent;
        }}

        QPushButton#backButton {{
            background-color: {c['bg_card']};
            color: {c['accent']};
            border: 1px solid {c['border']};
            border-radius: 19px;
            font-size: 20px;
            font-weight: 600;
            padding: 0px;
        }}

        QPushButton#backButton:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['border_hover']};
        }}

        QLabel#unreadLabel {{
            color: {c['accent']};
            background-color: {c['accent_light']};
            border: 1px solid {c['border_hover']};
            border-radius: 14px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 700;
        }}

        QPushButton#markAllBtn {{
            background-color: {c['bg_card']};
            color: {c['accent']};
            border: 1px solid {c['border_hover']};
            border-radius: 18px;
            padding: 0 16px;
            font-size: 11px;
            font-weight: 700;
        }}

        QPushButton#markAllBtn:hover {{
            background-color: {c['bg_hover']};
        }}

        QFrame#messagesBox {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}

        QWidget#scrollContent {{
            background: transparent;
        }}

        QScrollArea {{
            background: transparent;
            border: none;
        }}

        QScrollArea::viewport {{
            background: transparent;
        }}

        QFrame#messageCard {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 16px;
        }}

        QFrame#messageCard:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['accent']};
        }}

        QFrame#unreadCard {{
            background-color: {c['accent_light']};
            border: 1px solid {c['accent']};
            border-radius: 16px;
        }}

        QFrame#unreadCard:hover {{
            background-color: {c['bg_hover']};
        }}

        QLabel#msgIcon {{
            background-color: {c['accent_light']};
            color: {c['accent']};
            border-radius: 18px;
            font-size: 16px;
            font-weight: 700;
        }}

        QLabel#msgIconOut {{
            background-color: {c['success_bg']};
            color: #16A34A;
            border-radius: 18px;
            font-size: 16px;
            font-weight: 700;
        }}

        QLabel#msgSender {{
            color: {c['accent']};
            font-size: 11px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#msgReceiver {{
            color: {c['text_dim']};
            font-size: 10px;
            background: transparent;
        }}

        QLabel#msgBody {{
            color: {c['text_main']};
            font-size: 12px;
            background: transparent;
        }}

        QLabel#msgDate {{
            color: {c['text_dim']};
            font-size: 10px;
            background: transparent;
        }}

        QFrame#sendBox {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}

        QLabel#sendTitle {{
            color: {c['text_main']};
            font-size: 13px;
            font-weight: 700;
            background: transparent;
        }}

        QLineEdit#messageInput {{
            background-color: {c['bg_input']};
            color: {c['text_main']};
            border: 1px solid {c['border']};
            border-radius: 19px;
            padding: 0 14px;
            font-size: 12px;
        }}

        QLineEdit#messageInput:focus {{
            background-color: {c['bg_card']};
            border: 2px solid {c['accent']};
        }}

        QComboBox#receiverCombo {{
            background-color: {c['bg_input']};
            color: {c['text_main']};
            border: 1px solid {c['border']};
            border-radius: 19px;
            padding: 0 14px;
            font-size: 12px;
            font-weight: 600;
        }}

        QComboBox#receiverCombo:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['border_hover']};
        }}

        QComboBox#receiverCombo::drop-down {{
            border: none;
            width: 24px;
        }}

        QComboBox#receiverCombo::down-arrow {{
            image: none;
            width: 0px;
            height: 0px;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {c['accent']};
            margin-right: 8px;
        }}

        QPushButton#sendButton {{
            background-color: {c['accent']};
            color: white;
            border: none;
            border-radius: 19px;
            padding: 0 20px;
            font-size: 12px;
            font-weight: 700;
        }}

        QPushButton#sendButton:hover {{
            background-color: {c['accent_hover']};
        }}

        QLabel#emptyLabel {{
            color: {c['text_dim']};
            font-size: 13px;
            padding: 40px;
            background: transparent;
        }}

        """)

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_messages(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.messages:
            empty = QLabel(tr("no_messages"))
            empty.setObjectName("emptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty)
            self.scroll_layout.addStretch()
            self.refresh_unread_badge()
            return

        for msg in self.messages:
            self.scroll_layout.addWidget(self.create_message_card(msg))

        self.scroll_layout.addStretch()
        self.refresh_unread_badge()

    def refresh_unread_badge(self):
        if not hasattr(self, "unread_label"):
            return

        unread = sum(
            1 for m in self.messages
            if not m["is_read"] and not m["is_outgoing"]
        )

        if unread > 0:
            self.unread_label.setText(tr("new_messages_count", n=unread))
            self.unread_label.show()
        else:
            self.unread_label.hide()

    # =====================================================
    # MESSAGE CARD
    # =====================================================

    def create_message_card(self, msg):
        is_unread = (not msg["is_read"]) and (not msg["is_outgoing"])

        card = QFrame()
        card.setObjectName("unreadCard" if is_unread else "messageCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        # ═══ آواتار پیش‌فرض (اگه بود) وگرنه آیکون ═══
        if msg["is_outgoing"]:
            avatar_image = msg.get("receiver_image") or ""
        else:
            avatar_image = msg.get("sender_image") or ""

        avatar_pixmap = self.load_avatar_pixmap(avatar_image)

        if avatar_pixmap is not None and not avatar_pixmap.isNull():
            avatar = RoundedAvatar(36)
            avatar.set_avatar(avatar_pixmap)
            layout.addWidget(avatar)
        else:
            if msg["is_outgoing"]:
                icon = QLabel("↗")
                icon.setObjectName("msgIconOut")
            else:
                icon = QLabel("✉")
                icon.setObjectName("msgIcon")
            icon.setFixedSize(36, 36)
            icon.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon)

        # متن
        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        sender_label = QLabel(msg["sender_name"])
        sender_label.setObjectName("msgSender")

        receiver_lbl = QLabel(f"→ {msg['receiver_name']}")
        receiver_lbl.setObjectName("msgReceiver")

        body_label = QLabel(msg["message"])
        body_label.setObjectName("msgBody")
        body_label.setWordWrap(True)

        date_label = QLabel(jalali_datetime(msg["sent_date"]))
        date_label.setObjectName("msgDate")

        text_col.addWidget(sender_label)
        text_col.addWidget(receiver_lbl)
        text_col.addWidget(body_label)
        text_col.addWidget(date_label)

        layout.addLayout(text_col, 1)

        if is_unread:
            def clicked(event, m_id=msg["id"]):
                self.mark_as_read(m_id)
                event.accept()

            card.mousePressEvent = clicked

        return card

    # =====================================================
    # MARK AS READ
    # =====================================================

    def mark_as_read(self, message_id):
        try:
            self.db.execute(
                "UPDATE messages SET isRead = '1' WHERE messageId = %s",
                (message_id,)
            )
            self.load_messages()
        except Exception as e:
            print("MARK READ ERROR:", e)

    def mark_all_read(self):
        if not self.user_id:
            return

        try:
            self.db.execute(
                "UPDATE messages SET isRead = '1' WHERE receiverId = %s AND isRead = '0'",
                (self.user_id,)
            )
            self.load_messages()
        except Exception as e:
            print("MARK ALL READ ERROR:", e)

    # =====================================================
    # SEND MESSAGE
    # =====================================================

    def send_message(self):
        text = self.message_input.text().strip()
        if not text:
            return

        if self.receiver_combo.count() == 0:
            NiceMessageBox.warning(self, tr("error"), tr("err_no_employee"))
            return

        receiver_id = self.receiver_combo.currentData()

        if not receiver_id or not self.user_id:
            return

        try:
            self.db.execute(
                """
                INSERT INTO messages (senderId, receiverId, title, message, sentDate, isRead)
                VALUES (%s, %s, %s, %s, NOW(), '0')
                """,
                (self.user_id, receiver_id, tr("new_message_title"), text)
            )

            self.message_input.clear()
            self.load_messages()

            signals.data_changed.emit("all")

        except Exception as e:
            print("SEND MESSAGE ERROR:", e)
            NiceMessageBox.error(self, tr("error"), tr("edit_error_msg"))

    # =====================================================
    # BACK
    # =====================================================

    def go_back(self):
        self.close()
        if self.parent_window:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()