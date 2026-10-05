import os
import sys
import glob
from datetime import datetime

from database import Database, get_app_directory

def get_migrations_directory():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "migrations")

def ensure_migrations_table(db):
    sql = """
        CREATE TABLE IF NOT EXISTS `schema_migrations` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `filename` varchar(100) NOT NULL,
            `appliedAt` datetime NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `uq_schema_migrations_filename` (`filename`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_persian_ci
    """
    result = db.execute(sql)
    print("MIGRATION: ensure schema_migrations ->", "OK" if result is not None else "FAILED")
    return result is not None

def get_applied_migrations(db):
    try:
        rows = db.fetch_all("SELECT filename FROM schema_migrations")
        return {r["filename"] for r in rows}
    except Exception as e:
        print("MIGRATION: get_applied_migrations error:", e)
        return set()

def get_all_migration_files():
    migrations_dir = get_migrations_directory()

    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir, exist_ok=True)
        print("MIGRATION: created migrations dir:", migrations_dir)
        return []

    files = glob.glob(os.path.join(migrations_dir, "*.sql"))
    print("MIGRATION: found files:", [os.path.basename(f) for f in files])

    def sort_key(path):
        name = os.path.basename(path).lower()
        if name.startswith("initializatio"):
            return (0, name)
        return (1, name)

    files.sort(key=sort_key)
    return files

def run_all_migrations():
    print("=" * 50)
    print("MIGRATION: start")

    db = Database()
    if not db.is_connected():
        print("MIGRATION: cannot connect to db")
        return False

    # ۱) اطمینان از وجود جدول schema_migrations
    if not ensure_migrations_table(db):
        print("MIGRATION: could not create schema_migrations table")
        return False

    # ۲) خواندن migration‌های قبلی
    applied = get_applied_migrations(db)
    print("MIGRATION: already applied:", list(applied))

    # ۳) لیست فایل‌ها
    all_files = get_all_migration_files()

    applied_count = 0

    for file_path in all_files:
        filename = os.path.basename(file_path)

        if filename in applied:
            print(f"MIGRATION: skip (already applied) {filename}")
            continue

        print(f"MIGRATION: applying {filename} ...")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                sql_text = f.read()

            ok = db.execute_script(sql_text)

            if not ok:
                print(f"MIGRATION FAILED: {filename}")
                return False

            db.execute(
                "INSERT INTO schema_migrations (filename, appliedAt) VALUES (%s, %s)",
                (filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            applied_count += 1
            print(f"MIGRATION: {filename} applied ✓")

        except Exception as e:
            print(f"MIGRATION ERROR {filename}:", e)
            return False

    print(f"MIGRATION: done. {applied_count} new migrations applied.")
    print("=" * 50)
    return True

if __name__ == "__main__":
    run_all_migrations()