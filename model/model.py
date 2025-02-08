import os
import shutil
import sqlite3
import uuid

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
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
                ("Fried Rice", 2.5, "fried_rice.png"),
                ("Coca Cola", 1.2, "coca_cola.png"),
                ("Burger", 3.0, "burger.png"),
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

    def add_menu_item(self, name, unit_price, image_path):
        # Ensure the images folder exists
        if not os.path.exists("images"):
            os.makedirs("images")

        # Generate a unique image filename using UUID
        unique_image_name = f"{uuid.uuid4().hex}.png"  # UUID will create a unique name for the image

        # Define the target path in the images folder
        target_path = os.path.join("images", unique_image_name)

        # Copy the image to the images folder with the new unique name
        shutil.copy(image_path, target_path)

        # Insert the new menu item into the database with the new image filename
        self.cursor.execute("INSERT INTO menu (name, unit_price, image) VALUES (?, ?, ?)",
                            (name, unit_price, unique_image_name))
        self.conn.commit()

    def get_menu_item(self, menu_id):
        # Fetch the menu item by menu_id from the database
        self.cursor.execute("SELECT name, unit_price, image FROM menu WHERE id = ?", (menu_id,))
        result = self.cursor.fetchone()
        if result:
            return {'name': result[0], 'unit_price': result[1], 'image': result[2]}
        return None

    def update_menu_item(self, menu_id, name, unit_price, image_path):
        # Ensure the images folder exists
        if not os.path.exists("images"):
            os.makedirs("images")

        # Generate a unique image filename using UUID
        unique_image_name = f"{uuid.uuid4().hex}.png"  # Generate unique name with .png extension
        target_path = os.path.join("images", unique_image_name)

        # If the image doesn't already exist in the images folder, copy it there
        if not os.path.exists(target_path):
            shutil.copy(image_path, target_path)

        # Update the menu item in the database using the column 'id'
        self.cursor.execute("UPDATE menu SET name = ?, unit_price = ?, image = ? WHERE id = ?",
                            (name, unit_price, unique_image_name, menu_id))
        self.conn.commit()