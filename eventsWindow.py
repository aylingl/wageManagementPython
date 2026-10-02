import os
from datetime import datetime, date

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QScrollBar
)

from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QPainter, QColor

from database import Database
from theme import theme_manager
from signals import signals
from i18n import tr, set_language, get_language

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
        c = theme_manager.colors()

        track_width = 6
        track_x = (self.width() - track_width) / 2
        track_top = 6
        track_bottom = self.height() - 6
        track_height = track_bottom - track_top

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(c["bg_input"]))
        painter.drawRoundedRect(
            int(track_x), int(track_top),
            track_width, int(track_height),
            track_width / 2, track_width / 2
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
        painter.drawRoundedRect(
            int(handle_x), int(handle_y),
            handle_width, int(handle_height),
            handle_width / 2, handle_width / 2
        )

# =========================================================
# JALALI HELPERS
# =========================================================

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (355666 + (365 * gy) + ((gy2 + 3) // 4)
            - ((gy2 + 99) // 100) + ((gy2 + 399) // 400)
            + gd + g_d_m[gm - 1])
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

def jalali_string_from_date(d):
    if isinstance(d, datetime):
        qdate = QDate(d.year, d.month, d.day)
        jy, jm, jd = gregorian_to_jalali(qdate.year(), qdate.month(), qdate.day())
        return f"{jy:04d}/{jm:02d}/{jd:02d} - {d.strftime('%H:%M')}"
    elif isinstance(d, date):
        jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
        return f"{jy:04d}/{jm:02d}/{jd:02d}"
    return str(d)

def format_money(amount):
    try:
        return f"{amount:,.0f}"
    except Exception:
        return "0"

# =========================================================
# EVENTS WINDOW
# =========================================================

class EventsWindow(QWidget):

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
        self.all_events = []
        self.current_filter = "all"

        self.setWindowTitle(tr("events_title"))
        self.setMinimumSize(500, 400)
        self.resize(900, 620)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("eventsWindow")

        self.load_user_id()
        self.setup_ui()
        self.load_events()

        theme_manager.theme_changed.connect(self.on_theme_changed)
        signals.language_changed.connect(self.on_language_changed)
        signals.data_changed.connect(self.on_data_changed)

    # =====================================================
    # THEME / LANGUAGE / DATA
    # =====================================================

    def on_theme_changed(self, theme_name):
        self.apply_stylesheet()

    def on_language_changed(self, lang):
        set_language(lang)
        self.setWindowTitle(tr("events_title"))
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
        self.load_events()

    def on_data_changed(self, kind):
        # هر بار دیتا عوض شد، رفرش کن
        self.load_events()

    # =====================================================
    # LOAD USER ID
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
            print("LOAD USER ID ERROR:", e)

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        # HEADER
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        back_button = QPushButton("›")
        back_button.setObjectName("backButton")
        back_button.setFixedSize(42, 42)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setAttribute(Qt.WA_StyledBackground, True)
        back_button.clicked.connect(self.go_back)

        header_layout.addWidget(back_button)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel(tr("events_title"))
        title.setObjectName("title")

        subtitle = QLabel(tr("events_subtitle"))
        subtitle.setObjectName("subtitle")

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
        filter_layout.setContentsMargins(14, 12, 14, 12)
        filter_layout.setSpacing(7)

        filter_label = QLabel(tr("show_records"))
        filter_label.setObjectName("filterLabel")
        filter_layout.addWidget(filter_label)

        self.filter_buttons = []

        filter_defs = [
            ("all", tr("filter_all")),
            ("payment", tr("filter_payments")),
            ("attendance", tr("filter_attendance")),
            ("leave", tr("filter_leaves")),
            ("loan", tr("filter_loans")),
            ("other", tr("filter_others")),
        ]

        for key, label in filter_defs:
            btn = QPushButton(label)
            btn.setObjectName("filterButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setAttribute(Qt.WA_StyledBackground, True)
            btn.clicked.connect(
                lambda checked=False, k=key: self.change_filter(k)
            )
            filter_layout.addWidget(btn)
            self.filter_buttons.append((key, btn))

        filter_layout.addStretch()

        main_layout.addWidget(filter_box)

        # RECORDS BOX
        records_box = QFrame()
        records_box.setObjectName("recordsBox")
        records_box.setAttribute(Qt.WA_StyledBackground, True)

        records_layout = QVBoxLayout(records_box)
        records_layout.setContentsMargins(20, 20, 20, 20)
        records_layout.setSpacing(12)

        records_title = QLabel(tr("records_recorded"))
        records_title.setObjectName("sectionTitle")

        records_layout.addWidget(records_title)

        # SCROLL
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
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(6, 6, 11, 6)

        self.scroll.setWidget(scroll_content)

        records_layout.addWidget(self.scroll)

        main_layout.addWidget(records_box)

        self.apply_stylesheet()
        self.update_filter_buttons()

    # =====================================================
    # APPLY STYLESHEET
    # =====================================================

    def apply_stylesheet(self):
        c = theme_manager.colors()

        self.setStyleSheet(f"""

        QWidget#eventsWindow {{
            background-color: {c['bg_main']};
            font-family: "Vazirmatn";
            color: {c['text_main']};
        }}

        QLabel#title {{
            color: {c['text_main']};
            font-size: 21px;
            font-weight: 700;
            background: transparent;
        }}

        QLabel#subtitle {{
            color: {c['text_dim']};
            font-size: 11px;
            background: transparent;
        }}

        QPushButton#backButton {{
            background-color: {c['bg_card']};
            color: {c['accent']};
            border: 1px solid {c['border']};
            border-radius: 21px;
            font-size: 22px;
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
            border-radius: 20px;
        }}

        QLabel#filterLabel {{
            color: {c['text_main']};
            font-size: 13px;
            font-weight: 600;
            background: transparent;
            border: none;
            padding-right: 6px;
        }}

        QPushButton#filterButton {{
            background-color: {c['bg_input']};
            color: {c['text_dim']};
            border: 1px solid {c['border']};
            border-radius: 18px;
            padding: 7px 14px;
            font-size: 12px;
            font-weight: 600;
            min-width: 60px;
            min-height: 24px;
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
            border-radius: 20px;
        }}

        QLabel#sectionTitle {{
            color: {c['text_main']};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            border: none;
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
            border: none;
        }}

        QFrame#recordCard {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 16px;
        }}

        QFrame#recordCard:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['accent']};
        }}

        QFrame#recordCard QLabel {{
            background: transparent;
            border: none;
        }}

        QLabel#recordTitle {{
            color: {c['text_main']};
            font-size: 14px;
            font-weight: 700;
        }}

        QLabel#recordInfo {{
            color: {c['text_dim']};
            font-size: 12px;
        }}

        QLabel#recordDate {{
            color: {c['text_dim']};
            font-size: 11px;
        }}

        QLabel#categoryBadge {{
            color: {c['accent']};
            background-color: {c['accent_light']};
            border: none;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
        }}

        QLabel#emptyLabel {{
            color: {c['text_dim']};
            font-size: 14px;
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
    # LOAD EVENTS FROM DATABASE
    # =====================================================

    def load_events(self):
        self.all_events = []

        if not self.complex_id:
            self.refresh_records()
            return

        try:
            # ─── Payments ───
            payments = self.db.fetch_all(
                """
                SELECT p.paymentId, p.amount, p.paymentType, p.paymentDate,
                       p.description, u.name
                FROM payments p
                INNER JOIN complex_members cm ON cm.memberId = p.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                ORDER BY p.paymentDate DESC LIMIT 50
                """,
                (self.complex_id,)
            )

            payment_type_map = {
                "salary": tr("payment_salary"),
                "job": tr("payment_job"),
                "bonus": tr("payment_bonus"),
                "advance": tr("payment_advance"),
                "other": tr("payment_other"),
            }

            for p in payments or []:
                ptype = payment_type_map.get(p["paymentType"], tr("salary_type_pay"))
                desc = p.get("description") or f"{format_money(p['amount'])} {tr('toman')}"
                self.all_events.append({
                    "type": f"{ptype} — {p.get('name') or '—'}",
                    "category": "payment",
                    "description": desc,
                    "date": p["paymentDate"]
                })

            # ─── Attendance ───
            attendances = self.db.fetch_all(
                """
                SELECT a.attendanceId, a.workDate, a.checkIn, a.checkOut,
                       a.approvalStatus, u.name
                FROM attendance a
                INNER JOIN complex_members cm ON cm.memberId = a.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                  AND a.approvalStatus IN ('approved', 'rejected')
                ORDER BY a.workDate DESC LIMIT 50
                """,
                (self.complex_id,)
            )

            for a in attendances or []:
                if a["approvalStatus"] == "approved":
                    status_text = tr("approved_msg")
                else:
                    status_text = tr("rejected_msg")

                work_date = a["workDate"]
                date_str = str(work_date) if work_date else "-"

                self.all_events.append({
                    "type": f"{status_text} — {a.get('name') or '—'}",
                    "category": "attendance",
                    "description": f"{tr('date')}: {date_str}",
                    "date": a["workDate"]
                })

            # ─── Leaves ───
            leaves = self.db.fetch_all(
                """
                SELECT l.leaveId, l.startDate, l.endDate, l.leaveType,
                       l.status, l.reason, u.name
                FROM leaves l
                INNER JOIN complex_members cm ON cm.memberId = l.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                ORDER BY l.createdDate DESC LIMIT 50
                """,
                (self.complex_id,)
            )

            for l in leaves or []:
                status_text = {
                    "approved": tr("approved"),
                    "rejected": tr("rejected"),
                    "pending": tr("pending"),
                }.get(l["status"], l["status"] or "-")

                desc = f"{l['startDate']} → {l['endDate']}"
                if l.get("reason"):
                    desc += f"\n{l['reason']}"

                self.all_events.append({
                    "type": f"{tr('filter_leaves')} ({status_text}) — {l.get('name') or '—'}",
                    "category": "leave",
                    "description": desc,
                    "date": l["startDate"]
                })

            # ─── Loans ───
            loans = self.db.fetch_all(
                """
                SELECT lo.loanId, lo.totalAmount, lo.installmentCount,
                       lo.startDate, lo.status, u.name
                FROM loans lo
                INNER JOIN complex_members cm ON cm.memberId = lo.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                ORDER BY lo.createdDate DESC LIMIT 50
                """,
                (self.complex_id,)
            )

            for lo in loans or []:
                desc = f"{format_money(lo['totalAmount'])} {tr('toman')} — {lo['installmentCount']}x"
                self.all_events.append({
                    "type": f"{tr('filter_loans')} — {lo.get('name') or '—'}",
                    "category": "loan",
                    "description": desc,
                    "date": lo["startDate"]
                })

            # ─── Bonuses ───
            bonuses = self.db.fetch_all(
                """
                SELECT b.bonusId, b.amount, b.title, b.bonusDate, u.name
                FROM bonuses b
                INNER JOIN complex_members cm ON cm.memberId = b.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                ORDER BY b.bonusDate DESC LIMIT 30
                """,
                (self.complex_id,)
            )

            for b in bonuses or []:
                self.all_events.append({
                    "type": f"{tr('tab_bonuses')} — {b.get('name') or '—'}",
                    "category": "other",
                    "description": f"{b.get('title') or '—'} • {format_money(b['amount'])} {tr('toman')}",
                    "date": b["bonusDate"]
                })

            # ─── Deductions ───
            deductions = self.db.fetch_all(
                """
                SELECT d.deductionId, d.amount, d.title, d.deductionDate, u.name
                FROM deductions d
                INNER JOIN complex_members cm ON cm.memberId = d.memberId
                INNER JOIN users u ON u.userId = cm.userId
                WHERE cm.complexId = %s
                ORDER BY d.deductionDate DESC LIMIT 30
                """,
                (self.complex_id,)
            )

            for d in deductions or []:
                self.all_events.append({
                    "type": f"{tr('tab_deductions')} — {d.get('name') or '—'}",
                    "category": "other",
                    "description": f"{d.get('title') or '—'} • {format_money(d['amount'])} {tr('toman')}",
                    "date": d["deductionDate"]
                })

            # ─── Sort ───
            def sort_key(e):
                d = e.get("date")
                if isinstance(d, datetime):
                    return d
                if isinstance(d, date):
                    return datetime(d.year, d.month, d.day)
                return datetime(1900, 1, 1)

            self.all_events.sort(key=sort_key, reverse=True)

        except Exception as e:
            print("LOAD EVENTS ERROR:", e)

        self.refresh_records()

    # =====================================================
    # REFRESH RECORDS
    # =====================================================

    def refresh_records(self):

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self.current_filter == "all":
            filtered = self.all_events
        else:
            filtered = [e for e in self.all_events if e["category"] == self.current_filter]

        if not filtered:
            empty_label = QLabel(tr("no_records"))
            empty_label.setObjectName("emptyLabel")
            empty_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            self.scroll_layout.addStretch()
            return

        for record in filtered:
            self.add_record(record)

        self.scroll_layout.addStretch()

    # =====================================================
    # ADD RECORD
    # =====================================================

    def add_record(self, record):

        card = QFrame()
        card.setObjectName("recordCard")
        card.setAttribute(Qt.WA_StyledBackground, True)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(15)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        title_label = QLabel(record["type"])
        title_label.setObjectName("recordTitle")

        info_label = QLabel(record["description"])
        info_label.setObjectName("recordInfo")
        info_label.setWordWrap(True)

        date_str = jalali_string_from_date(record["date"])
        date_label = QLabel(date_str)
        date_label.setObjectName("recordDate")

        text_layout.addWidget(title_label)
        text_layout.addWidget(info_label)
        text_layout.addWidget(date_label)

        card_layout.addLayout(text_layout)
        card_layout.addStretch()

        cat_map = {
            "payment": tr("filter_payments"),
            "attendance": tr("filter_attendance"),
            "leave": tr("filter_leaves"),
            "loan": tr("filter_loans"),
            "other": tr("filter_others"),
        }
        cat_text = cat_map.get(record["category"], "-")

        badge = QLabel(cat_text)
        badge.setObjectName("categoryBadge")
        badge.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(badge)

        self.scroll_layout.addWidget(card)

    # =====================================================
    # BACK
    # =====================================================

    def go_back(self):
        self.close()
        if self.parent_window:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()