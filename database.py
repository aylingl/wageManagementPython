import os
import sys
import configparser
import pymysql
from pymysql.cursors import DictCursor

def get_app_directory():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_config_path():
    return os.path.join(get_app_directory(), "config.ini")

def load_db_config():
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return None

    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")

    if "database" not in config:
        return None

    return {
        "host": config["database"].get("host", "localhost"),
        "port": config["database"].getint("port", 3306),
        "user": config["database"].get("user", "root"),
        "password": config["database"].get("password", ""),
        "database": config["database"].get("database", "wage_management"),
    }

def save_db_config(host, port, user, password, database):
    config = configparser.ConfigParser()
    config["database"] = {
        "host": host,
        "port": str(port),
        "user": user,
        "password": password,
        "database": database,
    }
    with open(get_config_path(), "w", encoding="utf-8") as f:
        config.write(f)

def create_database_if_not_exists(host, port, user, password, database):
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset="utf8mb4",
        )
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("CREATE DATABASE ERROR:", e)
        return False

class Database:

    def __init__(self):
        self.connection = None
        self.config = load_db_config()

        if self.config:
            self.connect()

    def connect(self):
        if not self.config:
            print("DB CONFIG NOT FOUND")
            return False

        try:
            self.connection = pymysql.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"],
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=False,
            )
            print("MySQL connected successfully.")
            return True
        except Exception as e:
            print("MySQL connection error:", e)
            self.connection = None
            return False

    def is_connected(self):
        try:
            if self.connection is None:
                return False
            self.connection.ping(reconnect=True)
            return True
        except Exception:
            return False

    def fetch_one(self, query, params=None):
        if not self.is_connected():
            return None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            print("FETCH ONE ERROR:", e)
            return None

    def fetch_all(self, query, params=None):
        if not self.is_connected():
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            print("FETCH ALL ERROR:", e)
            return []

    def execute(self, query, params=None):
        if not self.is_connected():
            return None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Exception as e:
            print("EXECUTE ERROR:", e)
            try:
                self.connection.rollback()
            except Exception:
                pass
            return None

    def execute_many(self, query, params_list):
        if not self.is_connected():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print("EXECUTE MANY ERROR:", e)
            try:
                self.connection.rollback()
            except Exception:
                pass
            return False

    def execute_script(self, sql_text):
        if not self.is_connected():
            return False
        try:
            cursor = self.connection.cursor()

            statements = []
            current = []
            for line in sql_text.splitlines():
                stripped = line.strip()
                if stripped.startswith("--") or stripped.startswith("#"):
                    continue
                current.append(line)
                if ";" in line:
                    stmt = "\n".join(current).strip().rstrip(";").strip()
                    if stmt:
                        statements.append(stmt)
                    current = []
            if current:
                stmt = "\n".join(current).strip().rstrip(";").strip()
                if stmt:
                    statements.append(stmt)

            for stmt in statements:
                cursor.execute(stmt)

            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print("EXECUTE SCRIPT ERROR:", e)
            try:
                self.connection.rollback()
            except Exception:
                pass
            return False