from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QComboBox,
    QMessageBox,
    QGridLayout
)

from PySide6.QtCore import Qt

# =========================================================
# REPORTS WINDOW
# =========================================================

class ReportsWindow(QWidget):

    def __init__(self, parent_window=None, phone_number=""):
        super().__init__()

        self.parent_window = parent_window
        self.phone_number = phone_number

        self.setWindowTitle("گزارش‌ها")
        self.setMinimumSize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)

        # -------------------------------------------------
        # SAMPLE DATA
        # بعداً این قسمت از MySQL خوانده می‌شود
        # -------------------------------------------------

        self.report_data = {
            "employees": 4,

            "working_hours": [
                32,
                28,
                36,
                32
            ],

            "payments": [
                6500000,
                5800000,
                7200000,
                5000000
            ],

            "tasks": {
                "total": 45,
                "completed": 36,
                "pending": 9
            }
        }

        self.setup_ui()
        self.calculate_reports()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        self.setStyleSheet("""
            QWidget {
                font-family: Vazirmatn;
                color: #25364A;
            }

            QFrame#mainFrame {
                background-color: #F5F8FC;
            }

            QFrame#headerFrame {
                background-color: white;
                border-bottom: 1px solid #E2EAF4;
            }

            QLabel#title {
                font-size: 23px;
                font-weight: bold;
                color: #25364A;
            }

            QLabel#subtitle {
                font-size: 13px;
                color: #8290A1;
            }

            QPushButton#backButton {
                background-color: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 12px;
                font-size: 20px;
            }

            QPushButton#backButton:hover {
                background-color: #DDEBFF;
            }

            QFrame#filterCard {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }

            QLabel#filterTitle {
                font-size: 15px;
                font-weight: bold;
            }

            QComboBox {
                background-color: #F5F8FC;
                border: 1px solid #E2EAF4;
                border-radius: 12px;
                padding: 10px 14px;
                min-height: 20px;
            }

            QComboBox:hover {
                border: 1px solid #4589E8;
            }

            QPushButton#filterButton {
                background-color: #1961C7;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 22px;
                font-weight: bold;
            }

            QPushButton#filterButton:hover {
                background-color: #4589E8;
            }

            QFrame#summaryCard {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }

            QLabel#summaryIcon {
                background-color: #EAF3FF;
                color: #1961C7;
                border-radius: 12px;
                font-size: 20px;
            }

            QLabel#summaryTitle {
                color: #8290A1;
                font-size: 12px;
            }

            QLabel#summaryValue {
                color: #25364A;
                font-size: 21px;
                font-weight: bold;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: bold;
            }

            QFrame#reportCard {
                background-color: white;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }

            QFrame#reportCard:hover {
                border: 1px solid #4589E8;
            }

            QLabel#reportTitle {
                font-size: 16px;
                font-weight: bold;
            }

            QLabel#reportDescription {
                color: #8290A1;
                font-size: 12px;
            }

            QPushButton#reportButton {
                background-color: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 10px;
                padding: 8px 15px;
                font-weight: bold;
            }

            QPushButton#reportButton:hover {
                background-color: #1961C7;
                color: white;
            }

            QScrollBar:vertical {
                width: 10px;
                background: transparent;
                margin: 8px 2px 8px 0;
            }

            QScrollBar::handle:vertical {
                background: #C9D8EA;
                border-radius: 5px;
                min-height: 40px;
            }

            QScrollBar::handle:vertical:hover {
                background: #AFC5DF;
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

        # =================================================
        # MAIN
        # =================================================

        main_frame = QFrame()
        main_frame.setObjectName("mainFrame")

        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =================================================
        # HEADER
        # =================================================

        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(85)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 12, 20, 12)
        header_layout.setSpacing(15)

        back_button = QPushButton("‹")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(45, 45)
        back_button.clicked.connect(self.go_back)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("گزارش‌ها")
        title.setObjectName("title")

        subtitle = QLabel(
            "گزارش عملکرد، حضور و امور مالی مجموعه"
        )
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addWidget(back_button)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addWidget(header)

        # =================================================
        # SCROLL AREA
        # =================================================

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(
            20, 18, 20, 20
        )
        content_layout.setSpacing(18)

        # =================================================
        # FILTER
        # =================================================

        filter_card = QFrame()
        filter_card.setObjectName("filterCard")

        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(18, 16, 18, 16)
        filter_layout.setSpacing(12)

        filter_title = QLabel("فیلتر گزارش")
        filter_title.setObjectName("filterTitle")

        filter_layout.addWidget(filter_title)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.group_combo = QComboBox()
        self.group_combo.addItems([
            "همه مجموعه‌ها",
            "پیچک",
            "مجموعه کارمند"
        ])

        self.date_combo = QComboBox()
        self.date_combo.addItems([
            "امروز",
            "این هفته",
            "این ماه",
            "سه ماه اخیر"
        ])

        filter_button = QPushButton("اعمال فیلتر")
        filter_button.setObjectName("filterButton")
        filter_button.clicked.connect(self.apply_filter)

        filter_row.addWidget(self.group_combo, 2)
        filter_row.addWidget(self.date_combo, 2)
        filter_row.addWidget(filter_button, 1)

        filter_layout.addLayout(filter_row)

        content_layout.addWidget(filter_card)

        # =================================================
        # SUMMARY TITLE
        # =================================================

        summary_title = QLabel("خلاصه گزارش")
        summary_title.setObjectName("sectionTitle")

        content_layout.addWidget(summary_title)

        # =================================================
        # SUMMARY CARDS
        # =================================================

        summary_grid = QGridLayout()
        summary_grid.setSpacing(14)

        self.employees_value = self.create_summary_card(
            summary_grid,
            0,
            0,
            "👥",
            "تعداد کارکنان",
            "0"
        )

        self.hours_value = self.create_summary_card(
            summary_grid,
            0,
            1,
            "◷",
            "ساعات کاری",
            "0 ساعت"
        )

        self.payment_value = self.create_summary_card(
            summary_grid,
            0,
            2,
            "₮",
            "مجموع پرداختی",
            "0 تومان"
        )

        self.tasks_value = self.create_summary_card(
            summary_grid,
            0,
            3,
            "✓",
            "کارهای انجام‌شده",
            "0"
        )

        content_layout.addLayout(summary_grid)

        # =================================================
        # REPORTS TITLE
        # =================================================

        reports_title = QLabel("گزارش‌های موجود")
        reports_title.setObjectName("sectionTitle")

        content_layout.addWidget(reports_title)

        # =================================================
        # REPORT CARDS
        # =================================================

        reports_grid = QGridLayout()
        reports_grid.setSpacing(14)

        self.create_report_card(
            reports_grid,
            0,
            0,
            "◷",
            "گزارش حضور و غیاب",
            "ساعات حضور، تأخیر و غیبت کارکنان",
            "attendance"
        )

        self.create_report_card(
            reports_grid,
            0,
            1,
            "₮",
            "گزارش مالی",
            "پرداخت‌ها، دستمزدها و هزینه‌های مجموعه",
            "finance"
        )

        self.create_report_card(
            reports_grid,
            1,
            0,
            "👥",
            "گزارش عملکرد کارکنان",
            "بررسی کارکرد و وضعیت عملکرد کارکنان",
            "employees"
        )

        self.create_report_card(
            reports_grid,
            1,
            1,
            "✓",
            "گزارش کارها",
            "کارهای ثبت‌شده و وضعیت انجام آن‌ها",
            "tasks"
        )

        content_layout.addLayout(reports_grid)

        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # =================================================
        # WINDOW
        # =================================================

        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(main_frame)

    # =====================================================
    # SUMMARY CARD
    # =====================================================

    def create_summary_card(
        self,
        grid,
        row,
        column,
        icon,
        title,
        value
    ):

        card = QFrame()
        card.setObjectName("summaryCard")
        card.setMinimumHeight(120)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setObjectName("summaryIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(45, 45)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("summaryTitle")

        value_label = QLabel(value)
        value_label.setObjectName("summaryValue")

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()

        grid.addWidget(card, row, column)

        return value_label

    # =====================================================
    # REPORT CARD
    # =====================================================

    def create_report_card(
        self,
        grid,
        row,
        column,
        icon,
        title,
        description,
        report_type
    ):

        card = QFrame()
        card.setObjectName("reportCard")
        card.setMinimumHeight(145)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        top_layout = QHBoxLayout()

        icon_label = QLabel(icon)
        icon_label.setObjectName("summaryIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(42, 42)

        title_label = QLabel(title)
        title_label.setObjectName("reportTitle")

        top_layout.addWidget(icon_label)
        top_layout.addSpacing(10)
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        description_label = QLabel(description)
        description_label.setObjectName("reportDescription")
        description_label.setWordWrap(True)

        button = QPushButton("مشاهده گزارش")
        button.setObjectName("reportButton")
        button.clicked.connect(
            lambda checked=False, r=report_type:
            self.open_report(r)
        )

        layout.addLayout(top_layout)
        layout.addWidget(description_label)
        layout.addStretch()
        layout.addWidget(
            button,
            alignment=Qt.AlignLeft
        )

        grid.addWidget(card, row, column)

    # =====================================================
    # CALCULATIONS
    # =====================================================

    def calculate_reports(self):

        # تعداد کارکنان
        employees = self.report_data["employees"]

        # مجموع ساعات کاری
        total_hours = sum(
            self.report_data["working_hours"]
        )

        # مجموع پرداختی
        total_payment = sum(
            self.report_data["payments"]
        )

        # کارهای انجام‌شده
        completed_tasks = self.report_data["tasks"]["completed"]

        self.employees_value.setText(
            f"{employees}"
        )

        self.hours_value.setText(
            f"{total_hours} ساعت"
        )

        self.payment_value.setText(
            f"{total_payment:,} تومان"
        )

        self.tasks_value.setText(
            f"{completed_tasks}"
        )

    # =====================================================
    # FILTER
    # =====================================================

    def apply_filter(self):

        group = self.group_combo.currentText()
        date_range = self.date_combo.currentText()

        # فعلاً داده‌ها نمونه هستند.
        # بعد از اتصال MySQL این قسمت
        # بر اساس گروه و تاریخ از دیتابیس
        # داده‌ها را دریافت می‌کند.

        self.calculate_reports()

        QMessageBox.information(
            self,
            "گزارش",
            f"گزارش {group}\n"
            f"بازه زمانی: {date_range}\n\n"
            f"فیلتر با موفقیت اعمال شد."
        )

    # =====================================================
    # OPEN REPORT
    # =====================================================

    def open_report(self, report_type):

        report_names = {
            "attendance": "گزارش حضور و غیاب",
            "finance": "گزارش مالی",
            "employees": "گزارش عملکرد کارکنان",
            "tasks": "گزارش کارها"
        }

        name = report_names.get(
            report_type,
            "گزارش"
        )

        QMessageBox.information(
            self,
            name,
            f"{name}\n\n"
            "این بخش بعد از اتصال به MySQL "
            "با اطلاعات واقعی مجموعه تکمیل می‌شود."
        )

    # =====================================================
    # BACK
    # =====================================================

    def go_back(self):

        self.close()

        if self.parent_window:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()