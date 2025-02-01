import sqlite3

# Model: Handles database interactions
class Model:
    def __init__(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """
        )
        self.conn.commit()

    def check_user(self, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return self.cursor.fetchone() is not None

    def add_user(self, username, password):
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False