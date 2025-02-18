import os
import shutil
import sqlite3
import uuid
import bcrypt  # Import bcrypt for password hashing

db_path = "/Users/kaoleangseng/PycharmProjects/RMS/controller/rms.db"
image_base_path = "/Users/kaoleangseng/PycharmProjects/RMS/controller/images"

# Model: Handles database interactions
class Model:
    def __init__(self):
        self.db_path = db_path

        # Open the connection and set the cursor once
        # self.conn = sqlite3.connect(self.db_path)
        # self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0, isolation_level=None)
        self.conn.execute("PRAGMA journal_mode=WAL;")  # Enables write-ahead logging
        # os.chmod(self.db_path, 0o777)  # Ensure the db file is writable

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
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER NOT NULL,
                order_date DATETIME DEFAULT (datetime('now', 'localtime')),
                menu_id INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                tax REAL DEFAULT 0.0,  
                discount REAL DEFAULT 0.0,
                is_enabled BOOLEAN DEFAULT 1,  
                invoice_id INTEGER,
                FOREIGN KEY (menu_id) REFERENCES menu(id),
                FOREIGN KEY (table_number) REFERENCES tables(table_number),
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_date DATETIME DEFAULT (datetime('now', 'localtime')),
                is_enabled BOOLEAN DEFAULT 1
            );
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

            # Check if invoice status data exists
            # self.cursor.execute("SELECT COUNT(*) FROM invoices")
            # if self.cursor.fetchone()[0] == 0:
            #     sample_invoices = [
            #         ("2025-02-18 12:00:00", 1),  # Invoice is enabled
            #         ("2025-02-18 12:15:00", 1),  # Invoice is disabled
            #         ("2025-02-18 12:30:00", 1),  # Invoice is enabled
            #         ("2025-02-18 12:45:00", 1),  # Invoice is enabled
            #         ("2025-02-18 13:00:00", 1),  # Invoice is disabled
            #     ]
            #     self.cursor.executemany(
            #         "INSERT INTO invoices (created_date, is_enabled) VALUES (?, ?)",
            #         sample_invoices
            #     )

            self.conn.commit()

    # def get_menu_items(self):
    #     conn = sqlite3.connect(self.db_path, check_same_thread=False)
    #     conn.execute("PRAGMA journal_mode=WAL;")  # Enables write-ahead logging
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT * FROM menu")
    #     return self.cursor.fetchall()

    def get_menu_items(self):
        self.cursor.execute("SELECT id, name, unit_price, image FROM menu")  # Query to get menu items
        menu_items = self.cursor.fetchall()
        return menu_items

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

    # Tables
    def get_table_number(self):
        self.cursor.execute("SELECT table_number FROM tables")  # Only select the table_number
        tables = [row[0] for row in self.cursor.fetchall()]
        return tables

    def get_tables(self):
        self.cursor.execute("SELECT table_number, description FROM tables")  # Only select the table_number
        tables = self.cursor.fetchall()
        return tables

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

    # Order
    def insert_order(self, table_number, menu_id, qty, tax, discount):
        """Insert order data into the database, including tax and discount."""
        try:
            self.cursor.execute("""
                INSERT INTO orders (table_number, menu_id, qty, tax, discount)
                VALUES (?, ?, ?, ?, ?)
            """, (table_number, menu_id, qty, tax, discount))
            self.conn.commit()
            print(
                f"Order for table {table_number}, menu_id {menu_id}, qty {qty}, tax {tax}, discount {discount} inserted.")
        except Exception as e:
            print(f"Failed to insert order: {e}")


    # Invoice

    def disable_invoice(self, order_id):
        query = "UPDATE orders SET is_enabled = 0 WHERE id = ?"
        self.cursor.execute(query, (order_id,))
        self.conn.commit()

    # def get_invoices(self):
    #     query = """
    #         SELECT o.id, o.table_number, o.order_date, m.name, m.unit_price, o.qty, o.tax, o.discount
    #         FROM orders o
    #         JOIN menu m ON o.menu_id = m.id
    #         WHERE o.is_enabled = 1
    #     """
    #     self.cursor.execute(query)
    #     return self.cursor.fetchall()

    def get_menu_names(self):
        # Get all menu names from the database
        query = "SELECT name FROM menu"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def update_invoice(self, updated_data):
        query = """
            UPDATE orders
            SET table_number = ?, menu_id = (SELECT id FROM menu WHERE name = ?), qty = ?, tax = ?, discount = ?
            WHERE id = ?
        """
        self.cursor.execute(query, updated_data)
        self.conn.commit()

    def get_invoices(self, table_number=None):
        """Fetch invoices, optionally filtered by table number."""
        query = """
            SELECT o.id, o.table_number, o.order_date, m.name, m.unit_price, o.qty, o.tax, o.discount
            FROM orders o
            JOIN menu m ON o.menu_id = m.id
            WHERE o.is_enabled = 1
        """
        params = []

        if table_number:
            query += " AND o.table_number = ?"
            params.append(table_number)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_table_numbers(self):
        """Fetch unique table numbers from the orders table where is_enabled = 1."""
        query = "SELECT DISTINCT table_number FROM orders WHERE is_enabled = 1 ORDER BY table_number"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def get_valid_table_numbers(self):
        """Fetch available table numbers from the tables table."""
        try:
            query = "SELECT DISTINCT table_number FROM tables ORDER BY table_number"
            self.cursor.execute(query)
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Failed to fetch valid table numbers: {e}")
            return []

    def get_last_invoice_id(self):
        """Fetch the last inserted invoice ID from the database."""
        try:
            query = "SELECT MAX(id) FROM invoices"
            self.cursor.execute(query)  # Execute the query
            result = self.cursor.fetchone()  # Fetch one row from the result
            if result[0] is None:  # No invoices exist
                return 1
            else:
                return result[0] + 1  # Increment the last invoice ID
        except Exception as e:
            print(f"Failed to fetch the last invoice ID: {e}")
            return 1  # Default to 1 if something goes wrong

    def insert_new_invoice(self, invoice_datetime):
        """Insert a new invoice record into the invoices table with a provided datetime."""
        try:
            # Insert the new invoice record with the provided datetime
            self.cursor.execute(
                "INSERT INTO invoices (created_date, is_enabled) VALUES (?, ?)",
                (invoice_datetime, True)  # Pass the provided datetime and True for is_enabled
            )
            self.conn.commit()  # Commit the transaction
        except Exception as e:
            print(f"Failed to insert new invoice: {e}")
            return None

    def update_order_invoice(self, table_number, invoice_id):
        """Update the order to associate it with an invoice."""
        try:
            # Update the orders table where table_number is matched and is_enabled is true
            self.cursor.execute(
                """
                UPDATE orders
                SET invoice_id = ?
                WHERE table_number = ? AND is_enabled = 1
                """,
                (invoice_id, table_number)
            )
            self.conn.commit()  # Commit the transaction

            # Check how many rows were affected
            rows_affected = self.cursor.rowcount
            if rows_affected > 0:
                print(
                    f"Successfully updated {rows_affected} order(s) for table {table_number} with invoice {invoice_id}.")
            else:
                print(f"No active orders found for table {table_number}.")

        except Exception as e:
            print(f"Failed to update order invoice: {e}")

    def update_order_status_by_invoice(self, invoice_id):
        """Update the status of orders to 'disabled' (is_enabled = 0) based on invoice ID."""
        try:
            # Update the orders table where invoice matches
            self.cursor.execute(
                """
                UPDATE orders
                SET is_enabled = 0
                WHERE invoice_id = ?
                """,
                (invoice_id,)
            )
            self.conn.commit()  # Commit the transaction

            # Check how many rows were affected
            rows_affected = self.cursor.rowcount
            if rows_affected > 0:
                print(f"Successfully updated {rows_affected} order(s) with invoice {invoice_id} to disabled.")
            else:
                print(f"No orders found with invoice {invoice_id}.")

        except Exception as e:
            print(f"Failed to update order status: {e}")

    def get_enabled_invoices(self):
        """Fetch all invoices where is_enabled = 1."""
        self.cursor.execute("SELECT id, created_date FROM invoices WHERE is_enabled = 1")
        return self.cursor.fetchall()

    def add_invoice(self, created_date):
        """Insert a new invoice."""
        self.cursor.execute("INSERT INTO invoices (created_date, is_enabled) VALUES (?, 1)", (created_date,))
        self.conn.commit()

    def remove_invoice(self, invoice_id):
        """Disable an invoice by setting is_enabled to 0."""
        self.cursor.execute("UPDATE invoices SET is_enabled = 0 WHERE id = ?", (invoice_id,))
        self.conn.commit()

    def get_grand_total(self, invoice_id):
        """Calculate grand total from orders where invoice_id = ? and is_enabled = 0."""
        self.cursor.execute("""
            SELECT SUM(
                (o.qty * m.unit_price) + 
                ((o.qty * m.unit_price) * IFNULL(o.tax, 0) / 100) - 
                ((o.qty * m.unit_price) * IFNULL(o.discount, 0) / 100)
            )
            FROM orders o
            JOIN menu m ON o.menu_id = m.id
            WHERE o.invoice_id = ? AND o.is_enabled = 0
        """, (invoice_id,))

        result = self.cursor.fetchone()
        return result[0] if result[0] is not None else 0

