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

from PySide6.QtCore import Qt, QTimer, QTime, QPoint

class AttendanceWindow(QWidget):

    def __init__(self, phone_number):

        super().__init__()

        self.phone_number = phone_number

        # =================================================
        # EMPLOYEES
        # =================================================

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

        self.selected_employee = None
        self.employee_menu = None

        # =================================================
        # WORK TIME
        # =================================================

        self.work_start = QTime(
            8,
            0,
            0
        )

        self.work_end = QTime(
            16,
            0,
            0
        )

        self.entry_time = None
        self.exit_time = None

        # =================================================
        # WINDOW
        # =================================================

        self.setWindowTitle(
            "حضور و غیاب"
        )

        self.setMinimumSize(
            900,
            620
        )

        self.setLayoutDirection(
            Qt.RightToLeft
        )

        self.setStyleSheet("""
            QWidget {
                font-family: "Vazirmatn";
            }

            QLabel {
                color: #18324D;
            }
        """)

        self.setup_ui()

        # =================================================
        # CLOCK
        # =================================================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_clock
        )

        self.timer.start(
            1000
        )

        self.update_clock()

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            22,
            15,
            22,
            15
        )

        main_layout.setSpacing(
            10
        )

        # =================================================
        # HEADER
        # =================================================

        header = QHBoxLayout()

        header.setSpacing(
            8
        )

        title_layout = QHBoxLayout()

        title_layout.setSpacing(
            7
        )

        title_text_layout = QVBoxLayout()

        title_text_layout.setSpacing(
            1
        )

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

        back_button = QPushButton(
            "›"
        )

        back_button.setFixedSize(
            36,
            36
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

        # =================================================
        # EMPLOYEE CARD
        # =================================================

        employee_card = QFrame()

        employee_card.setFixedHeight(
            52
        )

        employee_card.setStyleSheet("""
            QFrame#employeeCard {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 19px;
            }
        """)

        employee_card.setObjectName(
            "employeeCard"
        )

        employee_layout = QHBoxLayout(
            employee_card
        )

        employee_layout.setContentsMargins(
            12,
            6,
            12,
            6
        )

        employee_layout.setSpacing(
            9
        )

        # =================================================
        # کارمند
        # =================================================

        employee_title = QLabel(
            "کارمند"
        )

        employee_title.setStyleSheet("""
            QLabel {
                background: #F5F8FC;
                color: #7890A8;
                border-radius: 14px;
                padding: 6px 11px;
                font-size: 9px;
            }
        """)

        employee_layout.addWidget(
            employee_title
        )

        # =================================================
        # SELECTED EMPLOYEE BOX
        # =================================================

        self.employee_name_box = QFrame()

        self.employee_name_box.setFixedHeight(
            34
        )

        self.employee_name_box.setMinimumWidth(
            170
        )

        self.employee_name_box.setCursor(
            Qt.PointingHandCursor
        )

        self.employee_name_box.setObjectName(
            "employeeNameBox"
        )

        employee_name_layout = QHBoxLayout(
            self.employee_name_box
        )

        employee_name_layout.setContentsMargins(
            12,
            0,
            9,
            0
        )

        employee_name_layout.setSpacing(
            6
        )

        self.employee_name_label = QLabel(
            "علی رضایی"
        )

        self.employee_name_label.setObjectName(
            "employeeNameLabel"
        )

        self.employee_name_label.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        employee_arrow = QLabel(
            "⌄"
        )

        employee_arrow.setObjectName(
            "employeeArrow"
        )

        employee_arrow.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True
        )

        employee_name_layout.addWidget(
            self.employee_name_label
        )

        employee_name_layout.addStretch()

        employee_name_layout.addWidget(
            employee_arrow
        )

        employee_layout.addWidget(
            self.employee_name_box
        )

        # =================================================
        # POSITION
        # =================================================

        self.employee_position = QLabel(
            "مدیر فروش"
        )

        self.employee_position.setObjectName(
            "employeePosition"
        )

        employee_layout.addStretch()

        employee_layout.addWidget(
            self.employee_position
        )

        # =================================================
        # CLICK EMPLOYEE
        # =================================================

        def employee_clicked(event):

            self.show_employee_menu()

            event.accept()

        self.employee_name_box.mousePressEvent = (
            employee_clicked
        )

        main_layout.addWidget(
            employee_card
        )

        # =================================================
        # TOP CARDS
        # =================================================

        top_cards = QHBoxLayout()

        top_cards.setSpacing(
            9
        )

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

        # =================================================
        # TODAY CARD
        # =================================================

        today_card = QFrame()

        today_card.setMinimumHeight(
            245
        )

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
            16,
            14,
            16,
            14
        )

        today_layout.setSpacing(
            9
        )

        today_title = QLabel(
            "وضعیت امروز"
        )

        today_title.setAlignment(
            Qt.AlignCenter
        )

        today_title.setFixedSize(
            650,
            38
        )

        today_title.setStyleSheet("""
            QLabel {
                background: #EAF3FF;
                color: #1961C7;
                font-size: 13px;
                font-weight: 700;
                border-radius: 19px;
                padding: 0px;
            }
        """)

        today_layout.addWidget(
            today_title,
            0,
            Qt.AlignHCenter
        )

        # =================================================
        # ENTRY / EXIT / WORK
        # =================================================

        info_layout = QHBoxLayout()

        info_layout.setSpacing(
            8
        )

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

        # =================================================
        # CALCULATIONS
        # =================================================

        calculation_layout = QHBoxLayout()

        calculation_layout.setSpacing(
            8
        )

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

        # =================================================
        # BUTTONS
        # =================================================

        buttons_layout = QHBoxLayout()

        buttons_layout.setSpacing(
            8
        )

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

        # =================================================
        # HISTORY TITLE
        # =================================================

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

        # =================================================
        # SEARCH
        # =================================================

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

        # =================================================
        # HISTORY SCROLL
        # =================================================

        history_scroll_layout = QHBoxLayout()

        history_scroll_layout.setContentsMargins(
            0,
            0,
            30,
            0
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
                margin: 20px 0 0 0;
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
            20,
            0,
            12,
            0
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

        # =================================================
        # HISTORY
        # =================================================

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

        # =================================================
        # INITIAL EMPLOYEE
        # =================================================

        self.select_employee(
            self.employees[0]
        )

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet("""
            QWidget {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
                color: #25364A;
            }

            /* =============================================
               EMPLOYEE CARD
            ============================================= */

            QFrame#employeeCard {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 19px;
            }

            QFrame#employeeNameBox {
                background-color: #EAF3FF;
                border: 1px solid #D6E6F8;
                border-radius: 13px;
            }

            QFrame#employeeNameBox:hover {
                background-color: #E4F0FF;
                border: 1px solid #4589E8;
            }

            QLabel#employeeNameLabel {
                background-color: transparent;
                border: none;
                color: #17324D;
                font-size: 12px;
                font-weight: 600;
                padding: 0px;
                margin: 0px;
            }

            QLabel#employeeArrow {
                background-color: transparent;
                border: none;
                color: #4589E8;
                font-size: 16px;
                padding: 0px;
                margin: 0px;
            }

            QLabel#employeePosition {
                background-color: transparent;
                border: none;
                color: #7890A8;
                font-size: 10px;
                padding: 0px;
                margin: 0px;
            }

            /* =============================================
               EMPLOYEE POPUP
            ============================================= */

            QFrame#employeePopup {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 22px;
            }

            QFrame#employeeOption {
                background-color: #F8FAFD;
                border: 1px solid #E7EDF5;
                border-radius: 15px;
            }

            QFrame#employeeOption:hover {
                background-color: #EAF3FF;
                border: 1px solid #4589E8;
                border-radius: 15px;
            }

            QLabel#employeeOptionName {
                background-color: transparent;
                border: none;
                color: #25364A;
                font-size: 13px;
                font-weight: 600;
                padding: 0px;
                margin: 0px;
            }

            QLabel#employeeOptionPosition {
                background-color: transparent;
                border: none;
                color: #8997A8;
                font-size: 10px;
                padding: 0px;
                margin: 0px;
            }

            /* =============================================
               INFO
            ============================================= */

            QFrame#infoCard {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 26px;
            }

            /* =============================================
               TODAY OUTER BOXES
            ============================================= */

            QFrame#timeBox {
                background: #F5F8FC;
                border: 1px solid #E8EEF5;
                border-radius: 32px;
            }

            QFrame#smallBox {
                background: #F8FAFD;
                border: 1px solid #E8EEF5;
                border-radius: 27px;
            }

            /* =============================================
               SCROLL
            ============================================= */

            QScrollBar:vertical {
                width: 12px;
                background: #E8EEF6;
                border-radius: 6px;
                margin: 20px 0 0 0;
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

    # =====================================================
    # EMPLOYEE POPUP
    # =====================================================

    def show_employee_menu(self):

        if (
            self.employee_menu is not None
            and self.employee_menu.isVisible()
        ):
            return

        menu = QFrame(
            self
        )

        menu.setObjectName(
            "employeePopup"
        )

        menu.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        menu.setFixedWidth(
            350
        )

        menu.setFixedHeight(
            200
        )

        menu_layout = QVBoxLayout(
            menu
        )

        menu_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        menu_layout.setSpacing(
            0
        )

        # =================================================
        # POPUP SCROLL
        # =================================================

        employee_scroll = QScrollArea(
            menu
        )

        employee_scroll.setWidgetResizable(
            True
        )

        employee_scroll.setFrameShape(
            QFrame.NoFrame
        )

        employee_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        employee_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOn
        )

        employee_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                width: 7px;
                background: #E8EEF6;
                border: none;
                border-radius: 4px;
                margin: 4px 2px 4px 2px;
            }

            QScrollBar::handle:vertical {
                background: #4589E8;
                border-radius: 4px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #1961C7;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:vertical {
                background: transparent;
            }
        """)

        scroll_content = QWidget()

        scroll_layout = QVBoxLayout(
            scroll_content
        )

        scroll_layout.setContentsMargins(
            20,
            0,
            0,
            0
        )

        scroll_layout.setSpacing(
            8
        )

        # =================================================
        # OTHER EMPLOYEES
        # =================================================

        for employee in self.employees:

            if (
                self.selected_employee
                and employee["name"]
                == self.selected_employee["name"]
            ):
                continue

            employee_button = QFrame()

            employee_button.setObjectName(
                "employeeOption"
            )

            employee_button.setAttribute(
                Qt.WA_StyledBackground,
                True
            )

            employee_button.setCursor(
                Qt.PointingHandCursor
            )

            employee_button.setFixedHeight(
                55
            )

            employee_layout = QHBoxLayout(
                employee_button
            )

            employee_layout.setContentsMargins(
                14,
                6,
                14,
                6
            )

            employee_layout.setSpacing(
                3
            )

            text_layout = QVBoxLayout()

            text_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            text_layout.setSpacing(
                1
            )

            name_label = QLabel(
                employee["name"]
            )

            name_label.setObjectName(
                "employeeOptionName"
            )

            name_label.setAttribute(
                Qt.WA_TransparentForMouseEvents,
                True
            )

            position_label = QLabel(
                employee["position"]
            )

            position_label.setObjectName(
                "employeeOptionPosition"
            )

            position_label.setAttribute(
                Qt.WA_TransparentForMouseEvents,
                True
            )

            text_layout.addWidget(
                name_label
            )

            text_layout.addWidget(
                position_label
            )

            employee_layout.addLayout(
                text_layout
            )

            employee_button.mousePressEvent = (
                lambda event,
                selected=employee,
                popup=menu:
                self.employee_selected(
                    selected,
                    popup,
                    event
                )
            )

            scroll_layout.addWidget(
                employee_button
            )

        scroll_layout.addStretch()

        employee_scroll.setWidget(
            scroll_content
        )

        menu_layout.addWidget(
            employee_scroll
        )

        # =================================================
        # SHOW
        # =================================================

        menu.adjustSize()

        pos = self.employee_name_box.mapToGlobal(
            QPoint(
                self.employee_name_box.width()
                - menu.width(),
                self.employee_name_box.height()
                + 8
            )
        )

        local_pos = self.mapFromGlobal(
            pos
        )

        menu.move(
            local_pos
        )

        self.employee_menu = menu

        menu.show()

        menu.raise_()

    # =====================================================
    # EMPLOYEE SELECTED
    # =====================================================

    def employee_selected(
        self,
        employee,
        menu,
        event
    ):

        self.select_employee(
            employee
        )

        menu.close()

        self.employee_menu = None

        event.accept()

    # =====================================================
    # SELECT EMPLOYEE
    # =====================================================

    def select_employee(
        self,
        employee
    ):

        self.selected_employee = employee

        self.employee_name_label.setText(
            employee["name"]
        )

        self.employee_position.setText(
            employee["position"]
        )

        self.entry_time = None

        self.exit_time = None

        self.entry_box.findChild(
            QLabel,
            "time_value"
        ).setText(
            "—"
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
            "—"
        )

        self.delay_box.findChild(
            QLabel,
            "small_value"
        ).setText(
            "۰ دقیقه"
        )

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
            "۸ ساعت"
        )

        self.status_value.setText(
            "ثبت نشده"
        )

        self.entry_button.setEnabled(
            True
        )

        self.exit_button.setEnabled(
            False
        )

    # =====================================================
    # INFO CARD
    # =====================================================

    def create_info_card(
        self,
        title_text,
        value_text
    ):

        card = QFrame()

        card.setObjectName(
            "infoCard"
        )

        card.setFixedHeight(
            52
        )

        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            10,
            5,
            10,
            5
        )

        layout.setSpacing(
            8
        )

        title = QLabel(
            title_text
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setStyleSheet("""
            QLabel {
                background: #F5F8FC;
                color: #7890A8;
                font-size: 9px;
                border-radius: 18px;
                padding: 5px 10px;
            }
        """)

        value = QLabel(
            value_text
        )

        value.setObjectName(
            "value"
        )

        value.setAlignment(
            Qt.AlignCenter
        )

        value.setStyleSheet("""
            QLabel {
                background: #EAF3FF;
                color: #1961C7;
                font-size: 14px;
                font-weight: 700;
                border-radius: 18px;
                padding: 5px 12px;
            }
        """)

        layout.addWidget(
            title
        )

        layout.addStretch()

        layout.addWidget(
            value
        )

        return card

    # =====================================================
    # TIME BOX
    # =====================================================

    def create_time_box(
        self,
        title_text
    ):

        box = QFrame()

        box.setObjectName(
            "timeBox"
        )

        box.setMinimumHeight(
            64
        )

        box.setStyleSheet("""
            QFrame {
                background: #F5F8FC;
                border: 1px solid #E8EEF5;
                border-radius: 32px;
            }
        """)

        layout = QVBoxLayout(
            box
        )

        layout.setContentsMargins(
            10,
            5,
            10,
            5
        )

        layout.setSpacing(
            3
        )

        # =================================================
        # INNER TITLE BOX
        # =================================================

        title = QLabel(
            title_text
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setFixedHeight(
            21
        )

        title.setStyleSheet("""
            QLabel {
                color: #7890A8;
                font-size: 9px;
                background: #FFFFFF;
                border: none;
                border-radius: 11px;
                padding: 0px 12px;
            }
        """)

        # =================================================
        # INNER VALUE BOX
        # =================================================

        value = QLabel(
            "—"
        )

        value.setObjectName(
            "time_value"
        )

        value.setAlignment(
            Qt.AlignCenter
        )

        value.setFixedHeight(
            28
        )

        value.setStyleSheet("""
            QLabel {
                color: #17324D;
                font-size: 15px;
                font-weight: 700;
                background: #FFFFFF;
                border: none;
                border-radius: 14px;
                padding: 0px 12px;
            }
        """)

        layout.addWidget(
            title,
            0,
            Qt.AlignCenter
        )

        layout.addWidget(
            value,
            0,
            Qt.AlignCenter
        )

        return box

    # =====================================================
    # SMALL BOX
    # =====================================================

    def create_small_box(
        self,
        title_text,
        value_text
    ):

        box = QFrame()

        box.setObjectName(
            "smallBox"
        )

        box.setMinimumHeight(
            54
        )

        box.setStyleSheet("""
            QFrame {
                background: #F8FAFD;
                border: 1px solid #E8EEF5;
                border-radius: 27px;
            }
        """)

        layout = QVBoxLayout(
            box
        )

        layout.setContentsMargins(
            10,
            5,
            10,
            5
        )

        layout.setSpacing(
            2
        )

        # =================================================
        # INNER TITLE BOX
        # =================================================

        title = QLabel(
            title_text
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setFixedHeight(
            20
        )

        title.setStyleSheet("""
            QLabel {
                color: #7890A8;
                font-size: 9px;
                background: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 0px 11px;
            }
        """)

        # =================================================
        # INNER VALUE BOX
        # =================================================

        value = QLabel(
            value_text
        )

        value.setObjectName(
            "small_value"
        )

        value.setAlignment(
            Qt.AlignCenter
        )

        value.setFixedHeight(
            25
        )

        value.setStyleSheet("""
            QLabel {
                color: #1961C7;
                font-size: 11px;
                font-weight: 700;
                background: #FFFFFF;
                border: none;
                border-radius: 13px;
                padding: 0px 10px;
            }
        """)

        layout.addWidget(
            title,
            0,
            Qt.AlignCenter
        )

        layout.addWidget(
            value,
            0,
            Qt.AlignCenter
        )

        return box

    # =====================================================
    # CLOCK
    # =====================================================

    def update_clock(self):

        now = QTime.currentTime()

        self.clock_value.setText(
            now.toString(
                "HH:mm:ss"
            )
        )

        if (
            self.entry_time
            and not self.exit_time
        ):

            self.update_live_calculations()

    # =====================================================
    # CURRENT MINUTE
    # =====================================================

    def current_minute_time(self):

        now = QTime.currentTime()

        return QTime(
            now.hour(),
            now.minute(),
            0
        )

    # =====================================================
    # REGISTER ENTRY
    # =====================================================

    def register_entry(self):

        if not self.selected_employee:
            return

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

    # =====================================================
    # REGISTER EXIT
    # =====================================================

    def register_exit(self):

        if not self.entry_time:
            return

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

    # =====================================================
    # CALCULATE WORK TIME
    # =====================================================

    def calculate_work_time(self):

        if (
            not self.entry_time
            or not self.exit_time
        ):
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

    # =====================================================
    # LIVE CALCULATIONS
    # =====================================================

    def update_live_calculations(self):

        if not self.entry_time:
            return

        current = (
            self.current_minute_time()
        )

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

    # =====================================================
    # DELAY
    # =====================================================

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

                text = (
                    f"{minutes} دقیقه"
                )

        self.delay_box.findChild(
            QLabel,
            "small_value"
        ).setText(
            text
        )

    # =====================================================
    # OVERTIME
    # =====================================================

    def calculate_overtime(self):

        if not self.entry_time:
            return

        current_time = (
            self.exit_time
            if self.exit_time
            else self.current_minute_time()
        )

        overtime_seconds = (
            self.work_end.secsTo(
                current_time
            )
        )

        if overtime_seconds <= 0:

            text = "۰ دقیقه"

        else:

            minutes = (
                overtime_seconds // 60
            )

            hours = minutes // 60

            minutes = minutes % 60

            if hours > 0:

                text = (
                    f"{hours} ساعت و "
                    f"{minutes} دقیقه"
                )

            else:

                text = (
                    f"{minutes} دقیقه"
                )

        self.overtime_box.findChild(
            QLabel,
            "small_value"
        ).setText(
            text
        )

    # =====================================================
    # REMAINING WORK
    # =====================================================

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

    # =====================================================
    # STATUS
    # =====================================================

    def calculate_status(self):

        if not self.entry_time:
            return "غیبت"

        if self.entry_time > self.work_start:
            return "تأخیر"

        return "حاضر"

    # =====================================================
    # FORMAT DURATION
    # =====================================================

    def format_duration(
        self,
        hours,
        minutes
    ):

        if hours == 0:

            return (
                f"{minutes} دقیقه"
            )

        if minutes == 0:

            return (
                f"{hours} ساعت"
            )

        return (
            f"{hours} ساعت و "
            f"{minutes} دقیقه"
        )

    # =====================================================
    # HISTORY ROW
    # =====================================================

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
            13,
            5,
            13,
            5
        )

        layout.setSpacing(
            10
        )

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
                    border-radius: 10px;
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
                    border-radius: 10px;
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
                    border-radius: 10px;
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