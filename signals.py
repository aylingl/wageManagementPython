# signals.py
from PySide6.QtCore import QObject, Signal

class AppSignals(QObject):

    # ─── کارمندان ───
    employee_added = Signal(int)      # complex_id
    employee_removed = Signal(int)    # complex_id
    employee_updated = Signal(int)    # complex_id

    # ─── مجموعه‌ها ───
    complex_changed = Signal(int)     # user_id

    # ─── تم / زبان ───
    theme_changed = Signal(str)       # "light" / "dark"
    language_changed = Signal(str)    # "fa" / "en" / "ar"

    # ─── دیتای عمومی (حضور، مالی، کارتابل و...) ───
    data_changed = Signal(str)        # kind: "attendance" / "finance" / "jobs" / "all"

signals = AppSignals()