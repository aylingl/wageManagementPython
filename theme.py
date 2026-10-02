from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
import json
import os

class ThemeManager(QObject):

    theme_changed = Signal(str)  # "light" یا "dark"

    def __init__(self):
        super().__init__()
        self.current_theme = "light"

    # =====================================================
    # GET
    # =====================================================

    def get(self):
        return self.current_theme

    def is_dark(self):
        return self.current_theme == "dark"

    # =====================================================
    # COLORS — رنگ‌های تم فعلی
    # =====================================================

    def colors(self):

        if self.is_dark():
            return {
                "bg_main":      "#121418",
                "bg_card":      "#1E2128",
                "bg_input":     "#2A2E36",
                "bg_hover":     "#252932",
                "text_main":    "#E8EAED",
                "text_dim":     "#9AA0A6",
                "border":       "#3C4043",
                "border_hover": "#5F6368",
                "accent":       "#4589E8",
                "accent_hover": "#5B9AF0",
                "accent_light": "#1A2A44",
                "success":      "#16A34A",
                "success_bg":   "#14321F",
                "danger":       "#EF4444",
                "danger_bg":    "#3A1A1A",
                "warning":      "#F59E0B",
                "warning_bg":   "#3A2A10",
                "white":        "#FFFFFF",
            }
        else:
            return {
                "bg_main":      "#F5F8FC",
                "bg_card":      "#FFFFFF",
                "bg_input":     "#F7F9FC",
                "bg_hover":     "#EAF3FF",
                "text_main":    "#1E2F43",
                "text_dim":     "#8290A1",
                "border":       "#E2EAF4",
                "border_hover": "#C9DDF5",
                "accent":       "#1961C7",
                "accent_hover": "#4589E8",
                "accent_light": "#EAF3FF",
                "success":      "#16A34A",
                "success_bg":   "#EAF6EE",
                "danger":       "#D93025",
                "danger_bg":    "#FDEBEC",
                "warning":      "#B87900",
                "warning_bg":   "#FFF4DD",
                "white":        "#FFFFFF",
            }

    # =====================================================
    # APPLY
    # =====================================================

    def apply(self, theme_name, save_to_db=False, user_id=None):

        if theme_name not in ("light", "dark"):
            theme_name = "light"

        changed = (theme_name != self.current_theme)
        self.current_theme = theme_name

        app = QApplication.instance()
        if app is None:
            return

        if theme_name == "dark":
            self._apply_dark_palette(app)
        else:
            self._apply_light_palette(app)

        # ذخیره در دیتابیس
        if save_to_db and user_id:
            try:
                from database import Database
                db = Database()

                existing = db.fetch_one(
                    "SELECT settingId FROM user_settings WHERE userId = %s LIMIT 1",
                    (user_id,)
                )

                if existing:
                    db.execute(
                        """
                        UPDATE user_settings
                        SET themeName = %s
                        WHERE userId = %s
                        """,
                        (theme_name, user_id)
                    )
                else:
                    db.execute(
                        """
                        INSERT INTO user_settings (userId, themeName)
                        VALUES (%s, %s)
                        """,
                        (user_id, theme_name)
                    )
            except Exception as e:
                print("SAVE THEME ERROR:", e)

        # ذخیره در فایل
        

        if changed:
            self.theme_changed.emit(theme_name)

    # =====================================================
    # LOAD FOR USER
    # =====================================================

    def load_for_user(self, user_id):

        try:
            from database import Database
            db = Database()

            row = db.fetch_one(
                """
                SELECT themeName
                FROM user_settings
                WHERE userId = %s
                LIMIT 1
                """,
                (user_id,)
            )

            if row and row.get("themeName"):
                self.current_theme = row["themeName"]

        except Exception as e:
            print("LOAD THEME ERROR:", e)

        self.apply(self.current_theme)

    # =====================================================
    # SAVE / LOAD FROM FILE
    # =====================================================

    def save_to_file(self):

        try:
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "theme_config.json"
            )

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({"theme": self.current_theme}, f)

        except Exception as e:
            print("SAVE THEME FILE ERROR:", e)

    def load_from_file(self):

        try:
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "theme_config.json"
            )

            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("theme") in ("light", "dark"):
                        self.current_theme = data["theme"]

        except Exception as e:
            print("LOAD THEME FILE ERROR:", e)

    # =====================================================
    # PALETTES
    # =====================================================

    def _apply_dark_palette(self, app):

        palette = QPalette()

        bg_main = QColor("#121418")
        bg_card = QColor("#1E2128")
        bg_input = QColor("#2A2E36")
        text_main = QColor("#E8EAED")
        text_dim = QColor("#9AA0A6")
        accent = QColor("#4589E8")

        palette.setColor(QPalette.Window, bg_main)
        palette.setColor(QPalette.WindowText, text_main)
        palette.setColor(QPalette.Base, bg_card)
        palette.setColor(QPalette.AlternateBase, bg_input)
        palette.setColor(QPalette.ToolTipBase, bg_card)
        palette.setColor(QPalette.ToolTipText, text_main)
        palette.setColor(QPalette.Text, text_main)
        palette.setColor(QPalette.Button, bg_card)
        palette.setColor(QPalette.ButtonText, text_main)
        palette.setColor(QPalette.BrightText, QColor("#FF5555"))
        palette.setColor(QPalette.Link, accent)
        palette.setColor(QPalette.Highlight, accent)
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.PlaceholderText, text_dim)

        palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#5F6368"))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#5F6368"))

        app.setPalette(palette)

    def _apply_light_palette(self, app):

        palette = QPalette()

        bg_main = QColor("#F5F8FC")
        bg_card = QColor("#FFFFFF")
        bg_input = QColor("#F7F9FC")
        text_main = QColor("#1D2939")
        text_dim = QColor("#667085")
        accent = QColor("#4589E8")

        palette.setColor(QPalette.Window, bg_main)
        palette.setColor(QPalette.WindowText, text_main)
        palette.setColor(QPalette.Base, bg_card)
        palette.setColor(QPalette.AlternateBase, bg_input)
        palette.setColor(QPalette.ToolTipBase, bg_card)
        palette.setColor(QPalette.ToolTipText, text_main)
        palette.setColor(QPalette.Text, text_main)
        palette.setColor(QPalette.Button, bg_card)
        palette.setColor(QPalette.ButtonText, text_main)
        palette.setColor(QPalette.BrightText, QColor("#D93025"))
        palette.setColor(QPalette.Link, accent)
        palette.setColor(QPalette.Highlight, accent)
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.PlaceholderText, text_dim)

        app.setPalette(palette)

# نمونه سراسری
theme_manager = ThemeManager()

# ─── اتصال theme_manager به signals ───
from signals import signals

def _emit_theme_change(theme_name):
    signals.theme_changed.emit(theme_name)

theme_manager.theme_changed.connect(_emit_theme_change)