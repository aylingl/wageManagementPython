import os
import uuid
import shutil
import hashlib
import json

PRIMARY_APP_DIR = r"C:\Program Files\wageManagementImg"

_CACHED_APP_DIR = None

def _test_write(directory):
    try:
        os.makedirs(directory, exist_ok=True)
        test_file = os.path.join(directory, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return True
    except Exception:
        return False

def get_app_directory():
    global _CACHED_APP_DIR
    if _CACHED_APP_DIR is not None:
        return _CACHED_APP_DIR

    if _test_write(PRIMARY_APP_DIR):
        _CACHED_APP_DIR = PRIMARY_APP_DIR
        return _CACHED_APP_DIR

    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    fallback = os.path.join(appdata, "wageManagementImg")

    if _test_write(fallback):
        _CACHED_APP_DIR = fallback
        return _CACHED_APP_DIR

    project_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "wageManagementImg"
    )
    _test_write(project_dir)
    _CACHED_APP_DIR = project_dir
    return _CACHED_APP_DIR

def get_images_directory():
    return os.path.join(get_app_directory(), "images")

def get_hashes_file():
    return os.path.join(get_app_directory(), "hashes.json")

def ensure_directories():
    try:
        os.makedirs(get_images_directory(), exist_ok=True)
        return True
    except Exception as e:
        print("ENSURE DIRECTORIES ERROR:", e)
        return False

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"}

def calculate_hash(file_path):
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print("CALCULATE HASH ERROR:", e)
        return None

# ═══════════════════════════════════════════════════════════
# کش هش → نام فایل
# ═══════════════════════════════════════════════════════════

def _load_hashes():
    path = get_hashes_file()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("LOAD HASHES ERROR:", e)
        return {}

def _save_hashes(data):
    path = get_hashes_file()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("SAVE HASHES ERROR:", e)
        return False

def find_by_hash(file_hash):
    """اگه هش توی کش پیدا شد، مسیر کامل رو برگردون"""
    if not file_hash:
        return None
    hashes = _load_hashes()
    filename = hashes.get(file_hash)
    if not filename:
        return None
    full_path = os.path.join(get_images_directory(), filename)
    if os.path.exists(full_path):
        return full_path
    # فایل پاک شده، از کش حذف کن
    del hashes[file_hash]
    _save_hashes(hashes)
    return None

def save_image(source_path, file_hash=None):
    """
    عکس رو کپی می‌کنه با چک تکراری نبودن.
    1. اگه هش توی کش بود → همون مسیر قبلی برمی‌گرده، کپی نمی‌کنه
    2. اگه نبود → کپی می‌کنه و توی کش ذخیره می‌کنه
    """
    if not source_path or not os.path.exists(source_path):
        return None

    if not ensure_directories():
        return None

    if not file_hash:
        file_hash = calculate_hash(source_path)
        if not file_hash:
            return None

    # ═══ اول توی کش بگرد ═══
    existing = find_by_hash(file_hash)
    if existing:
        return existing

    # ═══ عکس جدید → کپی کن ═══
    ext = os.path.splitext(source_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".png"

    part1 = uuid.uuid4().hex[:8]
    part2 = uuid.uuid4().hex[:16]
    part3 = uuid.uuid4().hex[:8]
    part4 = uuid.uuid4().hex[:2]
    unique_name = f"{part1}-{part2}-{part3}-{part4}{ext}"

    dest_path = os.path.join(get_images_directory(), unique_name)

    try:
        shutil.copy2(source_path, dest_path)
    except Exception as e:
        print("SAVE IMAGE ERROR:", e)
        return None

    # ═══ ثبت توی کش ═══
    hashes = _load_hashes()
    hashes[file_hash] = unique_name
    _save_hashes(hashes)

    return dest_path

def delete_image(image_path):
    if not image_path:
        return
    try:
        images_dir = get_images_directory()
        if image_path.startswith(images_dir) and os.path.exists(image_path):
            filename = os.path.basename(image_path)
            os.remove(image_path)
            hashes = _load_hashes()
            keys_to_del = [k for k, v in hashes.items() if v == filename]
            for k in keys_to_del:
                del hashes[k]
            if keys_to_del:
                _save_hashes(hashes)
    except Exception as e:
        print("DELETE IMAGE ERROR:", e)