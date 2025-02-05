import os
import sqlite3
import bcrypt  # Import bcrypt for password hashing

# Model: Handles database interactions
class Model:
    def __init__(self):
        self.db_path = "rms.db"

        # Remove the database file if it exists
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print("rms.db has been removed.")

        self.conn = sqlite3.connect("rms.db", isolation_level="EXCLUSIVE")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.initialize_data()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                unit_price REAL NOT NULL,
                image TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def check_user(self, username, password):
        self.cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user = self.cursor.fetchone()

        if user:
            hashed_password = user[0]
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        return False

    def add_user(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def initialize_data(self):
        # Check if data already exists
        self.cursor.execute("SELECT COUNT(*) FROM menu")
        if self.cursor.fetchone()[0] == 0:
            sample_data = [
                ("Fried Rice", 2.5, "../images/fried_rice.png"),
                ("Coca Cola", 1.2, "../images/coca_cola.png"),
                ("Burger", 3.0, "../images/burger.png"),
            ]
            self.cursor.executemany("INSERT INTO menu (name, unit_price, image) VALUES (?, ?, ?)", sample_data)
            self.conn.commit()

    def get_menu_items(self):
        self.cursor.execute("SELECT * FROM menu")
        return self.cursor.fetchall()

    def delete_menu_item(self, menu_id):
        try:
            self.cursor.execute("DELETE FROM menu WHERE id=?", (menu_id,))
            self.conn.commit()  # Make sure to commit after executing the delete
        except sqlite3.Error as e:
            print(f"Error deleting menu item: {e}")
            self.conn.rollback()  # Rollback in case of error

    def update_menu_item(self, menu_id, name, price, image):
        self.cursor.execute("UPDATE menu SET name=?, unit_price=?, image=? WHERE id=?", (name, price, image, menu_id))
        self.conn.commit()