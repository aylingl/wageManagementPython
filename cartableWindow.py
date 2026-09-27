from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QDialog,
    QLineEdit
)

from PySide6.QtCore import Qt, QTime

class CartableWindow(QWidget):

    def __init__(self, parent_window=None):

        super().__init__()

        self.parent_window = parent_window

        self.setWindowTitle("کارتابل")

        self.setMinimumSize(
            900,
            620
        )

        self.setLayoutDirection(
            Qt.RightToLeft
        )

        self.setup_ui()

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            28,
            22,
            28,
            22
        )

        main_layout.setSpacing(
            16
        )

        # =================================================
        # HEADER
        # =================================================

        header_layout = QHBoxLayout()

        header_layout.setContentsMargins(
            4,
            0,
            4,
            0
        )

        header_layout.setSpacing(
            12
        )

        # -----------------------------------------------
        # BACK
        # -----------------------------------------------

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

        # -----------------------------------------------
        # TITLE
        # -----------------------------------------------

        header_text = QVBoxLayout()

        header_text.setSpacing(
            4
        )

        title = QLabel(
            "کارتابل"
        )

        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "درخواست‌ها و مواردی که نیاز به بررسی شما دارند"
        )

        subtitle.setObjectName(
            "pageSubtitle"
        )

        header_text.addWidget(
            title
        )

        header_text.addWidget(
            subtitle
        )

        header_layout.addLayout(
            header_text
        )

        header_layout.addStretch()

        main_layout.addLayout(
            header_layout
        )

        # =================================================
        # CATEGORY BAR
        # =================================================

        category_box = QFrame()

        category_box.setObjectName(
            "categoryBox"
        )

        category_layout = QHBoxLayout(
            category_box
        )

        category_layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        category_layout.setSpacing(
            8
        )

        attendance_btn = self.create_category_button(
            "🕒",
            "حضور و غیاب"
        )

        leave_btn = self.create_category_button(
            "📅",
            "مرخصی"
        )

        overtime_btn = self.create_category_button(
            "⏱",
            "اضافه‌کاری"
        )

        loan_btn = self.create_category_button(
            "💳",
            "درخواست وام"
        )

        category_layout.addWidget(
            attendance_btn
        )

        category_layout.addWidget(
            leave_btn
        )

        category_layout.addWidget(
            overtime_btn
        )

        category_layout.addWidget(
            loan_btn
        )

        main_layout.addWidget(
            category_box
        )

        # =================================================
        # SCROLL
        # =================================================

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        content = QWidget()

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            4,
            4,
            4,
            10
        )

        content_layout.setSpacing(
            12
        )

        # =================================================
        # ATTENDANCE
        # =================================================

        content_layout.addWidget(
            self.create_section_title(
                "🕒",
                "حضور و غیاب"
            )
        )

        content_layout.addWidget(
            self.create_attendance_card(
                "علی رضایی",
                "امروز",
                "08:12",
                "17:03"
            )
        )

        content_layout.addWidget(
            self.create_attendance_card(
                "سارا محمدی",
                "امروز",
                "08:35",
                "16:20"
            )
        )

        # =================================================
        # LEAVE
        # =================================================

        content_layout.addWidget(
            self.create_section_title(
                "📅",
                "درخواست مرخصی"
            )
        )

        content_layout.addWidget(
            self.create_leave_card(
                "سارا محمدی",
                "۲ روز",
                "۱۴۰۵/۰۷/۰۵ تا ۱۴۰۵/۰۷/۰۶",
                "مرخصی شخصی"
            )
        )

        # =================================================
        # OVERTIME
        # =================================================

        content_layout.addWidget(
            self.create_section_title(
                "⏱",
                "درخواست اضافه‌کاری"
            )
        )

        content_layout.addWidget(
            self.create_overtime_card(
                "محمد احمدی",
                "۲ ساعت",
                "امروز",
                "تکمیل کارهای پایان ماه"
            )
        )

        # =================================================
        # LOAN
        # =================================================

        content_layout.addWidget(
            self.create_section_title(
                "💳",
                "درخواست وام"
            )
        )

        content_layout.addWidget(
            self.create_loan_card(
                "علی رضایی",
                "۵۰,۰۰۰,۰۰۰ تومان",
                "۱۲ ماه",
                "خرید لوازم ضروری",
                "۱۴۰۵/۰۷/۰۱"
            )
        )

        content_layout.addStretch()

        self.scroll.setWidget(
            content
        )

        main_layout.addWidget(
            self.scroll
        )

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet("""
            QWidget {
                background: #F5F8FC;
                font-family: "Vazirmatn";
            }

            QLabel#pageTitle {
                color: #1E2F43;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                color: #8290A1;
                font-size: 13px;
            }

            QPushButton#backButton {
                background: white;
                color: #1961C7;
                border: 1px solid #E2EAF4;
                border-radius: 12px;
                font-size: 28px;
                font-weight: 500;
            }

            QPushButton#backButton:hover {
                background: #EAF3FF;
            }

            QFrame#categoryBox {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 16px;
            }

            QPushButton#categoryButton {
                background: #F5F8FC;
                color: #536477;
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
                font-size: 13px;
            }

            QPushButton#categoryButton:hover {
                background: #EAF3FF;
                color: #1961C7;
            }

            QFrame#requestCard {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 18px;
            }

            QFrame#requestCard:hover {
                border: 1px solid #C8DDF5;
                background: #FBFDFF;
            }

            QLabel#employeeName {
                color: #1E2F43;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#requestDate {
                color: #8290A1;
                font-size: 12px;
            }

            QLabel#infoLabel {
                color: #65758A;
                font-size: 12px;
            }

            QLabel#infoValue {
                color: #1E2F43;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#sectionTitle {
                color: #1E2F43;
                font-size: 15px;
                font-weight: 700;
            }

            QPushButton#approveButton {
                background: #1961C7;
                color: white;
                border: none;
                border-radius: 9px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#approveButton:hover {
                background: #4589E8;
            }

            QPushButton#editButton {
                background: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 9px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#editButton:hover {
                background: #DCEBFF;
            }

            QPushButton#rejectButton {
                background: #F4F6F9;
                color: #697789;
                border: none;
                border-radius: 9px;
                padding: 8px 16px;
                font-size: 12px;
            }

            QPushButton#rejectButton:hover {
                background: #E9EDF2;
                color: #4E5C6C;
            }

            QScrollBar:vertical {
                width: 6px;
                background: transparent;
                margin: 4px 0 4px 0;
            }

            QScrollBar::handle:vertical {
                background: #4589E8;
                border-radius: 3px;
                min-height: 30px;
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

    # =====================================================
    # CATEGORY BUTTON
    # =====================================================

    def create_category_button(
        self,
        icon,
        text
    ):

        button = QPushButton(
            f"{icon}  {text}"
        )

        button.setObjectName(
            "categoryButton"
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        return button

    # =====================================================
    # SECTION TITLE
    # =====================================================

    def create_section_title(
        self,
        icon,
        text
    ):

        label = QLabel(
            f"{icon}  {text}"
        )

        label.setObjectName(
            "sectionTitle"
        )

        label.setContentsMargins(
            4,
            8,
            4,
            2
        )

        return label

    # =====================================================
    # ATTENDANCE CARD
    # =====================================================

    def create_attendance_card(
        self,
        name,
        date,
        start_time,
        end_time
    ):

        card = QFrame()

        card.setObjectName(
            "requestCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        layout.setSpacing(
            10
        )

        # -----------------------------------------------
        # HEADER
        # -----------------------------------------------

        header = QHBoxLayout()

        employee = QLabel(
            name
        )

        employee.setObjectName(
            "employeeName"
        )

        date_label = QLabel(
            date
        )

        date_label.setObjectName(
            "requestDate"
        )

        header.addWidget(
            employee
        )

        header.addStretch()

        header.addWidget(
            date_label
        )

        layout.addLayout(
            header
        )

        # -----------------------------------------------
        # INFO
        # -----------------------------------------------

        info_layout = QHBoxLayout()

        info_layout.setSpacing(
            28
        )

        info_layout.addLayout(
            self.create_info_item(
                "ورود",
                start_time
            )
        )

        info_layout.addLayout(
            self.create_info_item(
                "خروج",
                end_time
            )
        )

        duration = self.calculate_duration(
            start_time,
            end_time
        )

        duration_label = QLabel(
            duration
        )

        duration_label.setObjectName(
            "durationValue"
        )

        duration_layout = QVBoxLayout()

        duration_title = QLabel(
            "مدت کار"
        )

        duration_title.setObjectName(
            "infoLabel"
        )

        duration_layout.addWidget(
            duration_title
        )

        duration_layout.addWidget(
            duration_label
        )

        info_layout.addLayout(
            duration_layout
        )

        info_layout.addStretch()

        layout.addLayout(
            info_layout
        )

        # -----------------------------------------------
        # BUTTONS
        # -----------------------------------------------

        buttons = QHBoxLayout()

        buttons.setSpacing(
            8
        )

        approve = QPushButton(
            "✓ تأیید"
        )

        approve.setObjectName(
            "approveButton"
        )

        approve.clicked.connect(
            lambda: self.remove_card(card)
        )

        edit = QPushButton(
            "✎ ویرایش"
        )

        edit.setObjectName(
            "editButton"
        )

        edit.clicked.connect(
            lambda: self.edit_attendance(
                card,
                name,
                date,
                start_time,
                end_time
            )
        )

        reject = QPushButton(
            "رد کردن"
        )

        reject.setObjectName(
            "rejectButton"
        )

        reject.clicked.connect(
            lambda: self.remove_card(card)
        )

        buttons.addWidget(
            approve
        )

        buttons.addWidget(
            edit
        )

        buttons.addWidget(
            reject
        )

        buttons.addStretch()

        layout.addLayout(
            buttons
        )

        return card

    # =====================================================
    # LEAVE CARD
    # =====================================================

    def create_leave_card(
        self,
        name,
        duration,
        dates,
        description
    ):

        card = QFrame()

        card.setObjectName(
            "requestCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        layout.setSpacing(
            10
        )

        header = QHBoxLayout()

        employee = QLabel(
            name
        )

        employee.setObjectName(
            "employeeName"
        )

        header.addWidget(
            employee
        )

        header.addStretch()

        date_label = QLabel(
            duration
        )

        date_label.setObjectName(
            "requestDate"
        )

        header.addWidget(
            date_label
        )

        layout.addLayout(
            header
        )

        info = QHBoxLayout()

        info.addLayout(
            self.create_info_item(
                "بازه مرخصی",
                dates
            )
        )

        info.addLayout(
            self.create_info_item(
                "نوع",
                description
            )
        )

        info.addStretch()

        layout.addLayout(
            info
        )

        buttons = self.create_action_buttons(
            card
        )

        layout.addLayout(
            buttons
        )

        return card

    # =====================================================
    # OVERTIME CARD
    # =====================================================

    def create_overtime_card(
        self,
        name,
        hours,
        date,
        description
    ):

        card = QFrame()

        card.setObjectName(
            "requestCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        layout.setSpacing(
            10
        )

        header = QHBoxLayout()

        employee = QLabel(
            name
        )

        employee.setObjectName(
            "employeeName"
        )

        header.addWidget(
            employee
        )

        header.addStretch()

        date_label = QLabel(
            date
        )

        date_label.setObjectName(
            "requestDate"
        )

        header.addWidget(
            date_label
        )

        layout.addLayout(
            header
        )

        info = QHBoxLayout()

        info.addLayout(
            self.create_info_item(
                "مدت اضافه‌کاری",
                hours
            )
        )

        info.addLayout(
            self.create_info_item(
                "توضیح",
                description
            )
        )

        info.addStretch()

        layout.addLayout(
            info
        )

        buttons = self.create_action_buttons(
            card
        )

        layout.addLayout(
            buttons
        )

        return card

    # =====================================================
    # LOAN CARD
    # =====================================================

    def create_loan_card(
        self,
        name,
        amount,
        installments,
        description,
        date
    ):

        card = QFrame()

        card.setObjectName(
            "requestCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        layout.setSpacing(
            10
        )

        header = QHBoxLayout()

        employee = QLabel(
            name
        )

        employee.setObjectName(
            "employeeName"
        )

        header.addWidget(
            employee
        )

        header.addStretch()

        date_label = QLabel(
            date
        )

        date_label.setObjectName(
            "requestDate"
        )

        header.addWidget(
            date_label
        )

        layout.addLayout(
            header
        )

        info = QHBoxLayout()

        info.addLayout(
            self.create_info_item(
                "مبلغ وام",
                amount
            )
        )

        info.addLayout(
            self.create_info_item(
                "تعداد اقساط",
                installments
            )
        )

        info.addLayout(
            self.create_info_item(
                "دلیل درخواست",
                description
            )
        )

        info.addStretch()

        layout.addLayout(
            info
        )

        buttons = self.create_action_buttons(
            card
        )

        layout.addLayout(
            buttons
        )

        return card

    # =====================================================
    # INFO ITEM
    # =====================================================

    def create_info_item(
        self,
        title,
        value
    ):

        layout = QVBoxLayout()

        layout.setSpacing(
            2
        )

        label = QLabel(
            title
        )

        label.setObjectName(
            "infoLabel"
        )

        value_label = QLabel(
            value
        )

        value_label.setObjectName(
            "infoValue"
        )

        layout.addWidget(
            label
        )

        layout.addWidget(
            value_label
        )

        return layout

    # =====================================================
    # ACTION BUTTONS
    # =====================================================

    def create_action_buttons(
        self,
        card
    ):

        buttons = QHBoxLayout()

        buttons.setSpacing(
            8
        )

        approve = QPushButton(
            "✓ تأیید"
        )

        approve.setObjectName(
            "approveButton"
        )

        approve.clicked.connect(
            lambda: self.remove_card(card)
        )

        reject = QPushButton(
            "رد کردن"
        )

        reject.setObjectName(
            "rejectButton"
        )

        reject.clicked.connect(
            lambda: self.remove_card(card)
        )

        buttons.addWidget(
            approve
        )

        buttons.addWidget(
            reject
        )

        buttons.addStretch()

        return buttons

    # =====================================================
    # CALCULATE DURATION
    # =====================================================

    def calculate_duration(
        self,
        start_time,
        end_time
    ):

        start = QTime.fromString(
            start_time,
            "HH:mm"
        )

        end = QTime.fromString(
            end_time,
            "HH:mm"
        )

        if not start.isValid() or not end.isValid():
            return "نامشخص"

        seconds = start.secsTo(
            end
        )

        if seconds < 0:
            seconds += 24 * 60 * 60

        hours = seconds // 3600

        minutes = (
            seconds % 3600
        ) // 60

        return f"{hours} ساعت و {minutes} دقیقه"

    # =====================================================
    # REMOVE CARD
    # =====================================================

    def remove_card(
        self,
        card
    ):

        card.deleteLater()

    # =====================================================
    # EDIT ATTENDANCE
    # =====================================================

    def edit_attendance(
        self,
        card,
        name,
        date,
        start_time,
        end_time
    ):

        dialog = QDialog(
            self
        )

        dialog.setWindowTitle(
            "ویرایش حضور و غیاب"
        )

        dialog.setFixedSize(
            430,
            340
        )

        dialog.setLayoutDirection(
            Qt.RightToLeft
        )

        layout = QVBoxLayout(
            dialog
        )

        layout.setContentsMargins(
            24,
            24,
            24,
            24
        )

        layout.setSpacing(
            12
        )

        title = QLabel(
            f"ویرایش حضور و غیاب {name}"
        )

        title.setObjectName(
            "editTitle"
        )

        layout.addWidget(
            title
        )

        date_label = QLabel(
            date
        )

        date_label.setObjectName(
            "requestDate"
        )

        layout.addWidget(
            date_label
        )

        # -----------------------------------------------
        # START
        # -----------------------------------------------

        start_label = QLabel(
            "ساعت ورود"
        )

        start_input = QLineEdit(
            start_time
        )

        start_input.setPlaceholderText(
            "مثلاً 08:00"
        )

        layout.addWidget(
            start_label
        )

        layout.addWidget(
            start_input
        )

        # -----------------------------------------------
        # END
        # -----------------------------------------------

        end_label = QLabel(
            "ساعت خروج"
        )

        end_input = QLineEdit(
            end_time
        )

        end_input.setPlaceholderText(
            "مثلاً 17:00"
        )

        layout.addWidget(
            end_label
        )

        layout.addWidget(
            end_input
        )

        layout.addStretch()

        # -----------------------------------------------
        # BUTTONS
        # -----------------------------------------------

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "ذخیره"
        )

        save_button.setObjectName(
            "approveButton"
        )

        cancel_button = QPushButton(
            "انصراف"
        )

        cancel_button.setObjectName(
            "rejectButton"
        )

        buttons.addWidget(
            save_button
        )

        buttons.addWidget(
            cancel_button
        )

        layout.addLayout(
            buttons
        )

        cancel_button.clicked.connect(
            dialog.reject
        )

        save_button.clicked.connect(
            lambda: self.save_attendance_edit(
                dialog,
                card,
                name,
                date,
                start_input,
                end_input
            )
        )

        dialog.setStyleSheet("""
            QDialog {
                background: #F5F8FC;
            }

            QLabel#editTitle {
                color: #1E2F43;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel {
                color: #65758A;
                font-size: 12px;
            }

            QLineEdit {
                background: white;
                border: 1px solid #E2EAF4;
                border-radius: 10px;
                padding: 10px 12px;
                color: #1E2F43;
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 1px solid #4589E8;
            }

            QPushButton#approveButton {
                background: #1961C7;
                color: white;
                border: none;
                border-radius: 9px;
                padding: 9px 18px;
                font-size: 12px;
                font-weight: 600;
            }

            QPushButton#approveButton:hover {
                background: #4589E8;
            }

            QPushButton#rejectButton {
                background: #EAF3FF;
                color: #1961C7;
                border: none;
                border-radius: 9px;
                padding: 9px 18px;
                font-size: 12px;
            }

            QPushButton#rejectButton:hover {
                background: #DCEBFF;
            }
        """)

        dialog.exec()

    # =====================================================
    # SAVE ATTENDANCE EDIT
    # =====================================================

    def save_attendance_edit(
        self,
        dialog,
        card,
        name,
        date,
        start_input,
        end_input
    ):

        start_time = start_input.text().strip()

        end_time = end_input.text().strip()

        start = QTime.fromString(
            start_time,
            "HH:mm"
        )

        end = QTime.fromString(
            end_time,
            "HH:mm"
        )

        if not start.isValid() or not end.isValid():
            return

        duration = self.calculate_duration(
            start_time,
            end_time
        )

        card.deleteLater()

        new_card = self.create_attendance_card(
            name,
            date,
            start_time,
            end_time
        )

        parent = self.scroll.widget()

        content_layout = parent.layout()

        # پیدا کردن محل مناسب برای کارت جدید
        for i in range(
            content_layout.count()
        ):

            item = content_layout.itemAt(
                i
            )

            widget = item.widget()

            if widget:

                title = widget.findChild(
                    QLabel,
                    "employeeName"
                )

                if title and title.text() == name:
                    content_layout.insertWidget(
                        i,
                        new_card
                    )
                    break

        dialog.accept()