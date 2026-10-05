from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt

from database import (
    save_db_config,
    create_database_if_not_exists,
    get_config_path
)

class SetupDatabaseWindow(QWidget):

    def __init__(self, on_success=None):
        super().__init__()

        self.on_success = on_success

        self.setWindowTitle("راه‌اندازی دیتابیس")
        self.setFixedSize(480, 560)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setObjectName("setupDbWindow")

        self.build_ui()
        self.apply_style()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(12)

        title = QLabel("راه‌اندازی دیتابیس")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("اطلاعات اتصال MySQL خود را وارد کنید")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(8)

        def add_field(label_text, placeholder, default="", password=False):
            lbl = QLabel(label_text)
            lbl.setObjectName("fieldLabel")
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(44)
            inp.setText(default)
            if password:
                inp.setEchoMode(QLineEdit.Password)
            card_layout.addWidget(lbl)
            card_layout.addWidget(inp)
            return inp

        self.host_input = add_field("هاست", "localhost", "localhost")
        self.port_input = add_field("پورت", "3306", "3306")
        self.user_input = add_field("نام کاربری", "root", "root")
        self.pass_input = add_field("رمز عبور", "", "", password=True)
        self.db_input = add_field("نام دیتابیس", "wage_management", "wage_management")

        layout.addWidget(card)
        layout.addSpacing(10)

        self.connect_btn = QPushButton("اتصال و راه‌اندازی")
        self.connect_btn.setObjectName("connectBtn")
        self.connect_btn.setFixedHeight(48)
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.clicked.connect(self.try_connect)
        layout.addWidget(self.connect_btn)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(40)
        layout.addWidget(self.status_label)

        layout.addStretch()

        path_lbl = QLabel(f"محل ذخیره تنظیمات:\n{get_config_path()}")
        path_lbl.setObjectName("pathLabel")
        path_lbl.setWordWrap(True)
        layout.addWidget(path_lbl)

    def apply_style(self):
        self.setStyleSheet("""
            QWidget#setupDbWindow {
                background-color: #F5F8FC;
                font-family: "Vazirmatn";
            }
            QLabel#title {
                color: #173B67;
                font-size: 22px;
                font-weight: 800;
            }
            QLabel#subtitle {
                color: #7A8999;
                font-size: 12px;
            }
            QFrame#card {
                background-color: #FFFFFF;
                border: 1px solid #E2EAF4;
                border-radius: 18px;
            }
            QLabel#fieldLabel {
                color: #536779;
                font-size: 12px;
                font-weight: 600;
            }
            QLineEdit {
                background-color: #F5F8FC;
                color: #243B53;
                border: 1px solid #DCE6F2;
                border-radius: 12px;
                padding: 0 16px;
                font-size: 13px;
            }
            QLineEdit:focus {
                background-color: #FFFFFF;
                border: 2px solid #4B82C3;
            }
            QPushButton#connectBtn {
                background-color: #4589E8;
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton#connectBtn:hover {
                background-color: #3478D8;
            }
            QLabel#statusLabel {
                color: #D93025;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#pathLabel {
                color: #98A2B3;
                font-size: 10px;
            }
        """)

    def try_connect(self):
        host = self.host_input.text().strip() or "localhost"
        port_text = self.port_input.text().strip() or "3306"
        user = self.user_input.text().strip() or "root"
        password = self.pass_input.text()
        dbname = self.db_input.text().strip() or "wage_management"

        try:
            port = int(port_text)
        except ValueError:
            self.status_label.setText("پورت باید عدد باشد.")
            return

        self.status_label.setText("در حال اتصال...")
        self.status_label.repaint()

        ok = create_database_if_not_exists(host, port, user, password, dbname)
        if not ok:
            self.status_label.setText(
                "اتصال به MySQL برقرار نشد. اطلاعات را بررسی کنید."
            )
            return

        save_db_config(host, port, user, password, dbname)

        self.status_label.setText("در حال اجرای migration ها...")
        self.status_label.repaint()

        try:
            from migrationRunner import run_all_migrations
            run_all_migrations()
        except Exception as e:
            print("MIGRATION ERROR:", e)

        self.status_label.setText("اتصال موفق! در حال باز کردن برنامه...")

        if callable(self.on_success):
            self.on_success()
        self.close()