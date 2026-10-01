# signals.py
from PySide6.QtCore import QObject, Signal

class AppSignals(QObject):

    # وقتی کارمند اضافه شد → complex_id
    employee_added = Signal(int)

    # وقتی کارمند حذف شد → complex_id
    employee_removed = Signal(int)

    # وقتی کارمند ویرایش شد → complex_id
    employee_updated = Signal(int)

    # وقتی مجموعه اضافه/حذف شد → user_id
    complex_changed = Signal(int)

# نمونه‌ی سراسری
signals = AppSignals()