from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QComboBox,
    QFrame,
    QApplication,
    QSizePolicy,
    QBoxLayout
)

from PySide6.QtCore import Qt, QPoint

class FinanceWindow(QWidget):

    def __init__(self, phone_number):

        super().__init__()

        self.phone_number = phone_number

        # =====================================================
        # اطلاعات مالی
        # =====================================================

        self.base_salary = 18_000_000
        self.overtime = 2_450_000
        self.bonus = 0
        self.benefits = 0

        self.insurance = 900_000
        self.tax = 420_000
        self.advance = 0
        self.other_deductions = 0

        self.total_loan = 5_000_000
        self.paid_loan = 1_000_000
        self.loan_installment = 1_000_000
        self.other_debt = 0

        self.remaining_loan = max(
            self.total_loan - self.paid_loan,
            0
        )

        self.total_deductions = (
            self.insurance
            + self.tax
            + self.advance
            + self.other_deductions
            + self.loan_installment
            + self.other_debt
        )

        self.final_salary = (
            self.base_salary
            + self.overtime
            + self.bonus
            + self.benefits
            - self.total_deductions
        )

        # =====================================================
        # کارمندان
        # =====================================================

        self.employees = [
            {
                "name": "علی رضایی",
                "position": "مدیر فروش"
            },
            {
                "name": "سارا محمدی",
                "position": "حسابدار"
            },
            {
                "name": "محمد احمدی",
                "position": "کارشناس فروش"
            }
        ]

        self.selected_employee = self.employees[0]

        self.init_ui()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):

        self.setWindowTitle("امور مالی")

        self.setMinimumSize(
            900,
            620
        )

        self.setLayoutDirection(
            Qt.RightToLeft
        )

        self.setStyleSheet("""
            QWidget {
                font-family: Vazirmatn;
                color: #17324D;
            }

            QWidget#mainWidget {
                background: #F5F8FC;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

            QScrollArea > QWidget > QWidget {
                background: transparent;
            }

            /* =================================================
               اسکرول‌بار کاملاً گرد
               ================================================= */

            QScrollBar:vertical {
                width: 10px;
                background: #E8EEF6;
                border: none;
                border-radius: 5px;
                margin: 2px 0;
            }

            QScrollBar::handle:vertical {
                background: #4589E8;
                border: none;
                border-radius: 5px;
                min-height: 45px;
                margin: 0;
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

            /* =================================================
               ماه
               ================================================= */

            QComboBox {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 15px;
                padding: 6px 12px;
                min-height: 28px;
                color: #17324D;
            }

            QComboBox:hover {
                border-color: #4589E8;
            }

            QComboBox::drop-down {
                border: none;
                width: 26px;
            }

            QComboBox QAbstractItemView {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 15px;
                padding: 5px;
                selection-background-color: #EAF3FF;
                selection-color: #1961C7;
            }

            /* =================================================
               انتخاب کارمند
               ================================================= */

            QFrame#employeeNameBox {
                background: #EAF3FF;
                border: 1px solid #D6E7FA;
                border-radius: 18px;
            }

            QLabel#employeeNameLabel {
                color: #1961C7;
                background: transparent;
                border: none;
                font-size: 10px;
                font-weight: 800;
            }

            QLabel#employeePositionLabel {
                color: #8292A5;
                background: transparent;
                border: none;
                font-size: 8px;
            }

            QFrame#employeePopup {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 22px;
            }

            QFrame#employeeOption {
                background: #F7F9FC;
                border: 1px solid #E7EDF5;
                border-radius: 15px;
            }

            QFrame#employeeOption:hover {
                background: #EAF3FF;
                border-color: #D2E3F8;
            }

            QLabel#employeeOptionName {
                color: #29445D;
                background: transparent;
                border: none;
                font-size: 10px;
                font-weight: 800;
            }

            QLabel#employeeOptionPosition {
                color: #8292A5;
                background: transparent;
                border: none;
                font-size: 8px;
            }
        """)

        # =====================================================
        # MAIN
        # =====================================================

        main_widget = QWidget()

        main_widget.setObjectName(
            "mainWidget"
        )

        main_layout = QVBoxLayout(
            main_widget
        )

        main_layout.setContentsMargins(
            20,
            10,
            20,
            18
        )

        main_layout.setSpacing(
            7
        )

        # =====================================================
        # HEADER
        # =====================================================

        header = QHBoxLayout()

        header.setSpacing(
            6
        )

        title_area = QBoxLayout(
            QBoxLayout.LeftToRight
        )

        title_area.setSpacing(
            7
        )

        # -----------------------------------------------------
        # فلش
        # -----------------------------------------------------

        back_button = QPushButton(
            "›"
        )

        back_button.setFixedSize(
            34,
            34
        )

        back_button.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 17px;
                color: #1961C7;
                font-size: 23px;
                font-weight: bold;
                padding-bottom: 2px;
            }

            QPushButton:hover {
                background: #EAF3FF;
                border-color: #C9DDF7;
            }
        """)

        back_button.clicked.connect(
            self.close
        )

        # -----------------------------------------------------
        # عنوان
        # -----------------------------------------------------

        title_box = QVBoxLayout()

        title_box.setSpacing(
            0
        )

        title = QLabel(
            "امور مالی"
        )

        title.setStyleSheet("""
            QLabel {
                color: #17324D;
                font-size: 20px;
                font-weight: 800;
            }
        """)

        subtitle = QLabel(
            "مدیریت حقوق، مزایا، کسورات و بدهی"
        )

        subtitle.setStyleSheet("""
            QLabel {
                color: #8292A5;
                font-size: 9px;
            }
        """)

        title_box.addWidget(
            title
        )

        title_box.addWidget(
            subtitle
        )

        title_area.addWidget(
            back_button
        )

        title_area.addLayout(
            title_box
        )

        header.addLayout(
            title_area
        )

        header.addStretch()

        # -----------------------------------------------------
        # ماه
        # -----------------------------------------------------

        month_combo = QComboBox()

        month_combo.addItems([
            "مهر ۱۴۰۵",
            "شهریور ۱۴۰۵",
            "مرداد ۱۴۰۵",
            "تیر ۱۴۰۵"
        ])

        month_combo.setFixedWidth(
            115
        )

        header.addWidget(
            month_combo
        )

        main_layout.addLayout(
            header
        )

        # =====================================================
        # انتخاب کارمند
        # =====================================================

        employee_name_box = QFrame()

        employee_name_box.setObjectName(
            "employeeNameBox"
        )

        employee_name_box.setFixedHeight(
            48
        )

        employee_layout = QHBoxLayout(
            employee_name_box
        )

        employee_layout.setContentsMargins(
            12,
            5,
            12,
            5
        )

        employee_layout.setSpacing(
            7
        )

        employee_text_layout = QVBoxLayout()

        employee_text_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        employee_text_layout.setSpacing(
            0
        )

        employee_name_label = QLabel(
            self.selected_employee["name"]
        )

        employee_name_label.setObjectName(
            "employeeNameLabel"
        )

        employee_position_label = QLabel(
            self.selected_employee["position"]
        )

        employee_position_label.setObjectName(
            "employeePositionLabel"
        )

        employee_text_layout.addWidget(
            employee_name_label
        )

        employee_text_layout.addWidget(
            employee_position_label
        )

        arrow_label = QLabel(
            "⌄"
        )

        arrow_label.setStyleSheet("""
            QLabel {
                color: #4589E8;
                background: transparent;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
        """)

        employee_layout.addLayout(
            employee_text_layout
        )

        employee_layout.addStretch()

        employee_layout.addWidget(
            arrow_label
        )

        employee_name_box.mousePressEvent = (
            lambda event:
            self.show_employee_popup(
                employee_name_box
            )
        )

        main_layout.addWidget(
            employee_name_box
        )

        # =====================================================
        # SCROLL
        # =====================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            16,
            0,
            8,
            1
        )

        content_layout.setSpacing(
            7
        )

        # =====================================================
        # کارت دریافتی نهایی
        # =====================================================

        salary_card = self.round_card()

        salary_layout = QHBoxLayout(
            salary_card
        )

        salary_layout.setContentsMargins(
            14,
            9,
            14,
            9
        )

        salary_layout.setSpacing(
            9
        )

        salary_inner = QFrame()

        salary_inner.setStyleSheet("""
            QFrame {
                background: #F4F8FD;
                border: none;
                border-radius: 15px;
            }
        """)

        salary_inner_layout = QVBoxLayout(
            salary_inner
        )

        salary_inner_layout.setContentsMargins(
            12,
            5,
            12,
            5
        )

        salary_inner_layout.setSpacing(
            0
        )

        salary_label = QLabel(
            "دریافتی نهایی"
        )

        salary_label.setStyleSheet("""
            QLabel {
                color: #8292A5;
                background: transparent;
                border: none;
                font-size: 9px;
                font-weight: 600;
            }
        """)

        salary_value = QLabel(
            self.money(
                self.final_salary
            )
        )

        salary_value.setStyleSheet("""
            QLabel {
                color: #1961C7;
                background: transparent;
                border: none;
                font-size: 21px;
                font-weight: 900;
            }
        """)

        salary_unit = QLabel(
            "تومان"
        )

        salary_unit.setStyleSheet("""
            QLabel {
                color: #8292A5;
                background: transparent;
                border: none;
                font-size: 8px;
            }
        """)

        salary_inner_layout.addWidget(
            salary_label
        )

        salary_inner_layout.addWidget(
            salary_value
        )

        salary_inner_layout.addWidget(
            salary_unit
        )

        salary_layout.addWidget(
            salary_inner,
            1
        )

        # -----------------------------------------------------
        # وضعیت
        # -----------------------------------------------------

        status_box = QFrame()

        status_box.setStyleSheet("""
            QFrame {
                background: #EAF7EF;
                border: none;
                border-radius: 15px;
            }
        """)

        status_layout = QVBoxLayout(
            status_box
        )

        status_layout.setContentsMargins(
            12,
            7,
            12,
            7
        )

        status = QLabel(
            "پرداخت شده"
        )

        status.setAlignment(
            Qt.AlignCenter
        )

        status.setStyleSheet("""
            QLabel {
                color: #27945B;
                background: transparent;
                border: none;
                font-size: 9px;
                font-weight: 800;
            }
        """)

        status_layout.addWidget(
            status
        )

        salary_layout.addWidget(
            status_box
        )

        content_layout.addWidget(
            salary_card
        )

        # =====================================================
        # خلاصه حقوق
        # =====================================================

        summary_card = self.round_card()

        summary_layout = QHBoxLayout(
            summary_card
        )

        summary_layout.setContentsMargins(
            9,
            9,
            9,
            9
        )

        summary_layout.setSpacing(
            6
        )

        summary_layout.addWidget(
            self.inner_summary(
                "حقوق پایه",
                self.base_salary,
                "#1961C7"
            )
        )

        summary_layout.addWidget(
            self.inner_summary(
                "اضافه‌کاری",
                self.overtime,
                "#4589E8"
            )
        )

        summary_layout.addWidget(
            self.inner_summary(
                "کسورات",
                self.total_deductions,
                "#D45B68"
            )
        )

        content_layout.addWidget(
            summary_card
        )

        # =====================================================
        # جزئیات محاسبه
        # =====================================================

        calc_card = self.round_card()

        calc_layout = QVBoxLayout(
            calc_card
        )

        calc_layout.setContentsMargins(
            14,
            10,
            14,
            11
        )

        calc_layout.setSpacing(
            6
        )

        calc_title = QLabel(
            "جزئیات محاسبه"
        )

        calc_title.setStyleSheet("""
            QLabel {
                color: #17324D;
                background: transparent;
                border: none;
                font-size: 12px;
                font-weight: 800;
            }
        """)

        calc_layout.addWidget(
            calc_title
        )

        grid = QGridLayout()

        grid.setHorizontalSpacing(
            6
        )

        grid.setVerticalSpacing(
            6
        )

        details = [
            ("روزهای کاری", "۲۲ روز"),
            ("روزهای حضور", "۲۰ روز"),
            ("روزهای غیبت", "۲ روز"),
            ("ساعات کاری", "۱۶۰ ساعت"),
            ("ساعات اضافه‌کاری", "۱۲ ساعت"),
            ("تأخیر", "۱ ساعت و ۲۰ دقیقه"),
            ("پاداش", self.money(self.bonus)),
            ("مزایا", self.money(self.benefits)),
        ]

        for index, (label, value) in enumerate(
            details
        ):

            box = self.round_inner_box(
                label,
                value
            )

            row = index // 4
            col = index % 4

            grid.addWidget(
                box,
                row,
                col
            )

        calc_layout.addLayout(
            grid
        )

        content_layout.addWidget(
            calc_card
        )

        # =====================================================
        # قرض و بدهی
        # =====================================================

        loan_card = self.round_card()

        loan_layout = QVBoxLayout(
            loan_card
        )

        loan_layout.setContentsMargins(
            14,
            10,
            14,
            11
        )

        loan_layout.setSpacing(
            6
        )

        loan_title = QLabel(
            "قرض و بدهی"
        )

        loan_title.setStyleSheet("""
            QLabel {
                color: #17324D;
                background: transparent;
                border: none;
                font-size: 12px;
                font-weight: 800;
            }
        """)

        loan_layout.addWidget(
            loan_title
        )

        loan_grid = QGridLayout()

        loan_grid.setHorizontalSpacing(
            6
        )

        loan_items = [
            ("کل قرض", self.total_loan),
            ("پرداخت‌شده", self.paid_loan),
            ("مانده قرض", self.remaining_loan),
            ("قسط این ماه", self.loan_installment),
            ("سایر بدهی", self.other_debt),
        ]

        for index, (label, value) in enumerate(
            loan_items
        ):

            box = self.round_inner_box(
                label,
                self.money(value)
            )

            loan_grid.addWidget(
                box,
                0,
                index
            )

        loan_layout.addLayout(
            loan_grid
        )

        content_layout.addWidget(
            loan_card
        )

        # =====================================================
        # ریز تراکنش‌ها
        # =====================================================

        transaction_card = self.round_card()

        transaction_layout = QVBoxLayout(
            transaction_card
        )

        transaction_layout.setContentsMargins(
            14,
            10,
            14,
            11
        )

        transaction_layout.setSpacing(
            6
        )

        title_row = QHBoxLayout()

        transaction_title = QLabel(
            "ریز تراکنش‌ها"
        )

        transaction_title.setStyleSheet("""
            QLabel {
                color: #17324D;
                background: transparent;
                border: none;
                font-size: 12px;
                font-weight: 800;
            }
        """)

        count_box = QFrame()

        count_box.setStyleSheet("""
            QFrame {
                background: #EAF3FF;
                border: none;
                border-radius: 11px;
            }
        """)

        count_layout = QHBoxLayout(
            count_box
        )

        count_layout.setContentsMargins(
            8,
            3,
            8,
            3
        )

        count_label = QLabel(
            "۵ تراکنش"
        )

        count_label.setStyleSheet("""
            QLabel {
                color: #4589E8;
                background: transparent;
                border: none;
                font-size: 8px;
                font-weight: 700;
            }
        """)

        count_layout.addWidget(
            count_label
        )

        title_row.addWidget(
            transaction_title
        )

        title_row.addStretch()

        title_row.addWidget(
            count_box
        )

        transaction_layout.addLayout(
            title_row
        )

        transactions = [
            (
                "۶ مهر",
                "حقوق پایه",
                "+۱۸٬۰۰۰٬۰۰۰",
                True
            ),
            (
                "۱۰ مهر",
                "اضافه‌کاری",
                "+۲٬۴۵۰٬۰۰۰",
                True
            ),
            (
                "۱۵ مهر",
                "بیمه",
                "-۹۰۰٬۰۰۰",
                False
            ),
            (
                "۱۵ مهر",
                "مالیات",
                "-۴۲۰٬۰۰۰",
                False
            ),
            (
                "۲۰ مهر",
                "قسط قرض",
                "-۱٬۰۰۰٬۰۰۰",
                False
            )
        ]

        for date, name, amount, positive in transactions:

            transaction_layout.addWidget(
                self.transaction_row(
                    date,
                    name,
                    amount,
                    positive
                )
            )

        content_layout.addWidget(
            transaction_card
        )

        # =====================================================
        # فضای خالی پایین
        # =====================================================

        content_layout.addSpacing(
            10
        )

        scroll.setWidget(
            content
        )

        main_layout.addWidget(
            scroll
        )

        self.setLayout(
            main_layout
        )

    # =====================================================
    # پاپ‌آپ انتخاب کارمند
    # =====================================================

    def show_employee_popup(
        self,
        employee_name_box
    ):

        if hasattr(
            self,
            "employee_popup"
        ) and self.employee_popup.isVisible():

            self.employee_popup.close()

            return

        menu = QFrame(
            self
        )

        menu.setObjectName(
            "employeePopup"
        )

        menu.setFixedWidth(
            300
        )

        menu.setFixedHeight(
            220
        )

        menu_layout = QVBoxLayout(
            menu
        )

        menu_layout.setContentsMargins(
            12,
            12,
            10,
            12
        )

        menu_layout.setSpacing(
            0
        )

        # =====================================================
        # اسکرول پاپ‌آپ
        # =====================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        # فقط این قسمت برای اینکه اسکرول همیشه دیده شود
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOn
        )

        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                width: 8px;
                background: #E8EEF6;
                border: none;
                border-radius: 4px;
                margin: 3px 2px 3px 2px;
            }

            QScrollBar::handle:vertical {
                background: #4589E8;
                border: none;
                border-radius: 4px;
                min-height: 35px;
                margin: 0;
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
        """)

        # =====================================================
        # محتوای داخل اسکرول
        # =====================================================

        scroll_content = QWidget()

        scroll_content.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)

        scroll_layout = QVBoxLayout(
            scroll_content
        )

        scroll_layout.setContentsMargins(
            10,
            0,
            0,
            0
        )

        scroll_layout.setSpacing(
            8
        )

        # =====================================================
        # گزینه‌های کارمندان
        # =====================================================

        for employee in self.employees:

            option = QFrame()

            option.setObjectName(
                "employeeOption"
            )

            option.setFixedHeight(
                55
            )

            option_layout = QHBoxLayout(
                option
            )

            option_layout.setContentsMargins(
                12,
                6,
                12,
                6
            )

            option_layout.setSpacing(
                4
            )

            text_layout = QVBoxLayout()

            text_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            text_layout.setSpacing(
                0
            )

            name_label = QLabel(
                employee["name"]
            )

            name_label.setObjectName(
                "employeeOptionName"
            )

            position_label = QLabel(
                employee["position"]
            )

            position_label.setObjectName(
                "employeeOptionPosition"
            )

            text_layout.addWidget(
                name_label
            )

            text_layout.addWidget(
                position_label
            )

            option_layout.addLayout(
                text_layout
            )

            option_layout.addStretch()

            option.mousePressEvent = (
                lambda event,
                emp=employee,
                box=employee_name_box,
                popup=menu:
                self.select_employee(
                    emp,
                    box,
                    popup
                )
            )

            scroll_layout.addWidget(
                option
            )

        scroll_layout.addStretch()

        scroll.setWidget(
            scroll_content
        )

        menu_layout.addWidget(
            scroll
        )

        self.employee_popup = menu

        # =====================================================
        # موقعیت پاپ‌آپ
        # =====================================================

        pos = employee_name_box.mapToGlobal(
            QPoint(
                employee_name_box.width()
                - menu.width(),
                employee_name_box.height()
                + 8
            )
        )

        local_pos = self.mapFromGlobal(
            pos
        )

        menu.move(
            local_pos
        )

        menu.show()
        menu.raise_()

    # =====================================================
    # انتخاب کارمند
    # =====================================================

    def select_employee(
        self,
        employee,
        employee_name_box,
        popup
    ):

        self.selected_employee = employee

        labels = employee_name_box.findChildren(
            QLabel
        )

        if len(labels) >= 2:

            labels[0].setText(
                employee["name"]
            )

            labels[1].setText(
                employee["position"]
            )

        popup.close()

    # =====================================================
    # کارت اصلی
    # =====================================================

    def round_card(self):

        card = QFrame()

        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 20px;
            }
        """)

        return card

    # =====================================================
    # باکس داخلی
    # =====================================================

    def round_inner_box(
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
                background: #F7F9FC;
                border: 1px solid #E7EDF5;
                border-radius: 14px;
            }
        """)

        layout = QVBoxLayout(
            box
        )

        layout.setContentsMargins(
            8,
            5,
            8,
            5
        )

        layout.setSpacing(
            0
        )

        title = QLabel(
            title_text
        )

        title.setStyleSheet("""
            QLabel {
                color: #8A99AA;
                background: transparent;
                border: none;
                font-size: 8px;
                font-weight: 600;
            }
        """)

        value = QLabel(
            str(value_text)
        )

        value.setStyleSheet("""
            QLabel {
                color: #29445D;
                background: transparent;
                border: none;
                font-size: 10px;
                font-weight: 800;
            }
        """)

        layout.addWidget(
            title
        )

        layout.addWidget(
            value
        )

        return box

    # =====================================================
    # کارت خلاصه
    # =====================================================

    def inner_summary(
        self,
        title_text,
        value,
        text_color
    ):

        box = QFrame()

        box.setMinimumHeight(
            59
        )

        box.setStyleSheet("""
            QFrame {
                background: #F7F9FC;
                border: 1px solid #E7EDF5;
                border-radius: 15px;
            }
        """)

        layout = QVBoxLayout(
            box
        )

        layout.setContentsMargins(
            10,
            6,
            10,
            6
        )

        layout.setSpacing(
            1
        )

        title = QLabel(
            title_text
        )

        title.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #8292A5;
                font-size: 8px;
                font-weight: 600;
            }
        """)

        value_label = QLabel(
            self.money(value)
        )

        value_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {text_color};
                font-size: 12px;
                font-weight: 900;
            }}
        """)

        layout.addWidget(
            title
        )

        layout.addWidget(
            value_label
        )

        return box

    # =====================================================
    # تراکنش
    # =====================================================

    def transaction_row(
        self,
        date,
        name,
        amount,
        positive
    ):

        row = QFrame()

        row.setMinimumHeight(
            49
        )

        row.setStyleSheet("""
            QFrame {
                background: #F7F9FC;
                border: 1px solid #E7EDF5;
                border-radius: 16px;
            }

            QFrame:hover {
                background: #F0F6FF;
                border-color: #D8E5F4;
            }
        """)

        layout = QHBoxLayout(
            row
        )

        layout.setContentsMargins(
            11,
            5,
            11,
            5
        )

        layout.setSpacing(
            8
        )

        # -----------------------------------------------------
        # تاریخ
        # -----------------------------------------------------

        date_box = QFrame()

        date_box.setFixedWidth(
            55
        )

        date_box.setStyleSheet("""
            QFrame {
                background: white;
                border: none;
                border-radius: 12px;
            }
        """)

        date_layout = QVBoxLayout(
            date_box
        )

        date_layout.setContentsMargins(
            5,
            4,
            5,
            4
        )

        date_label = QLabel(
            date
        )

        date_label.setAlignment(
            Qt.AlignCenter
        )

        date_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #8292A5;
                font-size: 8px;
                font-weight: 700;
            }
        """)

        date_layout.addWidget(
            date_label
        )

        # -----------------------------------------------------
        # نام
        # -----------------------------------------------------

        name_box = QFrame()

        name_box.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)

        name_layout = QVBoxLayout(
            name_box
        )

        name_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        name_label = QLabel(
            name
        )

        name_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #29445D;
                font-size: 10px;
                font-weight: 800;
            }
        """)

        name_layout.addWidget(
            name_label
        )

        # -----------------------------------------------------
        # مبلغ
        # -----------------------------------------------------

        amount_box = QFrame()

        amount_box.setStyleSheet("""
            QFrame {
                background: white;
                border: none;
                border-radius: 13px;
            }
        """)

        amount_layout = QHBoxLayout(
            amount_box
        )

        amount_layout.setContentsMargins(
            8,
            4,
            8,
            4
        )

        amount_label = QLabel(
            amount
        )

        amount_label.setAlignment(
            Qt.AlignCenter
        )

        if positive:

            amount_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    border: none;
                    color: #27945B;
                    font-size: 10px;
                    font-weight: 900;
                }
            """)

        else:

            amount_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    border: none;
                    color: #D45B68;
                    font-size: 10px;
                    font-weight: 900;
                }
            """)

        amount_layout.addWidget(
            amount_label
        )

        layout.addWidget(
            date_box
        )

        layout.addWidget(
            name_box
        )

        layout.addStretch()

        layout.addWidget(
            amount_box
        )

        return row

    # =====================================================
    # فرمت پول
    # =====================================================

    def money(
        self,
        value
    ):

        return f"{value:,}".replace(
            ",",
            "٬"
        )

# =========================================================
# اجرای مستقل
# =========================================================

if __name__ == "__main__":

    import sys

    app = QApplication(
        sys.argv
    )

    app.setLayoutDirection(
        Qt.RightToLeft
    )

    window = FinanceWindow(
        "09123456789"
    )

    window.show()

    sys.exit(
        app.exec()
    )