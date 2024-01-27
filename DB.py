import sqlite3
from hashlib import md5


class Db:

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def create(self):
        with sqlite3.connect('Passwords.db') as db:
            cursor = db.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS password(
            ig INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tg INTEGER UNIQUE,
            password TEXT UNIQUE
            )""")
            db.commit()
            cursor.execute(f"INSERT OR IGNORE INTO password (id_tg) VALUES ({self.chat_id})")
            db.commit()

    def insert_password(self, password):
        password = md5(password.encode())
        with sqlite3.connect('Passwords.db') as db:
            cursor = db.cursor()
            cursor.execute(
                f"UPDATE password SET password = '{password.hexdigest()}' WHERE id_tg = {self.chat_id}")
            db.commit()
