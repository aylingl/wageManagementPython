import os

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea
)

from PySide6.QtCore import Qt

class EventsWindow(QWidget):

    def __init__(self, parent_window=None):

        # =================================================
        # IMPORTANT:
        # EventsWindow must be an independent window.
        # Do not pass parent to QWidget.
        # =================================================

        super().__init__()

        self.parent_window = parent_window

        self.setWindowTitle(
            "رویدادها و سوابق"
        )

        self.setMinimumSize(
            900,
            620
        )

        self.setLayoutDirection(
            Qt.RightToLeft
        )

        # =================================================
        # RECORDS
        # =================================================

        self.records = [

            {
                "type": "پرداخت حقوق",
                "category": "پرداخت",
                "employee": "علی رضایی",
                "description": "۲۵,۰۰۰,۰۰۰ تومان",
                "date": "۱۴۰۵/۰۷/۰۵ - ۱۰:۳۰"
            },

            {
                "type": "اصلاح حضور و غیاب",
                "category": "حضور و غیاب",
                "employee": "سارا محمدی",
                "description": "ساعت ورود از ۸:۱۰ به ۸:۰۰ اصلاح شد",
                "date": "۱۴۰۵/۰۷/۰۶ - ۰۹:۱۵"
            },

            {
                "type": "اضافه‌کاری",
                "category": "سایر",
                "employee": "محمد احمدی",
                "description": "۲ ساعت اضافه‌کاری ثبت شد",
                "date": "۱۴۰۵/۰۷/۰۷ - ۱۶:۴۰"
            },

            {
                "type": "پرداخت وام",
                "category": "وام",
                "employee": "علی رضایی",
                "description": "۱۰,۰۰۰,۰۰۰ تومان وام پرداخت شد",
                "date": "۱۴۰۵/۰۷/۰۸ - ۱۲:۲۰"
            },

            {
                "type": "تأیید حضور و غیاب",
                "category": "حضور و غیاب",
                "employee": "علی رضایی",
                "description": "ورود ۰۸:۰۰ - خروج ۱۶:۰۰",
                "date": "۱۴۰۵/۰۷/۰۹ - ۱۶:۱۵"
            },

            {
                "type": "تأیید مرخصی",
                "category": "مرخصی",
                "employee": "سارا محمدی",
                "description": "مرخصی روز ۱۴۰۵/۰۷/۱۰ تأیید شد",
                "date": "۱۴۰۵/۰۷/۰۹ - ۱۱:۲۰"
            },

            {
                "type": "درخواست وام",
                "category": "وام",
                "employee": "محمد احمدی",
                "description": "درخواست وام به مبلغ ۵,۰۰۰,۰۰۰ تومان ثبت شد",
                "date": "۱۴۰۵/۰۷/۱۰ - ۰۹:۴۵"
            }

        ]

        self.current_filter = "همه"

        self.setup_ui()

    # =================================================
    # SETUP UI
    # =================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        main_layout.setSpacing(
            20
        )

        # =================================================
        # HEADER
        # =================================================

        header_layout = QHBoxLayout()

        header_layout.setSpacing(
            12
        )

        # =================================================
        # BACK BUTTON
        # =================================================

        back_button = QPushButton(
            "›"
           
        )

        back_button.setObjectName(
            "backButton"
        )

        back_button.setFixedSize(
            42,
            42
        )

        back_button.setCursor(
            Qt.PointingHandCursor
        )

        back_button.clicked.connect(
            self.close
        )

        header_layout.addWidget(
            back_button
        )

        # =================================================
        # TITLE
        # =================================================

        title_layout = QVBoxLayout()

        title_layout.setSpacing(
            3
        )

        title = QLabel(
            "رویدادها و سوابق"
        )

        title.setObjectName(
            "title"
        )

        subtitle = QLabel(
            "ثبت و نگهداری سوابق فعالیت‌های سیستم"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        header_layout.addLayout(
            title_layout
        )

        header_layout.addStretch()

        main_layout.addLayout(
            header_layout
        )

        # =================================================
        # FILTER BOX
        # =================================================

        filter_box = QFrame()

        filter_box.setObjectName(
            "filterBox"
        )

        filter_layout = QHBoxLayout(
            filter_box
        )

        filter_layout.setContentsMargins(
            14,
            12,
            14,
            12
        )

        filter_layout.setSpacing(
            7
        )

        filter_label = QLabel(
            "نمایش سوابق:"
        )

        filter_label.setObjectName(
            "filterLabel"
        )

        filter_layout.addWidget(
            filter_label
        )

        # =================================================
        # FILTER BUTTONS
        # =================================================

        self.all_button = QPushButton(
            "همه"
        )

        self.payment_button = QPushButton(
            "پرداخت‌ها"
        )

        self.attendance_button = QPushButton(
            "حضور و غیاب"
        )

        self.leave_button = QPushButton(
            "مرخصی‌ها"
        )

        self.loan_button = QPushButton(
            "وام‌ها"
        )

        self.other_button = QPushButton(
            "سایر موارد"
        )

        self.filter_buttons = [

            self.all_button,
            self.payment_button,
            self.attendance_button,
            self.leave_button,
            self.loan_button,
            self.other_button

        ]

        for button in self.filter_buttons:

            button.setObjectName(
                "filterButton"
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            filter_layout.addWidget(
                button
            )

        self.all_button.clicked.connect(
            lambda: self.change_filter(
                "همه"
            )
        )

        self.payment_button.clicked.connect(
            lambda: self.change_filter(
                "پرداخت"
            )
        )

        self.attendance_button.clicked.connect(
            lambda: self.change_filter(
                "حضور و غیاب"
            )
        )

        self.leave_button.clicked.connect(
            lambda: self.change_filter(
                "مرخصی"
            )
        )

        self.loan_button.clicked.connect(
            lambda: self.change_filter(
                "وام"
            )
        )

        self.other_button.clicked.connect(
            lambda: self.change_filter(
                "سایر"
            )
        )

        filter_layout.addStretch()

        main_layout.addWidget(
            filter_box
        )

        # =================================================
        # RECORDS BOX
        # =================================================

        records_box = QFrame()

        records_box.setObjectName(
            "recordsBox"
        )

        records_layout = QVBoxLayout(
            records_box
        )

        records_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        records_layout.setSpacing(
            12
        )

        # =================================================
        # RECORDS TITLE
        # =================================================

        records_title = QLabel(
            "سوابق ثبت‌شده"
        )

        records_title.setObjectName(
            "sectionTitle"
        )

        records_layout.addWidget(
            records_title
        )

        # =================================================
        # SCROLL
        # =================================================

        self.scroll = QScrollArea()

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
            Qt.ScrollBarAsNeeded
        )

        scroll_content = QWidget()

        scroll_content.setObjectName(
            "scrollContent"
        )

        self.scroll_layout = QVBoxLayout(
            scroll_content
        )

        self.scroll_layout.setSpacing(
            10
        )

        self.scroll_layout.setContentsMargins(
            6,
            6,
            11,
            6
        )

        self.scroll.setWidget(
            scroll_content
        )

        records_layout.addWidget(
            self.scroll
        )

        main_layout.addWidget(
            records_box
        )

        # =================================================
        # LOAD RECORDS
        # =================================================

        self.refresh_records()

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet("""

        QWidget {
            background-color: #F5F8FC;
            font-family: Vazirmatn;
        }

        QLabel#title {
            color: #1E2F43;
            font-size: 24px;
            font-weight: 700;
        }

        QLabel#subtitle {
            color: #8290A1;
            font-size: 13px;
        }

        /* ================================================
           BACK BUTTON
        ================================================ */

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

        /* ================================================
           FILTER BOX
        ================================================ */

        QFrame#filterBox {
            background-color: white;
            border: 1px solid #E2EAF4;
            border-radius: 16px;
        }

        QLabel#filterLabel {
            color: #1E2F43;
            font-size: 13px;
            font-weight: 600;
            background-color : white;
            border : none;
            border-radius: 10px;
        }

        QPushButton#filterButton {
            background-color: #F5F8FC;
            color: #526273;
            border: 1px solid #E2EAF4;
            border-radius: 9px;
            padding: 7px 11px;
            font-size: 12px;
            min-width: 55px;
        }

        QPushButton#filterButton:hover {
            background-color: #EAF3FF;
            color: #1961C7;
            border-color: #C9DDF5;
        }

        QPushButton#filterButton[active="true"] {
            background-color: #1961C7;
            color: white;
            border-color: #1961C7;
        }

        /* ================================================
           RECORDS BOX
        ================================================ */

        QFrame#recordsBox {
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

        /* ================================================
           SCROLL CONTENT
        ================================================ */

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

        /* ================================================
           RECORD CARD
        ================================================ */

        QFrame#recordCard {
            background-color: white;
            border: 1px solid #E2EAF4;
            border-radius: 14px;
        }

        QFrame#recordCard:hover {
            background-color: #EAF3FF;
            border-color: #C9DDF5;
        }

        QFrame#recordCard QLabel {
            background-color: transparent;
            border: none;
        }

        QLabel#recordTitle {
            color: #1E2F43;
            font-size: 14px;
            font-weight: 700;
        }

        QLabel#recordInfo {
            color: #526273;
            font-size: 13px;
        }

        QLabel#recordDate {
            color: #8290A1;
            font-size: 11px;
        }

        QLabel#emptyLabel {
            color: #8290A1;
            font-size: 14px;
            padding: 40px;
        }

        /* ================================================
           SCROLL BAR
        ================================================ */

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

        self.update_filter_buttons()

    # =================================================
    # CHANGE FILTER
    # =================================================

    def change_filter(
        self,
        filter_name
    ):

        self.current_filter = filter_name

        self.refresh_records()

        self.update_filter_buttons()

    # =================================================
    # UPDATE FILTER BUTTONS
    # =================================================

    def update_filter_buttons(self):

        for button in self.filter_buttons:

            button.setProperty(
                "active",
                False
            )

            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )

        if self.current_filter == "همه":

            active_button = self.all_button

        elif self.current_filter == "پرداخت":

            active_button = self.payment_button

        elif self.current_filter == "حضور و غیاب":

            active_button = self.attendance_button

        elif self.current_filter == "مرخصی":

            active_button = self.leave_button

        elif self.current_filter == "وام":

            active_button = self.loan_button

        else:

            active_button = self.other_button

        active_button.setProperty(
            "active",
            True
        )

        active_button.style().unpolish(
            active_button
        )

        active_button.style().polish(
            active_button
        )

    # =================================================
    # REFRESH RECORDS
    # =================================================

    def refresh_records(self):

        while self.scroll_layout.count():

            item = self.scroll_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

        # =================================================
        # FILTER
        # =================================================

        if self.current_filter == "همه":

            filtered_records = self.records

        else:

            filtered_records = [

                record

                for record in self.records

                if record["category"]
                == self.current_filter

            ]

        # =================================================
        # EMPTY STATE
        # =================================================

        if not filtered_records:

            empty_label = QLabel(
                "برای این بخش سابقه‌ای ثبت نشده است."
            )

            empty_label.setObjectName(
                "emptyLabel"
            )

            empty_label.setAlignment(
                Qt.AlignCenter
            )

            self.scroll_layout.addWidget(
                empty_label
            )

            self.scroll_layout.addStretch()

            return

        # =================================================
        # ADD RECORDS
        # =================================================

        for record in filtered_records:

            self.add_record(
                self.scroll_layout,
                record["type"],
                record["employee"],
                record["description"],
                record["date"]
            )

        self.scroll_layout.addStretch()

    # =================================================
    # ADD EVENT
    # =================================================

    def add_event(
        self,
        event_type,
        category,
        employee,
        description
    ):

        now = datetime.now()

        record = {

            "type": event_type,

            "category": category,

            "employee": employee,

            "description": description,

            "date": now.strftime(
                "%Y/%m/%d - %H:%M"
            )

        }

        self.records.insert(
            0,
            record
        )

        self.refresh_records()

    # =================================================
    # RECORD CARD
    # =================================================

    def add_record(
        self,
        layout,
        title,
        employee,
        info,
        date
    ):

        card = QFrame()

        card.setObjectName(
            "recordCard"
        )

        card_layout = QHBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        card_layout.setSpacing(
            15
        )

        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            3
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "recordTitle"
        )

        employee_label = QLabel(
            employee
        )

        employee_label.setObjectName(
            "recordInfo"
        )

        info_label = QLabel(
            info
        )

        info_label.setObjectName(
            "recordInfo"
        )

        info_label.setWordWrap(
            True
        )

        date_label = QLabel(
            date
        )

        date_label.setObjectName(
            "recordDate"
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            employee_label
        )

        text_layout.addWidget(
            info_label
        )

        text_layout.addWidget(
            date_label
        )

        card_layout.addLayout(
            text_layout
        )

        card_layout.addStretch()

        layout.addWidget(
            card
        )