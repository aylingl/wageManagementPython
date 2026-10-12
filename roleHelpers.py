# roleHelpers.py
# نمایش badge نقش بر اساس زبان جاری

from i18n import tr

def get_role_badge(role_val):
    """
    (text, fg_color, bg_color) برمی‌گردونه
    خودکار با زبان جاری هماهنگ میشه
    """
    role_colors = {
        "owner":      ("#B87900", "#FFF4DD"),
        "both":       ("#B87900", "#FFF4DD"),
        "manager":    ("#1961C7", "#DBEAFE"),
        "supervisor": ("#16A34A", "#DCFCE7"),
        "employee":   ("#526273", "#EEF2F6"),
    }
    role_icons = {
        "owner":      "👑",
        "both":       "👑",
        "manager":    "📋",
        "supervisor": "🎯",
        "employee":   "👤",
    }

    if role_val not in role_colors:
        role_val = "employee"

    icon = role_icons[role_val]
    fg, bg = role_colors[role_val]
    label = tr(f"role_{role_val}")

    return f"{icon} {label}", fg, bg