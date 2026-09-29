import mysql.connector
from mysql.connector import Error

class Database:

    def __init__(self):

        self.connection = None

    # =====================================================
    # CONNECT
    # =====================================================

    def connect(self):

        try:

            self.connection = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="root",
                password="1",
                database="wagemanagement",
                autocommit=True
            )

            if self.connection.is_connected():

                print("MySQL connected successfully.")
                return True

            return False

        except Error as error:

            print("MySQL connection error:")
            print(error)

            self.connection = None
            return False

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        if self.connection is not None:

            if self.connection.is_connected():

                self.connection.close()
                print("MySQL connection closed.")

    # =====================================================
    # SELECT ALL
    # =====================================================

    def fetch_all(self, query, params=None):

        if self.connection is None:

            if not self.connect():
                return []

        cursor = None

        try:

            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())

            return cursor.fetchall()

        except Error as error:

            print("MySQL fetch error:")
            print(error)
            return []

        finally:

            if cursor:
                cursor.close()

    # =====================================================
    # SELECT ONE
    # =====================================================

    def fetch_one(self, query, params=None):

        if self.connection is None:

            if not self.connect():
                return None

        cursor = None

        try:

            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())

            return cursor.fetchone()

        except Error as error:

            print("MySQL fetch one error:")
            print(error)
            return None

        finally:

            if cursor:
                cursor.close()

    # =====================================================
    # INSERT / UPDATE / DELETE
    # =====================================================

    def execute(self, query, params=None):

        if self.connection is None:

            if not self.connect():
                return None

        cursor = None

        try:

            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()

            # برای INSERT، شناسه برگردان
            if cursor.lastrowid:
                return cursor.lastrowid

            # برای UPDATE/DELETE، تعداد ردیف تأثیرگرفته
            return cursor.rowcount

        except Error as error:

            self.connection.rollback()

            print("MySQL execute error:")
            print(error)
            return None

        finally:

            if cursor:
                cursor.close()