from database import Database

db = Database()

if db.connect():
    print("Database test successful!")
    db.close()
else:
    print("Database test failed!")