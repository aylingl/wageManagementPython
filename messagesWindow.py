from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QLineEdit,
    QComboBox
)
from PySide6.QtCore import Qt
from datetime import datetime

class MessagesWindow(QWidget):

    def __init__(self, parent_window=None):
        super().__init__()

        self.parent_window = parent_window

        self.setWindowTitle("پیام‌ها")
        self.setMinimumSize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)

        # =====================================================
        # کاربر فعلی
        # بعداً از اطلاعات حساب کاربر دریافت می‌شود
        # =====================================================

        self.current_user = "مالک"

        # =====================================================
        # افراد قابل انتخاب برای ارسال پیام
        # =====================================================

        self.recipients = [
            "علی رضایی",
            "سارا محمدی",
            "محمد احمدی"
        ]

        # =====================================================
        # پیام‌ها
        # =====================================================

        self.messages = [

            {
                "sender": "علی رضایی",
                "receiver": "مالک",
                "title": "پیام جدید",
                "description": "سلام، یک مورد درباره برنامه کاری هفته آینده داشتم.",
                "date": "امروز - ۱۰:۱۵",
                "unread": True
            },

            {
                "sender": "سارا محمدی",
                "receiver": "مالک",
                "title": "پیام جدید",
                "description": "سلام، اگر امکانش هست امروز با شما صحبت کنم.",
                "date": "امروز - ۱۱:۲۰",
                "unread": True
            },

            {
                "sender": "مالک",
                "receiver": "علی رضایی",
                "title": "پیام جدید",
                "description": "لطفاً فردا قبل از شروع کار با من هماهنگ کنید.",
                "date": "امروز - ۰۹:۳۰",
                "unread": False
            },

            {
                "sender": "محمد احمدی",
                "receiver": "مالک",
                "title": "پیام جدید",
                "description": "سلام، درباره برنامه کاری امروز یک سؤال داشتم.",
                "date": "امروز - ۱۲:۴۰",
                "unread": True
            },

            {
                "sender": "مالک",
                "receiver": "سارا محمدی",
                "title": "پیام جدید",
                "description": "سلام، ممنون از اطلاع‌رسانی شما.",
                "date": "۱۴۰۵/۰۷/۰۹ - ۱۴:۲۰",
                "unread": False
            }
        ]

        self.setup_ui()

    # =========================================================
    # UI
    # =========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        # =====================================================
        # Header
        # =====================================================

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

        title = QLabel("پیام‌ها")
        title.setObjectName("title")

        subtitle = QLabel("پیام‌های شما")
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        read_all_button = QPushButton("خوانده‌شده کردن همه")
        read_all_button.setObjectName("readAllButton")
        read_all_button.setCursor(Qt.PointingHandCursor)
        read_all_button.clicked.connect(self.mark_all_read)

        header_layout.addWidget(read_all_button)

        main_layout.addLayout(header_layout)

        # =====================================================
        # Messages Box
        # =====================================================

        messages_box = QFrame()
        messages_box.setObjectName("messagesBox")

        messages_layout = QVBoxLayout(messages_box)
        messages_layout.setContentsMargins(20, 20, 20, 20)
        messages_layout.setSpacing(12)

        # =====================================================
        # Section Header
        # =====================================================

        section_layout = QHBoxLayout()

        section_title = QLabel("پیام‌های شما")
        section_title.setObjectName("sectionTitle")

        section_layout.addWidget(section_title)
        section_layout.addStretch()

        self.unread_label = QLabel()
        self.unread_label.setObjectName("unreadLabel")

        section_layout.addWidget(self.unread_label)

        messages_layout.addLayout(section_layout)

        # =====================================================
        # Scroll
        # =====================================================

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")

        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(6, 6, 11, 6)

        self.scroll.setWidget(scroll_content)

        messages_layout.addWidget(self.scroll)

        main_layout.addWidget(messages_box)

        # =====================================================
        # Send Message Box
        # =====================================================

        send_box = QFrame()
        send_box.setObjectName("sendBox")

        send_layout = QVBoxLayout(send_box)
        send_layout.setContentsMargins(16, 14, 16, 14)
        send_layout.setSpacing(10)

        send_title = QLabel("ارسال پیام")
        send_title.setObjectName("sendTitle")

        send_layout.addWidget(send_title)

        # =====================================================
        # Receiver
        # =====================================================

        receiver_layout = QHBoxLayout()
        receiver_layout.setSpacing(8)

        receiver_label = QLabel("گیرنده:")
        receiver_label.setObjectName("receiverLabel")

        self.receiver_combo = QComboBox()
        self.receiver_combo.setObjectName("receiverCombo")
        self.receiver_combo.addItems(self.recipients)

        receiver_layout.addWidget(receiver_label)
        receiver_layout.addWidget(self.receiver_combo)

        receiver_layout.addStretch()

        send_layout.addLayout(receiver_layout)

        # =====================================================
        # Message Input
        # =====================================================

        message_layout = QHBoxLayout()
        message_layout.setSpacing(8)

        self.message_input = QLineEdit()
        self.message_input.setObjectName("messageInput")
        self.message_input.setPlaceholderText(
            "پیام خود را بنویسید..."
        )

        self.message_input.returnPressed.connect(
            self.send_message
        )

        send_button = QPushButton("ارسال")
        send_button.setObjectName("sendButton")
        send_button.setCursor(Qt.PointingHandCursor)
        send_button.clicked.connect(self.send_message)

        message_layout.addWidget(self.message_input)
        message_layout.addWidget(send_button)

        send_layout.addLayout(message_layout)

        main_layout.addWidget(send_box)

        # =====================================================
        # Style
        # =====================================================

        self.setStyleSheet("""

        QWidget {
            background-color: #F5F8FC;
            font-family: Vazirmatn;
        }

        QLabel#title {
            color: #1E2F43;
            font-size: 24px;
            font-weight: 700;
            background-color: transparent;
            border: none;
        }

        QLabel#subtitle {
            color: #8290A1;
            font-size: 13px;
            background-color: transparent;
            border: none;
        }

        QPushButton#backButton {
            background-color: white;
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

        QPushButton#readAllButton {
            background-color: #EAF3FF;
            color: #1961C7;
            border: 1px solid #C9DDF5;
            border-radius: 12px;
            padding: 9px 14px;
            font-size: 12px;
            font-weight: 600;
        }

        QPushButton#readAllButton:hover {
            background-color: #DDEEFF;
            border-color: #AFCFF0;
        }

        QFrame#messagesBox {
            background-color: white;
            border: 1px solid #E2EAF4;
            border-radius: 20px;
        }

        QLabel#sectionTitle {
            color: #1E2F43;
            font-size: 16px;
            font-weight: 700;
            background-color: white;
            border: none;
            border-radius: 10px;
        }

        QLabel#unreadLabel {
            color: #1961C7;
            background-color: #EAF3FF;
            border: 1px solid #D5E7FA;
            border-radius: 10px;
            padding: 5px 10px;
            font-size: 11px;
            font-weight: 600;
        }

        QWidget#scrollContent {
            background-color: white;
        }

        QScrollArea {
            background-color: white;
            border: none;
        }

        QScrollArea::viewport {
            background-color: white;
            border: none;
        }

        QFrame#messageCard {
            background-color: white;
            border: 1px solid #E2EAF4;
            border-radius: 16px;
        }

        QFrame#messageCard:hover {
            background-color: #EAF3FF;
            border-color: #C9DDF5;
        }

        QFrame#unreadMessage {
            background-color: #F8FBFF;
            border: 1px solid #CFE2F7;
            border-radius: 16px;
        }

        QFrame#unreadMessage:hover {
            background-color: #EAF3FF;
            border-color: #BBD8F4;
        }

        QLabel#messageIcon {
            background-color: #EAF3FF;
            color: #1961C7;
            border: none;
            border-radius: 22px;
            font-size: 18px;
            font-weight: 600;
        }

        QLabel#unreadDot {
            background-color: #1961C7;
            border: none;
            border-radius: 5px;
        }

        QLabel#messageTitle {
            color: #1E2F43;
            background-color: transparent;
            border: none;
            font-size: 14px;
            font-weight: 700;
        }

        QLabel#messageSender {
            color: #1961C7;
            background-color: transparent;
            border: none;
            font-size: 12px;
            font-weight: 600;
        }

        QLabel#messageDescription {
            color: #526273;
            background-color: transparent;
            border: none;
            font-size: 12px;
        }

        QLabel#messageDate {
            color: #8290A1;
            background-color: transparent;
            border: none;
            font-size: 11px;
        }

        QLabel#emptyLabel {
            color: #8290A1;
            background-color: transparent;
            border: none;
            font-size: 14px;
            padding: 50px;
        }

        QFrame#sendBox {
            background-color: white;
            border: 1px solid #E2EAF4;
            border-radius: 18px;
        }

        QLabel#sendTitle {
            color: #1E2F43;
            background-color: white;
            border: none;
            font-size: 14px;
            font-weight: 700;
        }

        QLabel#receiverLabel {
            color: #526273;
            background-color: transparent;
            border: none;
            font-size: 12px;
            font-weight: 600;
        }

        QComboBox#receiverCombo {
            background-color: #F5F8FC;
            color: #1E2F43;
            border: 1px solid #E2EAF4;
            border-radius: 10px;
            padding: 7px 10px;
            min-width: 150px;
            font-size: 12px;
        }

        QComboBox#receiverCombo:hover {
            border-color: #C9DDF5;
            background-color: #EAF3FF;
        }

        QComboBox#receiverCombo::drop-down {
            border: none;
            width: 25px;
        }

        QLineEdit#messageInput {
            background-color: #F5F8FC;
            color: #1E2F43;
            border: 1px solid #E2EAF4;
            border-radius: 11px;
            padding: 10px 12px;
            font-size: 12px;
        }

        QLineEdit#messageInput:focus {
            background-color: white;
            border-color: #4589E8;
        }

        QPushButton#sendButton {
            background-color: #1961C7;
            color: white;
            border: none;
            border-radius: 11px;
            padding: 10px 22px;
            font-size: 12px;
            font-weight: 600;
        }

        QPushButton#sendButton:hover {
            background-color: #4589E8;
        }

        QFrame#messageCard QLabel,
        QFrame#unreadMessage QLabel {
            background-color: transparent;
            border: none;
        }

        QScrollBar:vertical {
            width: 6px;
            background: #E8EEF6;
            border-radius: 3px;
            margin: 0px;
        }

        QScrollBar::handle:vertical {
            background: #4589E8;
            border-radius: 3px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background: #1961C7;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
        }

        """)

        self.refresh_messages()

    # =========================================================
    # Refresh Messages
    # =========================================================

    def refresh_messages(self):

        while self.scroll_layout.count():

            item = self.scroll_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        unread_count = sum(
            1
            for message in self.messages
            if message["unread"]
            and message["receiver"] == self.current_user
        )

        if unread_count:

            self.unread_label.setText(
                f"{unread_count} پیام جدید"
            )

            self.unread_label.show()

        else:

            self.unread_label.hide()

        # فقط پیام‌هایی که مربوط به کاربر فعلی هستند
        visible_messages = [
            message
            for message in self.messages
            if (
                message["receiver"] == self.current_user
                or message["sender"] == self.current_user
            )
        ]

        if not visible_messages:

            empty_label = QLabel(
                "پیامی برای نمایش وجود ندارد."
            )

            empty_label.setObjectName("emptyLabel")
            empty_label.setAlignment(Qt.AlignCenter)

            self.scroll_layout.addWidget(empty_label)
            self.scroll_layout.addStretch()

            return

        for message in visible_messages:

            self.add_message(
                self.scroll_layout,
                message
            )

        self.scroll_layout.addStretch()

    # =========================================================
    # Add Message Card
    # =========================================================

    def add_message(self, layout, message):

        if message["unread"]:

            card = QFrame()
            card.setObjectName("unreadMessage")

        else:

            card = QFrame()
            card.setObjectName("messageCard")

        card_layout = QHBoxLayout(card)

        card_layout.setContentsMargins(
            14, 13, 14, 13
        )

        card_layout.setSpacing(12)

        # =====================================================
        # Icon
        # =====================================================

        icon = QLabel("✉")
        icon.setObjectName("messageIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(44, 44)

        card_layout.addWidget(icon)

        # =====================================================
        # Text
        # =====================================================

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        # =====================================================
        # Sender
        # =====================================================

        sender_label = QLabel(
            message["sender"]
        )

        sender_label.setObjectName(
            "messageSender"
        )

        text_layout.addWidget(
            sender_label
        )

        # =====================================================
        # Message
        # =====================================================

        description_label = QLabel(
            message["description"]
        )

        description_label.setObjectName(
            "messageDescription"
        )

        description_label.setWordWrap(True)

        text_layout.addWidget(
            description_label
        )

        # =====================================================
        # Date
        # =====================================================

        date_label = QLabel(
            message["date"]
        )

        date_label.setObjectName(
            "messageDate"
        )

        text_layout.addWidget(
            date_label
        )

        card_layout.addLayout(
            text_layout
        )

        card_layout.addStretch()

        layout.addWidget(card)

    # =========================================================
    # Send Message
    # =========================================================

    def send_message(self):

        text = self.message_input.text().strip()

        if not text:
            return

        receiver = self.receiver_combo.currentText()

        now = datetime.now()

        date_text = (
            f"امروز - "
            f"{now.strftime('%H:%M')}"
        )

        new_message = {
            "sender": self.current_user,
            "receiver": receiver,
            "title": "پیام جدید",
            "description": text,
            "date": date_text,
            "unread": False
        }

        self.messages.insert(
            0,
            new_message
        )

        self.message_input.clear()

        self.refresh_messages()

    # =========================================================
    # Mark All Read
    # =========================================================

    def mark_all_read(self):

        for message in self.messages:

            if message["receiver"] == self.current_user:
                message["unread"] = False

        self.refresh_messages()