from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QScrollArea,
    QBoxLayout
)

from PySide6.QtCore import Qt, QTimer, QTime

class AttendanceWindow(QWidget):

    def __init__(self, phone_number):

        super().__init__()

        self.phone_number = phone_number

        # ==============================
        # زمان کاری
        # ==============================

        self.work_start = QTime(8, 0, 0)
        self.work_end = QTime(16, 0, 0)

        self.entry_time = None
        self.exit_time = None

        # ==============================
        # Window
        # ==============================

        self.setWindowTitle("حضور و غیاب")
        self.resize(980, 640)

        self.setLayoutDirection(
            Qt.RightToLeft
        )

        self.setStyleSheet("""
            QWidget {
                font-family: Vazirmatn;
            }

            QLabel {
                color: #18324D;
            }
        """)

        self.setup_ui()

        # ==============================
        # ساعت زنده
        # ==============================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_clock
        )

        self.timer.start(1000)

        self.update_clock()

    # =========================================================
    # UI
    # =========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            22, 15, 22, 15
        )

        main_layout.setSpacing(10)

        # =====================================================
        # Header
        # =====================================================

        header = QHBoxLayout()
        header.setSpacing(8)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(7)

        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(1)

        title = QLabel(
            "حضور و غیاب"
        )

        title.setStyleSheet("""
            font-size: 21px;
            font-weight: 700;
            color: #17324D;
        """)

        subtitle = QLabel(
            "مدیریت ورود، خروج و ساعات کاری"
        )

        subtitle.setStyleSheet("""
            font-size: 10px;
            color: #7890A8;
        """)

        title_text_layout.addWidget(
            title
        )

        title_text_layout.addWidget(
            subtitle
        )

        # فلش کنار عنوان
        back_button = QPushButton("›")

        back_button.setFixedSize(
            36, 36
        )

        back_button.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                color: #1961C7;
                font-size: 24px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #EAF3FF;
            }
        """)

        back_button.clicked.connect(
            self.close
        )

        # فلش سمت راست و عنوان سمت چپ آن
        title_layout.setDirection(
            QBoxLayout.LeftToRight
        )

        title_layout.addWidget(
            back_button
        )

        title_layout.addLayout(
            title_text_layout
        )

        header.addLayout(
            title_layout
        )

        header.addStretch()

        main_layout.addLayout(
            header
        )

        # =====================================================
        # Top Cards
        # =====================================================

        top_cards = QHBoxLayout()
        top_cards.setSpacing(9)

        self.clock_card = self.create_info_card(
            "ساعت فعلی",
            "00:00:00"
        )

        self.clock_value = (
            self.clock_card.findChild(
                QLabel,
                "value"
            )
        )

        self.status_card = self.create_info_card(
            "وضعیت امروز",
            "ثبت نشده"
        )

        self.status_value = (
            self.status_card.findChild(
                QLabel,
                "value"
            )
        )

        top_cards.addWidget(
            self.clock_card
        )

        top_cards.addWidget(
            self.status_card
        )

        main_layout.addLayout(
            top_cards
        )

        # =====================================================
        # Today Card
        # =====================================================

        today_card = QFrame()

        today_card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 19px;
            }
        """)

        today_layout = QVBoxLayout(
            today_card
        )

        today_layout.setContentsMargins(
            16, 12, 16, 12
        )

        today_layout.setSpacing(8)

        today_title = QLabel(
            "وضعیت امروز"
        )

        today_title.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #17324D;
        """)

        today_layout.addWidget(
            today_title
        )

        # =====================================================
        # ورود / خروج / مدت کار
        # =====================================================

        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)

        self.entry_box = self.create_time_box(
            "ورود"
        )

        self.exit_box = self.create_time_box(
            "خروج"
        )

        self.work_box = self.create_time_box(
            "مدت کار"
        )

        info_layout.addWidget(
            self.entry_box
        )

        info_layout.addWidget(
            self.exit_box
        )

        info_layout.addWidget(
            self.work_box
        )

        today_layout.addLayout(
            info_layout
        )

        # =====================================================
        # محاسبات
        # =====================================================

        calculation_layout = QHBoxLayout()
        calculation_layout.setSpacing(8)

        self.delay_box = self.create_small_box(
            "تأخیر",
            "۰ دقیقه"
        )

        self.overtime_box = self.create_small_box(
            "اضافه‌کاری",
            "۰ دقیقه"
        )

        self.remaining_box = self.create_small_box(
            "باقی‌مانده کار",
            "۸ ساعت"
        )

        calculation_layout.addWidget(
            self.delay_box
        )

        calculation_layout.addWidget(
            self.overtime_box
        )

        calculation_layout.addWidget(
            self.remaining_box
        )

        today_layout.addLayout(
            calculation_layout
        )

        # =====================================================
        # Buttons
        # =====================================================

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.entry_button = QPushButton(
            "ثبت ورود"
        )

        self.exit_button = QPushButton(
            "ثبت خروج"
        )

        self.entry_button.setFixedHeight(
            37
        )

        self.exit_button.setFixedHeight(
            37
        )

        self.entry_button.setStyleSheet("""
            QPushButton {
                background: #1961C7;
                color: white;
                border: none;
                border-radius: 11px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #1454AE;
            }

            QPushButton:disabled {
                background: #B8C9DD;
            }
        """)

        self.exit_button.setStyleSheet("""
            QPushButton {
                background: #4589E8;
                color: white;
                border: none;
                border-radius: 11px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #3678D5;
            }

            QPushButton:disabled {
                background: #B8C9DD;
            }
        """)

        self.entry_button.clicked.connect(
            self.register_entry
        )

        self.exit_button.clicked.connect(
            self.register_exit
        )

        buttons_layout.addWidget(
            self.entry_button
        )

        buttons_layout.addWidget(
            self.exit_button
        )

        today_layout.addLayout(
            buttons_layout
        )

        main_layout.addWidget(
            today_card
        )

        # =====================================================
        # History Title
        # =====================================================

        history_title = QLabel(
            "سوابق حضور و غیاب"
        )

        history_title.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #17324D;
        """)

        main_layout.addWidget(
            history_title
        )

        # =====================================================
        # Search
        # =====================================================

        self.search_box = QLineEdit()

        self.search_box.setPlaceholderText(
            "جستجو در سوابق..."
        )

        self.search_box.setFixedHeight(
            36
        )

        self.search_box.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 11px;
                padding: 0 12px;
                font-size: 11px;
                color: #17324D;
            }

            QLineEdit:focus {
                border: 1px solid #4589E8;
            }
        """)

        main_layout.addWidget(
            self.search_box
        )

        # =====================================================
        # History Scroll
        # =====================================================

        history_scroll_layout = QHBoxLayout()

        # فاصله بیشتر از اسکرول‌بار
        history_scroll_layout.setContentsMargins(
            50, 0, 0, 0
        )

        self.history_scroll = QScrollArea()

        self.history_scroll.setWidgetResizable(
            True
        )

        self.history_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.history_scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.history_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                width: 12px;
                background: #E8EEF6;
                border-radius: 6px;
                margin: 20px 0 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: #4589E8;
                border-radius: 6px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #1961C7;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        history_container = QWidget()

        self.history_layout = QVBoxLayout(
            history_container
        )

        self.history_layout.setContentsMargins(
            20, 0, 12, 0
        )

        self.history_layout.setSpacing(
            7
        )

        self.history_scroll.setWidget(
            history_container
        )

        history_scroll_layout.addWidget(
            self.history_scroll
        )

        main_layout.addLayout(
            history_scroll_layout,
            1
        )

        # =====================================================
        # نمونه سوابق
        # =====================================================

        self.add_history_row(
            "شنبه ۶ مهر",
            "08:12",
            "16:25",
            "8 ساعت و 13 دقیقه",
            "حاضر"
        )

        self.add_history_row(
            "جمعه ۵ مهر",
            "08:35",
            "16:10",
            "7 ساعت و 35 دقیقه",
            "تأخیر"
        )

        self.add_history_row(
            "پنجشنبه ۴ مهر",
            "08:05",
            "16:20",
            "8 ساعت و 15 دقیقه",
            "حاضر"
        )

        self.add_history_row(
            "چهارشنبه ۳ مهر",
            "—",
            "—",
            "—",
            "غیبت"
        )

        self.add_history_row(
            "سه‌شنبه ۲ مهر",
            "08:15",
            "16:30",
            "8 ساعت و 15 دقیقه",
            "حاضر"
        )

        self.add_history_row(
            "دوشنبه ۱ مهر",
            "08:40",
            "16:10",
            "7 ساعت و 30 دقیقه",
            "تأخیر"
        )

    # =========================================================
    # Info Card
    # =========================================================

    def create_info_card(
        self,
        title_text,
        value_text
    ):

        card = QFrame()

        card.setMinimumHeight(
            66
        )

        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            15, 8, 15, 8
        )

        title = QLabel(
            title_text
        )

        title.setStyleSheet("""
            color: #7890A8;
            font-size: 10px;
        """)

        value = QLabel(
            value_text
        )

        value.setObjectName(
            "value"
        )

        value.setStyleSheet("""
            color: #1961C7;
            font-size: 17px;
            font-weight: 700;
        """)

        layout.addWidget(
            title
        )

        layout.addWidget(
            value
        )

        return card

    # =========================================================
    # Time Box
    # =========================================================

    def create_time_box(
        self,
        title_text
    ):

        box = QFrame()

        box.setMinimumHeight(
            58
        )

        box.setStyleSheet("""
            QFrame {
                background: #F5F8FC;
                border-radius: 12px;
                border: 1px solid #E8EEF5;
            }
        """)

        layout = QVBoxLayout(
            box
        )

        layout.setContentsMargins(
            11, 6, 11, 6
        )

        title = QLabel(
            title_text
        )

        title.setStyleSheet("""
            color: #7890A8;
            font-size: 9px;
        """)

        value = QLabel(
            "—"
        )

        value.setObjectName(
            "time_value"
        )

        value.setStyleSheet("""
            color: #17324D;
            font-size: 16px;
            font-weight: 700;
        """)

        layout.addWidget(
            title
        )

        layout.addWidget(
            value
        )

        return box

    # =========================================================
    # Small Box
    # =========================================================

    def create_small_box(
        self,
        title_text,
        value_text
    ):

        box = QFrame()

        box.setMinimumHeight(
            49
        )

        box.setStyleSheet("""
            QFrame {
                background: #F8FAFD;
                border: 1px solid #E8EEF5;
                border-radius: 11px;
            }
        """)

        layout = QVBoxLayout(
            box
        )

        layout.setContentsMargins(
            11, 5, 11, 5
        )

        title = QLabel(
            title_text
        )

        title.setStyleSheet("""
            color: #7890A8;
            font-size: 9px;
        """)

        value = QLabel(
            value_text
        )

        value.setObjectName(
            "small_value"
        )

        value.setStyleSheet("""
            color: #1961C7;
            font-size: 11px;
            font-weight: 700;
        """)

        layout.addWidget(
            title
        )

        layout.addWidget(
            value
        )

        return box

    # =========================================================
    # Clock
    # =========================================================

    def update_clock(self):

        now = QTime.currentTime()

        self.clock_value.setText(
            now.toString("HH:mm:ss")
        )

        if self.entry_time and not self.exit_time:

            self.update_live_calculations()

    # =========================================================
    # زمان ثبت‌شده بدون ثانیه
    # =========================================================

    def current_minute_time(self):

        now = QTime.currentTime()

        return QTime(
            now.hour(),
            now.minute(),
            0
        )

    # =========================================================
    # ثبت ورود
    # =========================================================

    def register_entry(self):

        # فقط ساعت و دقیقه ذخیره می‌شود
        self.entry_time = (
            self.current_minute_time()
        )

        self.exit_time = None

        self.entry_box.findChild(
            QLabel,
            "time_value"
        ).setText(
            self.entry_time.toString(
                "HH:mm"
            )
        )

        self.exit_box.findChild(
            QLabel,
            "time_value"
        ).setText(
            "—"
        )

        self.work_box.findChild(
            QLabel,
            "time_value"
        ).setText(
            "۰ دقیقه"
        )

        self.calculate_delay()

        self.overtime_box.findChild(
            QLabel,
            "small_value"
        ).setText(
            "۰ دقیقه"
        )

        self.remaining_box.findChild(
            QLabel,
            "small_value"
        ).setText(
            "در حال محاسبه"
        )

        self.status_value.setText(
            self.calculate_status()
        )

        self.entry_button.setEnabled(
            False
        )

        self.exit_button.setEnabled(
            True
        )

    # =========================================================
    # ثبت خروج
    # =========================================================

    def register_exit(self):

        if not self.entry_time:
            return

        # فقط ساعت و دقیقه
        current_time = (
            self.current_minute_time()
        )

        if current_time < self.entry_time:
            return

        self.exit_time = current_time

        self.exit_box.findChild(
            QLabel,
            "time_value"
        ).setText(
            self.exit_time.toString(
                "HH:mm"
            )
        )

        self.calculate_work_time()

        self.calculate_overtime()

        self.calculate_remaining_work()

        self.status_value.setText(
            self.calculate_status()
        )

        self.exit_button.setEnabled(
            False
        )

    # =========================================================
    # محاسبه مدت کار
    # =========================================================

    def calculate_work_time(self):

        if not self.entry_time or not self.exit_time:
            return

        seconds = self.entry_time.secsTo(
            self.exit_time
        )

        hours = seconds // 3600

        minutes = (
            seconds % 3600
        ) // 60

        self.work_box.findChild(
            QLabel,
            "time_value"
        ).setText(
            self.format_duration(
                hours,
                minutes
            )
        )

    # =========================================================
    # محاسبه زنده
    # =========================================================

    def update_live_calculations(self):

        if not self.entry_time:
            return

        current = self.current_minute_time()

        seconds = self.entry_time.secsTo(
            current
        )

        hours = seconds // 3600

        minutes = (
            seconds % 3600
        ) // 60

        self.work_box.findChild(
            QLabel,
            "time_value"
        ).setText(
            self.format_duration(
                hours,
                minutes
            )
        )

        self.calculate_delay()

        self.calculate_overtime()

        self.calculate_remaining_work()

    # =========================================================
    # تأخیر
    # =========================================================

    def calculate_delay(self):

        if not self.entry_time:
            return

        delay_seconds = self.work_start.secsTo(
            self.entry_time
        )

        if delay_seconds <= 0:

            text = "۰ دقیقه"

        else:

            minutes = delay_seconds // 60

            hours = minutes // 60

            minutes = minutes % 60

            if hours > 0:

                text = (
                    f"{hours} ساعت و "
                    f"{minutes} دقیقه"
                )

            else:

                text = f"{minutes} دقیقه"

        self.delay_box.findChild(
            QLabel,
            "small_value"
        ).setText(
            text
        )

    # =========================================================
    # اضافه کاری
    # =========================================================

    def calculate_overtime(self):

        if not self.entry_time:
            return

        current_time = (
            self.exit_time
            if self.exit_time
            else self.current_minute_time()
        )

        overtime_seconds = self.work_end.secsTo(
            current_time
        )

        if overtime_seconds <= 0:

            text = "۰ دقیقه"

        else:

            minutes = overtime_seconds // 60

            hours = minutes // 60

            minutes = minutes % 60

            if hours > 0:

                text = (
                    f"{hours} ساعت و "
                    f"{minutes} دقیقه"
                )

            else:

                text = f"{minutes} دقیقه"

        self.overtime_box.findChild(
            QLabel,
            "small_value"
        ).setText(
            text
        )

    # =========================================================
    # باقی مانده کار
    # =========================================================

    def calculate_remaining_work(self):

        if not self.entry_time:
            return

        current_time = (
            self.exit_time
            if self.exit_time
            else self.current_minute_time()
        )

        required_seconds = (
            self.work_start.secsTo(
                self.work_end
            )
        )

        worked_seconds = (
            self.entry_time.secsTo(
                current_time
            )
        )

        remaining = (
            required_seconds
            - worked_seconds
        )

        if remaining <= 0:

            text = "تکمیل شده"

        else:

            hours = remaining // 3600

            minutes = (
                remaining % 3600
            ) // 60

            text = (
                f"{hours} ساعت و "
                f"{minutes} دقیقه"
            )

        self.remaining_box.findChild(
            QLabel,
            "small_value"
        ).setText(
            text
        )

    # =========================================================
    # وضعیت
    # =========================================================

    def calculate_status(self):

        if not self.entry_time:
            return "غیبت"

        if self.entry_time > self.work_start:
            return "تأخیر"

        return "حاضر"

    # =========================================================
    # فرمت مدت
    # =========================================================

    def format_duration(
        self,
        hours,
        minutes
    ):

        if hours == 0:
            return f"{minutes} دقیقه"

        if minutes == 0:
            return f"{hours} ساعت"

        return (
            f"{hours} ساعت و "
            f"{minutes} دقیقه"
        )

    # =========================================================
    # History Row
    # =========================================================

    def add_history_row(
        self,
        date_text,
        entry_text,
        exit_text,
        duration_text,
        status_text
    ):

        row = QFrame()

        row.setMinimumHeight(
            51
        )

        row.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 12px;
            }
        """)

        layout = QHBoxLayout(
            row
        )

        layout.setContentsMargins(
            13, 5, 13, 5
        )

        layout.setSpacing(10)

        date_label = QLabel(
            date_text
        )

        date_label.setStyleSheet("""
            color: #17324D;
            font-size: 11px;
            font-weight: 600;
        """)

        entry_label = QLabel(
            f"ورود: {entry_text}"
        )

        exit_label = QLabel(
            f"خروج: {exit_text}"
        )

        duration_label = QLabel(
            duration_text
        )

        entry_label.setStyleSheet("""
            color: #607D96;
            font-size: 11px;
        """)

        exit_label.setStyleSheet("""
            color: #607D96;
            font-size: 11px;
        """)

        duration_label.setStyleSheet("""
            color: #1961C7;
            font-size: 11px;
            font-weight: 600;
        """)

        status_label = QLabel(
            status_text
        )

        status_label.setAlignment(
            Qt.AlignCenter
        )

        status_label.setMinimumWidth(
            60
        )

        if status_text == "حاضر":

            status_style = """
                QLabel {
                    background: #EAF6EE;
                    color: #21844A;
                    border-radius: 8px;
                    padding: 3px 7px;
                    font-size: 10px;
                    font-weight: 600;
                }
            """

        elif status_text == "تأخیر":

            status_style = """
                QLabel {
                    background: #FFF4DD;
                    color: #B87900;
                    border-radius: 8px;
                    padding: 3px 7px;
                    font-size: 10px;
                    font-weight: 600;
                }
            """

        else:

            status_style = """
                QLabel {
                    background: #FDEBEC;
                    color: #C43D4B;
                    border-radius: 8px;
                    padding: 3px 7px;
                    font-size: 10px;
                    font-weight: 600;
                }
            """

        status_label.setStyleSheet(
            status_style
        )

        layout.addWidget(
            date_label,
            2
        )

        layout.addWidget(
            entry_label,
            1
        )

        layout.addWidget(
            exit_label,
            1
        )

        layout.addWidget(
            duration_label,
            1
        )

        layout.addWidget(
            status_label
        )

        self.history_layout.addWidget(
            row
        )