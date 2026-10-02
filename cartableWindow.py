import os
from datetime import datetime, date

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar, QDialog
)

from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QPainter, QColor

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

def jalali_str(d):
    if isinstance(d, datetime):
        jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
        return f"{jy:04d}/{jm:02d}/{jd:02d}"
    if isinstance(d, date):
        jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
        return f"{jy:04d}/{jm:02d}/{jd:02d}"
    return str(d) if d else "-"

def format_money(amount):
    try:
        return f"{amount:,.0f}"
    except Exception:
        return "0"

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
# CARTABLE WINDOW
# =========================================================

class CartableWindow(QWidget):

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
        self.all_items = []
        self.current_filter = "all"

        self.setWindowTitle(tr("cartable_title"))
        self.setMinimumSize(500, 400)
        self.resize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("cartableWindow")

        self.load_user_id()
        self.setup_ui()
        self.load_items()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)
        signals.employee_added.connect(self.on_employee_changed)
        signals.employee_updated.connect(self.on_employee_changed)
        signals.data_changed.connect(self.on_data_changed)

    # =====================================================
    # THEME / LANGUAGE
    # =====================================================

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("cartable_title"))
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
        self.load_items()

    def on_employee_changed(self, complex_id):
        if complex_id == self.complex_id:
            self.load_items()

    def on_data_changed(self, kind):
        # وقتی حضور یا مالی عوض شد، کارتابل رو رفرش کن
        if kind in ("all", "jobs", "attendance", "finance"):
            self.load_items()

    # =====================================================
    # LOAD USER
    # =====================================================

    def load_user_id(self):
        if not self.phone_number:
            return
        try:
            user = self.db.fetch_one(
                "SELECT userId FROM users WHERE phoneNumber = %s LIMIT 1",
                (self.phone_number,)
            )
            if user:
                self.user_id = user["userId"]
        except Exception as e:
            print("CARTABLE LOAD USER ID ERROR:", e)

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # HEADER
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(38, 38)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.close)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title = QLabel(tr("cartable_title"))
        title.setObjectName("cartableTitle")

        subtitle = QLabel(tr("cartable_subtitle"))
        subtitle.setObjectName("cartableSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # FILTER BOX
        filter_box = QFrame()
        filter_box.setObjectName("filterBox")
        filter_box.setAttribute(Qt.WA_StyledBackground, True)

        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setContentsMargins(10, 8, 10, 8)
        filter_layout.setSpacing(6)

        self.filter_buttons = []

        filter_defs = [
            ("all", tr("cartable_all")),
            ("pending", tr("cartable_pending")),
            ("inProgress", tr("cartable_in_progress")),
            ("completed", tr("cartable_completed")),
            ("rejected", tr("cartable_rejected")),
            ("cancelled", tr("cartable_cancelled")),
        ]

        for key, label in filter_defs:
            btn = QPushButton(label)
            btn.setObjectName("filterButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setAttribute(Qt.WA_StyledBackground, True)
            btn.clicked.connect(lambda checked=False, k=key: self.change_filter(k))
            filter_layout.addWidget(btn)
            self.filter_buttons.append((key, btn))

        filter_layout.addStretch()
        main_layout.addWidget(filter_box)

        # RECORDS BOX
        records_box = QFrame()
        records_box.setObjectName("recordsBox")
        records_box.setAttribute(Qt.WA_StyledBackground, True)

        records_layout = QVBoxLayout(records_box)
        records_layout.setContentsMargins(14, 14, 14, 14)
        records_layout.setSpacing(8)

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
        records_layout.addWidget(self.scroll)

        main_layout.addWidget(records_box, 1)

        self.apply_stylesheet()
        self.update_filter_buttons()

    # =====================================================
    # APPLY STYLESHEET
    # =====================================================

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""

        QWidget#cartableWindow {{
            background-color: {c['bg_main']};
            font-family: Vazirmatn;
            color: {c['text_main']};
        }}

        QLabel#cartableTitle {{
            color: {c['text_main']};
            font-size: 20px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#cartableSubtitle {{
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

        QFrame#filterBox {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 18px;
        }}

        QPushButton#filterButton {{
            background-color: {c['bg_input']};
            color: {c['text_dim']};
            border: 1px solid {c['border']};
            border-radius: 16px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 600;
            min-width: 55px;
            min-height: 22px;
        }}

        QPushButton#filterButton:hover {{
            background-color: {c['bg_hover']};
            color: {c['accent']};
            border-color: {c['border_hover']};
        }}

        QPushButton#filterButton[active="true"] {{
            background-color: {c['accent']};
            color: white;
            border-color: {c['accent']};
        }}

        QFrame#recordsBox {{
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

        QFrame#itemCard {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 16px;
        }}

        QFrame#itemCard:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['accent']};
        }}

        QLabel#itemTitle {{
            color: {c['text_main']};
            font-size: 13px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#itemName {{
            color: {c['accent']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }}

        QLabel#itemInfo {{
            color: {c['text_dim']};
            font-size: 10px;
            background: transparent;
        }}

        QLabel#itemDesc {{
            color: {c['text_dim']};
            font-size: 11px;
            background: transparent;
        }}

        QLabel#statusPending {{
            color: {c['warning']};
            background-color: {c['warning_bg']};
            border: none;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#statusInProgress {{
            color: {c['accent']};
            background-color: {c['accent_light']};
            border: none;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#statusCompleted {{
            color: #16A34A;
            background-color: {c['success_bg']};
            border: none;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#statusRejected {{
            color: {c['danger']};
            background-color: {c['danger_bg']};
            border: none;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#statusCancelled {{
            color: {c['text_dim']};
            background-color: {c['bg_input']};
            border: none;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QPushButton#approveBtn {{
            background-color: {c['success_bg']};
            color: #16A34A;
            border: none;
            border-radius: 14px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            min-height: 28px;
        }}

        QPushButton#approveBtn:hover {{
            background-color: {c['bg_hover']};
        }}

        QPushButton#rejectBtn {{
            background-color: {c['danger_bg']};
            color: {c['danger']};
            border: none;
            border-radius: 14px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            min-height: 28px;
        }}

        QPushButton#rejectBtn:hover {{
            background-color: {c['bg_hover']};
        }}

        QLabel#emptyLabel {{
            color: {c['text_dim']};
            font-size: 13px;
            padding: 40px;
            background: transparent;
        }}

        """)

    # =====================================================
    # FILTER
    # =====================================================

    def change_filter(self, key):
        self.current_filter = key
        self.refresh_records()
        self.update_filter_buttons()

    def update_filter_buttons(self):
        for key, btn in self.filter_buttons:
            btn.setProperty("active", key == self.current_filter)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    # =====================================================
    # LOAD ITEMS FROM DB
    # =====================================================

    def load_items(self):
        self.all_items = []

        if not self.complex_id:
            self.refresh_records()
            return

        try:
            rows = self.db.fetch_all(
                """
                SELECT ej.employeeJobId, ej.jobId, ej.memberId, ej.assignedBy,
                       ej.assignedDate, ej.startDate, ej.deadline, ej.quantity,
                       ej.price, ej.status, ej.description, ej.completedDate,
                       u.name AS employee_name,
                       au.name AS assigner_name,
                       j.jobTitle
                FROM employee_jobs ej
                INNER JOIN complex_members cm ON cm.memberId = ej.memberId
                INNER JOIN users u ON u.userId = cm.userId
                LEFT JOIN users au ON au.userId = ej.assignedBy
                LEFT JOIN jobs j ON j.jobId = ej.jobId
                WHERE cm.complexId = %s
                ORDER BY ej.assignedDate DESC
                LIMIT 100
                """,
                (self.complex_id,)
            )

            for r in rows or []:
                self.all_items.append({
                    "id": r["employeeJobId"],
                    "job_id": r.get("jobId"),
                    "member_id": r.get("memberId"),
                    "title": r.get("jobTitle") or tr("job_no_desc"),
                    "employee_name": r.get("employee_name") or "—",
                    "assigner_name": r.get("assigner_name") or "—",
                    "start_date": r.get("startDate"),
                    "deadline": r.get("deadline"),
                    "quantity": r.get("quantity"),
                    "price": r.get("price"),
                    "status": (r.get("status") or "pending"),
                    "description": r.get("description") or "",
                    "completed_date": r.get("completedDate"),
                })

        except Exception as e:
            print("CARTABLE LOAD ERROR:", e)

        self.refresh_records()

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_records(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if self.current_filter == "all":
            filtered = self.all_items
        else:
            filtered = [i for i in self.all_items if i["status"] == self.current_filter]

        if not filtered:
            empty = QLabel(tr("no_cartable_items"))
            empty.setObjectName("emptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty)
            self.scroll_layout.addStretch()
            return

        for it in filtered:
            self.scroll_layout.addWidget(self.create_item_card(it))

        self.scroll_layout.addStretch()

    # =====================================================
    # ITEM CARD
    # =====================================================

    def create_item_card(self, item):

        card = QFrame()
        card.setObjectName("itemCard")
        card.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        title = QLabel(item["title"])
        title.setObjectName("itemTitle")
        title.setWordWrap(True)

        emp = QLabel(f"{tr('job_assigned_to')}: {item['employee_name']}")
        emp.setObjectName("itemName")

        info1 = QLabel(
            f"{tr('job_start_date')}: {jalali_str(item['start_date'])}   •   "
            f"{tr('job_deadline')}: {jalali_str(item['deadline'])}"
        )
        info1.setObjectName("itemInfo")

        qty_text = f"{item['quantity']:g}" if item.get("quantity") else "-"
        price_text = f"{format_money(item['price'])} {tr('toman')}" if item.get("price") else "-"
        info2 = QLabel(f"{tr('job_quantity')}: {qty_text}   •   {tr('job_price')}: {price_text}")
        info2.setObjectName("itemInfo")

        text_col.addWidget(title)
        text_col.addWidget(emp)
        text_col.addWidget(info1)
        text_col.addWidget(info2)

        if item.get("description"):
            desc = QLabel(item["description"])
            desc.setObjectName("itemDesc")
            desc.setWordWrap(True)
            text_col.addWidget(desc)

        layout.addLayout(text_col, 1)

        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.setAlignment(Qt.AlignTop)

        status = item["status"]
        if status == "completed":
            badge = QLabel(tr("cartable_completed"))
            badge.setObjectName("statusCompleted")
        elif status == "inProgress":
            badge = QLabel(tr("cartable_in_progress"))
            badge.setObjectName("statusInProgress")
        elif status == "rejected":
            badge = QLabel(tr("cartable_rejected"))
            badge.setObjectName("statusRejected")
        elif status == "cancelled":
            badge = QLabel(tr("cartable_cancelled"))
            badge.setObjectName("statusCancelled")
        else:
            badge = QLabel(tr("cartable_pending"))
            badge.setObjectName("statusPending")

        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(26)
        right_col.addWidget(badge)

        if status == "pending":
            approve_btn = QPushButton(tr("approve_job"))
            approve_btn.setObjectName("approveBtn")
            approve_btn.setCursor(Qt.PointingHandCursor)
            approve_btn.clicked.connect(lambda checked=False, i=item: self.approve_item(i))
            right_col.addWidget(approve_btn)

            reject_btn = QPushButton(tr("reject_job"))
            reject_btn.setObjectName("rejectBtn")
            reject_btn.setCursor(Qt.PointingHandCursor)
            reject_btn.clicked.connect(lambda checked=False, i=item: self.reject_item(i))
            right_col.addWidget(reject_btn)

        right_col.addStretch()
        layout.addLayout(right_col)

        return card

    # =====================================================
    # APPROVE / REJECT
    # =====================================================

    def approve_item(self, item):
        item_id = item["id"]

        try:
            self.db.execute(
                """
                UPDATE employee_jobs
                SET status = 'completed', completedDate = NOW()
                WHERE employeeJobId = %s
                """,
                (item_id,)
            )

            if self.user_id:
                self.db.execute(
                    """
                    INSERT INTO job_approvals (employeeJobId, approvedBy, status, approvalDate)
                    VALUES (%s, %s, 'approved', NOW())
                    """,
                    (item_id, self.user_id)
                )

            self.load_items()

            # ─── به بقیه پنجره‌ها خبر بده ───
            signals.data_changed.emit("jobs")

            NiceMessageBox.success(
                self, tr("job_approved"),
                tr("job_approved_msg", name=item.get("employee_name", ""))
            )

        except Exception as e:
            print("APPROVE ERROR:", e)
            NiceMessageBox.error(self, tr("error"), tr("job_approve_failed"))

    def reject_item(self, item):
        item_id = item["id"]

        try:
            self.db.execute(
                """
                UPDATE employee_jobs
                SET status = 'rejected'
                WHERE employeeJobId = %s
                """,
                (item_id,)
            )

            if self.user_id:
                self.db.execute(
                    """
                    INSERT INTO job_approvals (employeeJobId, approvedBy, status, approvalDate)
                    VALUES (%s, %s, 'rejected', NOW())
                    """,
                    (item_id, self.user_id)
                )

            self.load_items()
            signals.data_changed.emit("jobs")

            NiceMessageBox.warning(
                self, tr("job_rejected"),
                tr("job_rejected_msg", name=item.get("employee_name", ""))
            )

        except Exception as e:
            print("REJECT ERROR:", e)
            NiceMessageBox.error(self, tr("error"), tr("job_reject_failed"))