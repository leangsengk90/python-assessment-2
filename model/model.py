import os
import shutil
import sqlite3
import uuid
import bcrypt  # Import bcrypt for password hashing

db_path = "/Users/kaoleangseng/PycharmProjects/RMS/controller/rms.db"

# Model: Handles database interactions
class Model:
    def __init__(self):
        self.db_path = db_path

        # Remove the database file if it exists
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print("rms.db has been removed.")

        # Open the connection and set the cursor once
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")  # Enables write-ahead logging
        os.chmod(self.db_path, 0o777)  # Ensure the db file is writable

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
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS tables (
                    table_number INTEGER PRIMARY KEY,
                    description TEXT
                )
            """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                reserve_number INTEGER PRIMARY KEY AUTOINCREMENT,
                tables TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
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
                # More sample data...
            ]
            self.cursor.executemany("INSERT INTO menu (name, unit_price, image) VALUES (?, ?, ?)", sample_data)

            # Insert sample table numbers
            self.cursor.execute("SELECT COUNT(*) FROM tables")
            if self.cursor.fetchone()[0] == 0:
                table_data = [
                    (1, "Window-side table"),
                    (2, "Near the kitchen"),
                    (3, "Outdoor seating"),
                    (4, "Private dining area"),
                    (5, "Bar counter seat"),
                ]
                self.cursor.executemany("INSERT INTO tables (table_number, description) VALUES (?, ?)", table_data)

            # Check if reservation data exists
            self.cursor.execute("SELECT COUNT(*) FROM reservations")
            if self.cursor.fetchone()[0] == 0:
                sample_reservations = [
                    ("1, 2, 3", "Dara", "123456789", "2025-02-15", "18:30"),
                    ("5", "Nita", "987654321", "2025-02-16", "19:00"),
                    ("4", "Bora", "555123456", "2025-02-17", "20:15"),
                ]
                self.cursor.executemany(
                    "INSERT INTO reservations (tables, name, phone, date, time) VALUES (?, ?, ?, ?, ?)",
                    sample_reservations)

            self.conn.commit()

    def get_menu_items(self):
        self.cursor.execute("SELECT * FROM menu")
        return self.cursor.fetchall()

    def delete_menu_item(self, menu_id):
        try:
            self.cursor.execute("DELETE FROM menu WHERE id=?", (menu_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting menu item: {e}")
            self.conn.rollback()  # Rollback in case of error

    def add_menu_item(self, name, unit_price, image_path):
        # Ensure the images folder exists
        if not os.path.exists("images"):
            os.makedirs("images")

        # Generate a unique image filename using UUID
        unique_image_name = f"{uuid.uuid4().hex}.png"

        # Define the target path in the images folder
        target_path = os.path.join("images", unique_image_name)

        # Copy the image to the images folder with the new unique name
        shutil.copy(image_path, target_path)

        # Insert the new menu item into the database with the new image filename
        self.cursor.execute("INSERT INTO menu (name, unit_price, image) VALUES (?, ?, ?)",
                            (name, unit_price, unique_image_name))
        self.conn.commit()

    def get_menu_item(self, menu_id):
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
        unique_image_name = f"{uuid.uuid4().hex}.png"
        target_path = os.path.join("images", unique_image_name)

        # If the image doesn't already exist in the images folder, copy it there
        if not os.path.exists(target_path):
            shutil.copy(image_path, target_path)

        # Update the menu item in the database using the column 'id'
        self.cursor.execute("UPDATE menu SET name = ?, unit_price = ?, image = ? WHERE id = ?",
                            (name, unit_price, unique_image_name, menu_id))
        self.conn.commit()

    def get_tables(self):
        self.cursor.execute("SELECT table_number, description FROM tables")
        return self.cursor.fetchall()

    def delete_table(self, table_number):
        try:
            self.cursor.execute("DELETE FROM tables WHERE table_number = ?", (table_number,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting table: {e}")
            self.conn.rollback()

    def update_table(self, table_number, new_description):
        self.cursor.execute("UPDATE tables SET description = ? WHERE table_number = ?",
                            (new_description, table_number))
        self.conn.commit()

    def add_table(self, table_number, description):
        try:
            self.cursor.execute("INSERT INTO tables (table_number, description) VALUES (?, ?)",
                                (table_number, description))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting table: {e}")

    # -------- Reservation Methods -------- #

    def get_reservations(self):
        self.cursor.execute("SELECT reserve_number, tables, name, phone, date, time FROM reservations")
        return self.cursor.fetchall()

    def add_reservation(self, tables, name, phone, date, time):
        try:
            self.cursor.execute("INSERT INTO reservations (tables, name, phone, date, time) VALUES (?, ?, ?, ?, ?)",
                                (tables, name, phone, date, time))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error inserting reservation: {e}")
            return False

    def update_reservation(self, reserve_number, tables, name, phone, date, time):
        try:
            self.cursor.execute("""
                   UPDATE reservations 
                   SET tables = ?, name = ?, phone = ?, date = ?, time = ? 
                   WHERE reserve_number = ?
               """, (tables, name, phone, date, time, reserve_number))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating reservation: {e}")
            return False

    def delete_reservation(self, reserve_number):
        try:
            self.cursor.execute("DELETE FROM reservations WHERE reserve_number = ?", (reserve_number,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting reservation: {e}")
            return False

    def close_connection(self):
        """Close the connection properly."""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"Error closing the connection: {e}")
