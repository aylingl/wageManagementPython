import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QComboBox,
    QTimeEdit,
    QScrollArea,
    QScrollBar,
    QDialog
)

from PySide6.QtCore import Qt, QTime, QTimer
from PySide6.QtGui import QPainter, QColor

from database import Database

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

        track_width = 6
        track_x = (self.width() - track_width) / 2
        track_top = 6
        track_bottom = self.height() - 6
        track_height = track_bottom - track_top

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#EEF3FA"))

        painter.drawRoundedRect(
            int(track_x),
            int(track_top),
            track_width,
            int(track_height),
            track_width / 2,
            track_width / 2
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

        handle_height = int(
            groove_height * page_step / total_range
        )

        handle_height = max(42, handle_height)
        handle_height = min(handle_height, groove_height)

        available_space = groove_height - handle_height

        if maximum == minimum:
            handle_y = groove_top
        else:
            value_ratio = (
                self.value() - minimum
            ) / (maximum - minimum)

            handle_y = (
                groove_top + available_space * value_ratio
            )

        handle_width = 8
        handle_x = (self.width() - handle_width) / 2

        painter.setBrush(QColor("#4589E8"))

        painter.drawRoundedRect(
            int(handle_x),
            int(handle_y),
            handle_width,
            int(handle_height),
            handle_width / 2,
            handle_width / 2
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

        if kind == "success":
            icon_char = "✓"
            color = "#16A34A"
            bg = "#DCFCE7"
        elif kind == "error":
            icon_char = "✕"
            color = "#D93025"
            bg = "#FEE2E2"
        elif kind == "warning":
            icon_char = "!"
            color = "#F59E0B"
            bg = "#FEF3C7"
        else:
            icon_char = "i"
            color = "#1961C7"
            bg = "#DBEAFE"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("niceMsgCard")
        card.setStyleSheet("""
            QFrame#niceMsgCard {
                background-color: #FFFFFF;
                border-radius: 22px;
                border: 1px solid #E2EAF4;
            }
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
        title_label.setStyleSheet("""
            QLabel {
                color: #1E2F43;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
                border: none;
            }
        """)

        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            QLabel {
                color: #526273;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)

        layout.addWidget(text_label)
        layout.addStretch()

        btn = QPushButton("تأیید")
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(120)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                padding: 0px 24px;
            }}
        """)

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
# USER PICKER DIALOG
# =========================================================

class UserPickerDialog(QDialog):

    def __init__(self, parent, complex_id, db):

        super().__init__(parent)

        self.complex_id = complex_id
        self.db = db
        self.selected_user = None
        self.user_cards = []
        self.users = []

        self.setModal(True)
        self.setWindowTitle("انتخاب کارمند")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumSize(500, 600)
        self.resize(520, 640)

        self.setObjectName("userPickerDialog")

        self.setup_ui()
        self.load_users()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 22, 22, 22)
        main_layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title = QLabel("انتخاب کارمند")
        title.setObjectName("pickerTitle")

        header_layout.addWidget(title)
        header_layout.addStretch()

        close_button = QPushButton("✕")
        close_button.setObjectName("pickerClose")
        close_button.setFixedSize(34, 34)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)

        header_layout.addWidget(close_button)

        main_layout.addLayout(header_layout)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("pickerSearch")
        self.search_input.setPlaceholderText("🔍  جستجوی نام یا شماره تلفن...")
        self.search_input.setFixedHeight(46)
        self.search_input.textChanged.connect(self.filter_users)

        main_layout.addWidget(self.search_input)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("pickerScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_bar = RoundScrollBar(Qt.Vertical)
        self.scroll.setVerticalScrollBar(scroll_bar)

        self.list_content = QWidget()
        self.list_content.setObjectName("pickerContent")
        self.list_content.setAttribute(Qt.WA_TranslucentBackground, True)

        self.list_layout = QVBoxLayout(self.list_content)
        self.list_layout.setContentsMargins(6, 6, 16, 6)
        self.list_layout.setSpacing(10)

        self.scroll.setWidget(self.list_content)

        main_layout.addWidget(self.scroll, 1)

        self.empty_label = QLabel(
            "کاربری برای افزودن وجود ندارد.\n"
            "همه‌ی کاربران یا عضو این مجموعه هستند،\n"
            "یا هنوز در سیستم ثبت‌نام نکرده‌اند."
        )
        self.empty_label.setObjectName("pickerEmpty")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.hide()

        main_layout.addWidget(self.empty_label)

        self.setStyleSheet("""

            QDialog#userPickerDialog {
                background-color: #F5F8FC;
            }

            QLabel#pickerTitle {
                color: #17324D;
                font-size: 20px;
                font-weight: 700;
                background: transparent;
            }

            QPushButton#pickerClose {
                background-color: #FFFFFF;
                color: #526273;
                border: 1px solid #DCE6F2;
                border-radius: 17px;
                font-size: 14px;
                font-weight: 700;
            }

            QPushButton#pickerClose:hover {
                background-color: #FEE2E2;
                color: #D93025;
                border-color: #FBD5D5;
            }

            QLineEdit#pickerSearch {
                background-color: #FFFFFF;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                padding: 0 16px;
                color: #17324D;
                font-size: 13px;
            }

            QLineEdit#pickerSearch:focus {
                border: 2px solid #4589E8;
            }

            QScrollArea#pickerScroll {
                background: transparent;
                border: none;
            }

            QScrollArea#pickerScroll > QWidget {
                background: transparent;
                border: none;
            }

            QWidget#pickerContent {
                background: transparent;
            }

            QFrame#userCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 16px;
            }

            QFrame#userCard:hover {
                background-color: #EAF3FF;
                border: 1px solid #4589E8;
            }

            QLabel#userAvatar {
                background-color: #EAF3FF;
                border: none;
                border-radius: 24px;
                color: #1961C7;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#userName {
                color: #17324D;
                font-size: 14px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#userInfo {
                color: #8290A1;
                font-size: 11px;
                background: transparent;
            }

            QLabel#pickerEmpty {
                color: #8290A1;
                font-size: 12px;
                background: transparent;
                padding: 20px;
            }

        """)

    def load_users(self):

        try:

            users = self.db.fetch_all(
                """
                SELECT
                    u.userId,
                    u.name,
                    u.profession,
                    u.phoneNumber,
                    u.nationalId,
                    u.imageBase64
                FROM users u
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM complex_members cm
                    WHERE cm.userId = u.userId
                      AND cm.complexId = %s
                )
                ORDER BY u.name ASC
                """,
                (self.complex_id,)
            )

            self.users = users or []

        except Exception as e:

            print("LOAD USERS ERROR:", e)
            self.users = []

        self.refresh_cards()

    def refresh_cards(self):

        for card in self.user_cards:
            card.deleteLater()

        self.user_cards.clear()

        while self.list_layout.count():

            item = self.list_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        if not self.users:

            self.empty_label.show()
            self.scroll.hide()
            return

        self.empty_label.hide()
        self.scroll.show()

        for user in self.users:

            card = self.create_user_card(user)
            self.list_layout.addWidget(card)
            self.user_cards.append(card)

        self.list_layout.addStretch()

    def create_user_card(self, user):

        card = QFrame()
        card.setObjectName("userCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setCursor(Qt.PointingHandCursor)
        card.setFixedHeight(72)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        avatar = QLabel()
        avatar.setObjectName("userAvatar")
        avatar.setFixedSize(48, 48)
        avatar.setAlignment(Qt.AlignCenter)

        name_text = user.get("name") or "?"
        first_letter = name_text[0] if name_text else "?"

        avatar.setText(first_letter)
        avatar.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout.addWidget(avatar)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(3)

        name_label = QLabel(name_text)
        name_label.setObjectName("userName")
        name_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        profession = user.get("profession") or "unknown"

        if profession == "unknown" or not profession:
            profession_display = "نامشخص"
        else:
            profession_display = profession

        phone = user.get("phoneNumber") or "-"

        info_label = QLabel(
            f"{profession_display}  •  {phone}"
        )
        info_label.setObjectName("userInfo")
        info_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        info_layout.addWidget(name_label)
        info_layout.addWidget(info_label)

        layout.addLayout(info_layout, 1)

        def select(event):
            self.selected_user = user
            self.accept()
            event.accept()

        card.mousePressEvent = select

        return card

    def filter_users(self, text):

        text = text.strip().lower()

        for user, card in zip(self.users, self.user_cards):

            if not text:
                card.show()
                continue

            name = (user.get("name") or "").lower()
            phone = (user.get("phoneNumber") or "").lower()
            profession = (user.get("profession") or "").lower()

            if (
                text in name
                or text in phone
                or text in profession
            ):
                card.show()
            else:
                card.hide()

# =========================================================
# ADD EMPLOYEES WINDOW
# =========================================================

class AddEmployees(QWidget):

    def __init__(self, parent_window=None, complex_id=None):
        super().__init__(parent_window)

        self.parent_window = parent_window
        self.complex_id = complex_id

        if self.complex_id is None and self.parent_window is not None:
            self.complex_id = getattr(
                self.parent_window,
                "complex_id",
                None
            )

        self.db = Database()

        # کاربر انتخاب‌شده
        self.selected_user = None

        # اسم مجموعه
        self.complex_name = "—"

        self.setWindowTitle("افزودن کارمند")
        self.resize(900, 700)
        self.setMinimumSize(600, 500)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("addEmployeesWindow")

        # ← اول اسم مجموعه رو بخون
        self.load_complex_name()

        self.setup_ui()

        # بعد از رندر، پاپ‌آپ انتخاب کاربر
        QTimer.singleShot(50, self.open_user_picker)

    # =========================================================
    # LOAD COMPLEX NAME
    # =========================================================

    def load_complex_name(self):

        self.complex_name = "—"

        if not self.complex_id:
            return

        try:

            row = self.db.fetch_one(
                """
                SELECT name
                FROM complexes
                WHERE complexId = %s
                LIMIT 1
                """,
                (self.complex_id,)
            )

            if row and row.get("name"):
                self.complex_name = row["name"]

        except Exception as e:
            print("LOAD COMPLEX NAME ERROR:", e)

    # =========================================================
    # UI
    # =========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(16)

        # =====================================================
        # HEADER
        # =====================================================

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("افزودن کارمند")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            f"افزودن کارمند به مجموعه: {self.complex_name}"
        )
        subtitle.setObjectName("pageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # =====================================================
        # SELECTED USER CARD
        # =====================================================

        self.user_card = QFrame()
        self.user_card.setObjectName("selectedUserCard")
        self.user_card.setAttribute(Qt.WA_StyledBackground, True)
        self.user_card.setFixedHeight(78)

        user_card_layout = QHBoxLayout(self.user_card)
        user_card_layout.setContentsMargins(18, 12, 18, 12)
        user_card_layout.setSpacing(14)

        self.selected_avatar = QLabel()
        self.selected_avatar.setObjectName("selectedAvatar")
        self.selected_avatar.setFixedSize(52, 52)
        self.selected_avatar.setAlignment(Qt.AlignCenter)

        user_card_layout.addWidget(self.selected_avatar)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(3)

        self.selected_name_label = QLabel("—")
        self.selected_name_label.setObjectName("selectedName")

        self.selected_info_label = QLabel("—")
        self.selected_info_label.setObjectName("selectedInfo")

        info_layout.addWidget(self.selected_name_label)
        info_layout.addWidget(self.selected_info_label)

        user_card_layout.addLayout(info_layout, 1)

        change_button = QPushButton("تغییر")
        change_button.setObjectName("changeUserButton")
        change_button.setFixedSize(70, 34)
        change_button.setCursor(Qt.PointingHandCursor)
        change_button.clicked.connect(self.open_user_picker)

        user_card_layout.addWidget(change_button)

        main_layout.addWidget(self.user_card)

        # =====================================================
        # FORM BOX
        # =====================================================

        form_box = QFrame()
        form_box.setObjectName("formBox")
        form_box.setAttribute(Qt.WA_StyledBackground, True)

        form_box_layout = QVBoxLayout(form_box)
        form_box_layout.setContentsMargins(18, 18, 18, 18)
        form_box_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("formScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_bar = RoundScrollBar(Qt.Vertical)
        scroll.setVerticalScrollBar(scroll_bar)

        content = QWidget()
        content.setObjectName("scrollContent")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(6, 6, 16, 6)
        content_layout.setSpacing(10)

        # =====================================================
        # JOB TITLE (با نام مجموعه)
        # =====================================================

        job_label = QLabel(
            f"شغل در مجموعه «{self.complex_name}»"
        )
        job_label.setObjectName("fieldLabel")

        self.job_input = QLineEdit()
        self.job_input.setObjectName("formInput")
        self.job_input.setPlaceholderText("مثلاً حسابدار ارشد")
        self.job_input.setFixedHeight(48)
        self.job_input.textChanged.connect(self.clear_job_error)

        self.job_error = QLabel()
        self.job_error.setObjectName("fieldError")
        self.job_error.setFixedHeight(20)
        self.job_error.setWordWrap(True)
        self.job_error.hide()

        content_layout.addWidget(job_label)
        content_layout.addWidget(self.job_input)
        content_layout.addWidget(self.job_error)

        # =====================================================
        # WORK TYPE
        # =====================================================

        work_type_label = QLabel("نوع همکاری")
        work_type_label.setObjectName("fieldLabel")

        self.work_type_combo = QComboBox()
        self.work_type_combo.setObjectName("formCombo")
        self.work_type_combo.addItems([
            "تمام‌وقت",
            "پاره‌وقت"
        ])
        self.work_type_combo.setFixedHeight(48)

        content_layout.addWidget(work_type_label)
        content_layout.addWidget(self.work_type_combo)

        # =====================================================
        # SALARY TYPE
        # =====================================================

        salary_type_label = QLabel("نوع حقوق")
        salary_type_label.setObjectName("fieldLabel")

        self.salary_type_combo = QComboBox()
        self.salary_type_combo.setObjectName("formCombo")
        self.salary_type_combo.addItems([
            "ماهانه",
            "روزانه",
            "ساعتی"
        ])
        self.salary_type_combo.setFixedHeight(48)

        content_layout.addWidget(salary_type_label)
        content_layout.addWidget(self.salary_type_combo)

        # =====================================================
        # SALARY
        # =====================================================

        salary_label = QLabel("مبلغ حقوق (تومان)")
        salary_label.setObjectName("fieldLabel")

        self.salary_input = QLineEdit()
        self.salary_input.setObjectName("formInput")
        self.salary_input.setPlaceholderText("مثلاً 20000000")
        self.salary_input.setFixedHeight(48)
        self.salary_input.setLayoutDirection(Qt.LeftToRight)
        self.salary_input.textChanged.connect(self.clear_salary_error)

        self.salary_error = QLabel()
        self.salary_error.setObjectName("fieldError")
        self.salary_error.setFixedHeight(20)
        self.salary_error.setWordWrap(True)
        self.salary_error.hide()

        content_layout.addWidget(salary_label)
        content_layout.addWidget(self.salary_input)
        content_layout.addWidget(self.salary_error)

        # =====================================================
        # WORK DAYS / HOURS
        # =====================================================

        work_info_layout = QHBoxLayout()
        work_info_layout.setSpacing(15)

        work_days_container = QVBoxLayout()
        work_days_container.setSpacing(6)

        work_days_label = QLabel("روز کاری در ماه")
        work_days_label.setObjectName("fieldLabel")

        self.work_days_input = QLineEdit()
        self.work_days_input.setObjectName("formInput")
        self.work_days_input.setPlaceholderText("26")
        self.work_days_input.setText("26")
        self.work_days_input.setFixedHeight(48)
        self.work_days_input.setLayoutDirection(Qt.LeftToRight)

        work_days_container.addWidget(work_days_label)
        work_days_container.addWidget(self.work_days_input)

        work_hours_container = QVBoxLayout()
        work_hours_container.setSpacing(6)

        work_hours_label = QLabel("ساعت کاری روزانه")
        work_hours_label.setObjectName("fieldLabel")

        self.work_hours_input = QLineEdit()
        self.work_hours_input.setObjectName("formInput")
        self.work_hours_input.setPlaceholderText("8")
        self.work_hours_input.setText("8")
        self.work_hours_input.setFixedHeight(48)
        self.work_hours_input.setLayoutDirection(Qt.LeftToRight)

        work_hours_container.addWidget(work_hours_label)
        work_hours_container.addWidget(self.work_hours_input)

        work_info_layout.addLayout(work_days_container)
        work_info_layout.addLayout(work_hours_container)

        content_layout.addLayout(work_info_layout)

        # =====================================================
        # START / END TIME
        # =====================================================

        time_layout = QHBoxLayout()
        time_layout.setSpacing(15)

        start_time_container = QVBoxLayout()
        start_time_container.setSpacing(6)

        start_time_label = QLabel("ساعت شروع")
        start_time_label.setObjectName("fieldLabel")

        self.start_time_input = QTimeEdit()
        self.start_time_input.setObjectName("formTime")
        self.start_time_input.setTime(QTime(8, 0))
        self.start_time_input.setDisplayFormat("HH:mm")
        self.start_time_input.setFixedHeight(48)
        self.start_time_input.setLayoutDirection(Qt.LeftToRight)

        start_time_container.addWidget(start_time_label)
        start_time_container.addWidget(self.start_time_input)

        end_time_container = QVBoxLayout()
        end_time_container.setSpacing(6)

        end_time_label = QLabel("ساعت پایان")
        end_time_label.setObjectName("fieldLabel")

        self.end_time_input = QTimeEdit()
        self.end_time_input.setObjectName("formTime")
        self.end_time_input.setTime(QTime(16, 0))
        self.end_time_input.setDisplayFormat("HH:mm")
        self.end_time_input.setFixedHeight(48)
        self.end_time_input.setLayoutDirection(Qt.LeftToRight)

        end_time_container.addWidget(end_time_label)
        end_time_container.addWidget(self.end_time_input)

        time_layout.addLayout(start_time_container)
        time_layout.addLayout(end_time_container)

        content_layout.addLayout(time_layout)

        # =====================================================
        # DESCRIPTION
        # =====================================================

        description_label = QLabel("توضیحات (اختیاری)")
        description_label.setObjectName("fieldLabel")

        self.description_input = QLineEdit()
        self.description_input.setObjectName("formInput")
        self.description_input.setPlaceholderText(
            "توضیحات مربوط به این کارمند"
        )
        self.description_input.setFixedHeight(48)

        content_layout.addWidget(description_label)
        content_layout.addWidget(self.description_input)

        content_layout.addStretch()

        scroll.setWidget(content)

        form_box_layout.addWidget(scroll)

        main_layout.addWidget(form_box, 1)

        # =====================================================
        # BUTTONS
        # =====================================================

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        cancel_button = QPushButton("انصراف")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setFixedHeight(50)
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.close)

        save_button = QPushButton("ذخیره کارمند")
        save_button.setObjectName("saveButton")
        save_button.setFixedHeight(50)
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.clicked.connect(self.save_employee)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

        # =====================================================
        # POLISH COMBO POPUPS
        # =====================================================

        self.polish_combo_popup(self.work_type_combo)
        self.polish_combo_popup(self.salary_type_combo)

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet("""

            QWidget#addEmployeesWindow {
                background-color: #F5F8FC;
            }

            QLabel#pageTitle {
                background: transparent;
                color: #17324D;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                background: transparent;
                color: #4589E8;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#fieldLabel {
                background: transparent;
                color: #526273;
                font-size: 13px;
                font-weight: 600;
                padding: 0px;
            }

            QLabel#fieldError {
                background: transparent;
                color: #D93025;
                font-size: 11px;
                font-weight: 600;
                padding: 0px;
                qproperty-alignment: 'AlignRight | AlignAbsolute | AlignVCenter';
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

            QFrame#selectedUserCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 18px;
            }

            QLabel#selectedAvatar {
                background-color: #EAF3FF;
                border: none;
                border-radius: 26px;
                color: #1961C7;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#selectedName {
                color: #17324D;
                font-size: 15px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#selectedInfo {
                color: #8290A1;
                font-size: 11px;
                background: transparent;
            }

            QPushButton#changeUserButton {
                background-color: #EAF3FF;
                color: #1961C7;
                border: 1px solid #C9DDF5;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#changeUserButton:hover {
                background-color: #D8E9FF;
            }

            QFrame#formBox {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 28px;
            }

            QScrollArea#formScroll {
                background: transparent;
                border: none;
            }

            QScrollArea#formScroll > QWidget {
                background: transparent;
                border: none;
            }

            QWidget#scrollContent {
                background: transparent;
                border: none;
            }

            QLineEdit#formInput,
            QTimeEdit#formTime {
                background: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                padding: 0 16px;
                color: #17324D;
                font-size: 13px;
            }

            QLineEdit#formInput:hover,
            QTimeEdit#formTime:hover {
                background: #FFFFFF;
                border: 1px solid #C9DDF5;
            }

            QLineEdit#formInput:focus,
            QTimeEdit#formTime:focus {
                background: #FFFFFF;
                border: 2px solid #4589E8;
            }

            QComboBox#formCombo {
                background: #F7F9FC;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                padding: 0 16px;
                padding-left: 40px;
                color: #17324D;
                font-size: 13px;
            }

            QComboBox#formCombo:hover {
                background: #FFFFFF;
                border: 1px solid #C9DDF5;
            }

            QComboBox#formCombo:focus {
                background: #FFFFFF;
                border: 2px solid #4589E8;
            }

            QComboBox#formCombo::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center left;
                width: 32px;
                border: none;
                background: transparent;
            }

            QComboBox#formCombo::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 7px solid #4589E8;
                margin-left: 14px;
                margin-right: 0px;
            }

            QTimeEdit#formTime::up-button,
            QTimeEdit#formTime::down-button {
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }

            QPushButton#saveButton {
                background: #1961C7;
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 700;
                padding: 0 28px;
            }

            QPushButton#saveButton:hover {
                background: #4589E8;
            }

            QPushButton#saveButton:pressed {
                background: #1453AA;
            }

            QPushButton#cancelButton {
                background: #FFFFFF;
                color: #526273;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 28px;
            }

            QPushButton#cancelButton:hover {
                background: #EAF3FF;
                color: #1961C7;
                border-color: #C9DDF5;
            }

        """)

    # =========================================================
    # OPEN USER PICKER
    # =========================================================

    def open_user_picker(self):

        picker = UserPickerDialog(
            self,
            self.complex_id,
            self.db
        )

        result = picker.exec()

        if result == QDialog.Accepted and picker.selected_user:

            self.selected_user = picker.selected_user
            self.update_selected_user_card()

    # =========================================================
    # UPDATE SELECTED USER CARD
    # =========================================================

    def update_selected_user_card(self):

        if not self.selected_user:
            return

        user = self.selected_user

        name = user.get("name") or "?"
        first_letter = name[0] if name else "?"

        self.selected_avatar.setText(first_letter)

        self.selected_name_label.setText(name)

        profession = user.get("profession") or "unknown"

        if profession == "unknown" or not profession:
            profession_display = "نامشخص"
        else:
            profession_display = profession

        phone = user.get("phoneNumber") or "-"

        self.selected_info_label.setText(
            f"{profession_display}  •  {phone}"
        )

    # =========================================================
    # POLISH COMBO POPUP
    # =========================================================

    def polish_combo_popup(self, combo):

        view = combo.view()

        view.setStyleSheet("""
            QAbstractItemView {
                background: white;
                border: 1px solid #DCE6F2;
                border-radius: 14px;
                padding: 6px;
                outline: 0;
                color: #17324D;
                font-size: 13px;
                selection-background-color: #EAF3FF;
                selection-color: #1961C7;
            }

            QAbstractItemView::item {
                min-height: 34px;
                border-radius: 10px;
                padding: 0 10px;
                margin: 2px 2px;
            }

            QAbstractItemView::item:hover {
                background-color: #EAF3FF;
                color: #1961C7;
            }

            QAbstractItemView::item:selected {
                background-color: #EAF3FF;
                color: #1961C7;
            }
        """)

        popup_window = view.window()

        if popup_window is not None:

            popup_window.setAttribute(
                Qt.WA_TranslucentBackground, True
            )

            popup_window.setWindowFlags(
                Qt.Popup
                | Qt.FramelessWindowHint
                | Qt.NoDropShadowWindowHint
            )

            popup_window.setStyleSheet("""
                background: transparent;
            """)

    # =========================================================
    # ERROR HELPERS
    # =========================================================

    def show_error(self, label, message):

        label.setText(message)
        label.setAlignment(
            Qt.AlignRight | Qt.AlignAbsolute | Qt.AlignVCenter
        )
        label.show()

    def clear_error(self, label):

        label.clear()
        label.hide()

    def clear_job_error(self):
        self.clear_error(self.job_error)

    def clear_salary_error(self):
        self.clear_error(self.salary_error)

    def contains_digit(self, text):

        for c in text:
            if c.isdigit():
                return True
        return False

    # =========================================================
    # SAVE
    # =========================================================

    def save_employee(self):

        if not self.selected_user:

            NiceMessageBox.warning(
                self,
                "خطا",
                "لطفاً یک کارمند انتخاب کنید."
            )

            self.open_user_picker()
            return

        job = self.job_input.text().strip()
        salary_text = self.salary_input.text().strip()

        work_type = self.work_type_combo.currentText()
        salary_type = self.salary_type_combo.currentText()

        work_days_text = self.work_days_input.text().strip()
        work_hours_text = self.work_hours_input.text().strip()
        description_text = self.description_input.text().strip()

        # =====================================================
        # JOB VALIDATION
        # =====================================================

        self.clear_error(self.job_error)

        if not job:

            self.show_error(
                self.job_error,
                "لطفاً شغل را وارد کنید."
            )

            self.job_input.setFocus()
            return

        if self.contains_digit(job):

            self.show_error(
                self.job_error,
                "شغل نباید شامل عدد باشد."
            )

            self.job_input.setFocus()
            return

        # =====================================================
        # SALARY VALIDATION
        # =====================================================

        self.clear_error(self.salary_error)

        if not salary_text:

            self.show_error(
                self.salary_error,
                "لطفاً مبلغ حقوق را وارد کنید."
            )

            self.salary_input.setFocus()
            return

        try:

            salary = float(
                salary_text.replace(",", "").replace("٬", "")
            )

        except ValueError:

            self.show_error(
                self.salary_error,
                "مبلغ حقوق صحیح نیست."
            )

            self.salary_input.setFocus()
            return

        MAX_SALARY = 999_999_999_999_999

        if salary <= 0:

            self.show_error(
                self.salary_error,
                "مبلغ حقوق باید بیشتر از صفر باشد."
            )

            self.salary_input.setFocus()
            return

        if salary > MAX_SALARY:

            self.show_error(
                self.salary_error,
                "مبلغ حقوق بیش از حد بزرگ است."
            )

            self.salary_input.setFocus()
            return

        # =====================================================
        # WORK DAYS / HOURS
        # =====================================================

        try:
            work_days = int(work_days_text) if work_days_text else 26
        except ValueError:
            work_days = 26

        try:
            work_hours = float(work_hours_text) if work_hours_text else 8
        except ValueError:
            work_hours = 8

        # =====================================================
        # COMPLEX
        # =====================================================

        if not self.complex_id:

            NiceMessageBox.warning(
                self,
                "خطا",
                "مجموعه فعلی مشخص نیست."
            )
            return

        # =====================================================
        # PREPARE DATA
        # =====================================================

        user = self.selected_user
        user_id = user["userId"]

        national_code = user.get("nationalId") or None

        if work_type == "تمام‌وقت":
            employment_type = "fullTime"
        else:
            employment_type = "partTime"

        if salary_type == "ماهانه":
            salary_type_db = "monthly"
        elif salary_type == "روزانه":
            salary_type_db = "daily"
        else:
            salary_type_db = "hourly"

        start_time = self.start_time_input.time().toString("HH:mm:ss")
        end_time = self.end_time_input.time().toString("HH:mm:ss")

        # =====================================================
        # INSERT MEMBER
        # =====================================================

        member_id = self.db.execute(
            """
            INSERT INTO complex_members (
                complexId,
                userId,
                role,
                joinedDate,
                isActive
            )
            VALUES (%s, %s, 'employee', %s, '1')
            """,
            (
                self.complex_id,
                user_id,
                datetime.now()
            )
        )

        if not member_id:

            NiceMessageBox.error(
                self,
                "خطا",
                "افزودن کارمند به مجموعه انجام نشد."
            )
            return

        # =====================================================
        # INSERT PROFILE
        # =====================================================

        profile_id = self.db.execute(
            """
            INSERT INTO employee_profiles (
                memberId,
                jobTitle,
                nationalCode,
                employmentType,
                salaryType,
                baseSalary,
                workDays,
                workHours,
                workStartTime,
                workEndTime,
                description,
                createdDate
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            """,
            (
                member_id,
                job,
                national_code,
                employment_type,
                salary_type_db,
                salary,
                work_days,
                work_hours,
                start_time,
                end_time,
                description_text or None,
                datetime.now()
            )
        )

        if not profile_id:

            self.db.execute(
                "DELETE FROM complex_members WHERE memberId = %s",
                (member_id,)
            )

            NiceMessageBox.error(
                self,
                "خطا",
                "اطلاعات پروفایل کارمند ذخیره نشد."
            )
            return

        # =====================================================
        # REFRESH PARENT
        # =====================================================

        if self.parent_window is not None:

            if hasattr(self.parent_window, "load_employees_from_database"):
                self.parent_window.load_employees_from_database()

            elif hasattr(self.parent_window, "refresh_employees"):
                self.parent_window.refresh_employees()

        # =====================================================
        # SUCCESS msg
        # =====================================================

        NiceMessageBox.success(
            self,
            "ثبت موفق",
            f"{user.get('name', 'کارمند')} به مجموعه "
            f"«{self.complex_name}» اضافه شد."
        )

        self.close()