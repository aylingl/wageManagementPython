import sys

from PySide6.QtWidgets import QApplication

from database import load_db_config
from migrationRunner import run_all_migrations

def main():
    app = QApplication(sys.argv)

    # اعمال تم
    try:
        from theme import theme_manager
        theme_manager.apply("light")
    except Exception as e:
        print("Theme error:", e)

    config = load_db_config()

    if config is None:
        # بار اول: پنجره راه‌اندازی دیتابیس
        from setupDatabaseWindow import SetupDatabaseWindow

        def after_setup():
            from main import LoginWindow
            window = LoginWindow()
            window.show()
            # نگه‌داشتن رفرنس که garbage collect نشه
            app._main_window = window

        setup_window = SetupDatabaseWindow(on_success=after_setup)
        setup_window.show()
        app._setup_window = setup_window
    else:
        # بارهای بعدی: اجرای migration و باز کردن Login
        try:
            run_all_migrations()
        except Exception as e:
            print("MIGRATION ERROR:", e)

        from main import LoginWindow
        window = LoginWindow()
        window.show()
        app._main_window = window

    sys.exit(app.exec())

if __name__ == "__main__":
    main()