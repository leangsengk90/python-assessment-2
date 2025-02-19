from functools import partial

from PyQt6.QtCore import Qt

from model.model import Model

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, \
    QMessageBox, QDialog, QFormLayout, QComboBox, QLineEdit, QSpinBox
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import webbrowser

class ReportView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Report")
        self.resize(600, 400)
        self.model = Model()

        self.layout = QVBoxLayout(self)

        # Table Widget
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

        self.load_invoice_data()

    from functools import partial

    def load_invoice_data(self):
        """Load invoice data where is_enabled = 1."""
        self.table_widget.setRowCount(0)  # Clear table before reloading
        data = self.model.get_enabled_invoices()  # Get enabled invoices

        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Invoice ID", "Created Date", "Grand Total", "Actions"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        for row_index, (invoice_id, created_date) in enumerate(data):
            grand_total = self.model.get_grand_total(invoice_id)  # Query grand total

            self.table_widget.insertRow(row_index)
            self.table_widget.setItem(row_index, 0, QTableWidgetItem(str(invoice_id)))
            self.table_widget.setItem(row_index, 1, QTableWidgetItem(str(created_date)))
            self.table_widget.setItem(row_index, 2, QTableWidgetItem(f"${grand_total:.2f}"))

            # Action buttons
            action_layout = QHBoxLayout()
            view_button = QPushButton("View")
            update_button = QPushButton("Update")
            delete_button = QPushButton("Delete")

            view_button.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
            update_button.setStyleSheet("background-color: #f1c40f; color: white; font-weight: bold;")
            delete_button.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")

            action_layout.addWidget(view_button)
            action_layout.addWidget(update_button)
            action_layout.addWidget(delete_button)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table_widget.setCellWidget(row_index, 3, action_widget)

            # Use functools.partial to pass parameters explicitly
            view_button.clicked.connect(partial(self.view_invoice, invoice_id, created_date))
            update_button.clicked.connect(partial(self.update_invoices, invoice_id))
            # delete_button.clicked.connect(partial(self.delete_invoice, invoice_id))

    def update_invoices(self, invoice_id):
        """Open update dialog to modify orders."""
        dialog = UpdateInvoiceDialog(self.model, invoice_id)
        if dialog.exec():  # If dialog is accepted (saved)
            self.load_invoice_data()  # Refresh report

    def view_invoice(self, invoice_id, get_invoice_date):
        """Generate the invoice as a PDF and view it."""
        print("ID:", invoice_id)
        try:
            # Set up the PDF file with custom page size (360x600 points)
            pdf_filename = f"invoice_{invoice_id}.pdf"
            custom_size = (360, 600)  # Custom width and height in points
            c = canvas.Canvas(pdf_filename, pagesize=custom_size)

            # Fetch the table number for the selected invoice from the 'orders' table
            table_number = self.model.get_table_number_by_invoice(invoice_id)
            if not table_number:
                QMessageBox.warning(self, "Error", "Table number not found for the invoice.")
                return

            invoice_date = get_invoice_date

            # Adjusted positions to fit the custom size
            left_margin = 30  # Reduced left margin
            column_width = 80  # Decreased column width to fit better
            y_pos1 = 550  # Adjusted based on custom size

            # Define the title as the table number
            c.setFont("Helvetica-Bold", 16)
            c.drawString(130, y_pos1, f"Restaurant MS")

            y_pos2 = y_pos1 - 40
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left_margin, y_pos2, f"Table Number: {table_number}")
            c.drawString(left_margin, y_pos2 - 20, f"Date: {invoice_date}")
            c.drawString(left_margin, y_pos2 - 40, f"Invoice: {invoice_id}")

            y_pos3 = y_pos2 - 80
            # Add a table header without table_number, order_id, and order_date
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left_margin, y_pos3, "Menu Name")
            c.drawString(left_margin + column_width, y_pos3, "Unit Price")
            c.drawString(left_margin + 2 * column_width, y_pos3, "Quantity")
            c.drawString(left_margin + 3 * column_width, y_pos3, "Total")

            # Fetch invoice data and print it
            invoices = self.model.get_invoices_by_invoice_id(invoice_id)

            y_position = y_pos3 - 20  # Start printing rows

            total_tax = 0
            total_discount = 0
            grand_total = 0
            subtotal = 0  # Initialize subtotal
            total_tax_amount = 0  # Accumulate tax amounts to calculate average tax
            total_discount_amount = 0  # Accumulate discount amounts to calculate average discount

            for (order_id, menu_name, unit_price, qty, tax, discount) in invoices:
                # Calculate total without tax and discount
                total = unit_price * qty
                tax_amount = (tax / 100) * total
                discount_amount = (discount / 100) * total

                # Accumulate the totals
                total_tax += tax_amount
                total_discount += discount_amount
                grand_total += total + tax_amount - discount_amount
                subtotal += total  # Accumulate the subtotal (without tax and discount)

                total_tax_amount += tax_amount  # Accumulate tax amounts
                total_discount_amount += discount_amount  # Accumulate discount amounts

                c.setFont("Helvetica", 10)
                c.drawString(left_margin, y_position, menu_name)
                c.drawString(left_margin + column_width, y_position, f"${unit_price:.2f}")
                c.drawString(left_margin + 2 * column_width, y_position, str(qty))
                c.drawString(left_margin + 3 * column_width, y_position, f"${total:.2f}")

                y_position -= 40  # Move down for the next row

            # Add Subtotal, Tax, Discount, and Grand Total with proper spacing
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left_margin + 2 * column_width, y_position - 10, f"Subtotal: ${subtotal:.2f}")
            c.drawString(left_margin + 2 * column_width, y_position - 30,
                         f"Tax (${total_tax * 100 / subtotal:.2f}%): ${total_tax:.2f}")
            c.drawString(left_margin + 2 * column_width, y_position - 50,
                         f"Discount (${total_discount * 100 / subtotal:.2f}%): -${total_discount:.2f}")
            c.drawString(left_margin + 2 * column_width, y_position - 70, f"Grand Total: ${grand_total:.2f}")

            # Save the PDF
            c.save()

            # Update data in DB
            # self.model.insert_new_invoice(invoice_date)
            # self.model.update_order_invoice(table_number, invoice_id)
            # self.model.update_order_status_by_invoice(invoice_id)

            self.load_invoice_data()

            # Open the generated PDF using the default system PDF viewer
            if os.name == 'nt':  # Windows
                os.startfile(pdf_filename)
            elif os.name == 'posix':  # macOS and Linux
                webbrowser.open(f"file://{os.path.realpath(pdf_filename)}")

        except Exception as e:
            print(f"Failed to generate invoice PDF: {e}")
            QMessageBox.warning(self, "Error", "Failed to generate PDF.")


    def refresh_report_data(self):
        try:
            print("Refresh Invoice...")
            self.load_invoice_data()

        except Exception as e:
            print(f"Failed to refresh invoice data: {e}")

class UpdateInvoiceDialog(QDialog):
    def __init__(self, model, invoice_id):
        super().__init__()
        self.setWindowTitle("Update Orders")
        self.resize(900, 500)  # 🔹 Increased size for better UI
        self.model = model
        self.invoice_id = invoice_id
        self.orders = self.model.get_orders_by_invoice(invoice_id)  # Fetch orders
        self.menu_items = self.model.get_all_menu_items()  # Fetch menu (menu_id, menu_name)

        self.layout = QVBoxLayout(self)

        # Table Widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Order ID", "Menu", "Quantity", "Tax", "Discount", "Action"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table_widget)

        self.deleted_orders = []  # 🔹 Store orders to delete
        self.load_order_data()

        # Save Button
        save_button = QPushButton("Save Changes")
        save_button.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(save_button)

    def load_order_data(self):
        """Load orders into the table with dropdown for menu selection."""
        self.table_widget.setRowCount(0)  # Clear table before reloading

        for row_index, (order_id, menu_name, qty, tax, discount) in enumerate(self.orders):
            self.table_widget.insertRow(row_index)

            # 🔹 Dropdown (QComboBox) for Menu Selection
            menu_dropdown = QComboBox()
            menu_dropdown.addItems([name for _, name in self.menu_items])  # Add menu names
            menu_dropdown.setCurrentText(menu_name)  # Set current selection
            self.table_widget.setCellWidget(row_index, 1, menu_dropdown)

            # Other editable fields
            self.table_widget.setItem(row_index, 2, QTableWidgetItem(str(qty)))
            self.table_widget.setItem(row_index, 3, QTableWidgetItem(str(tax)))
            self.table_widget.setItem(row_index, 4, QTableWidgetItem(str(discount)))

            # 🔹 Order ID (Non-Editable)
            order_id_item = QTableWidgetItem(str(order_id))
            order_id_item.setFlags(order_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make it read-only
            self.table_widget.setItem(row_index, 0, order_id_item)

            # 🔹 Remove Button
            remove_button = QPushButton("Remove")
            remove_button.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
            remove_button.clicked.connect(lambda _, row=row_index: self.remove_order(row))  # Handle row removal
            self.table_widget.setCellWidget(row_index, 5, remove_button)

    def remove_order(self, row_index):
        """Remove order from the table and mark it for deletion."""
        order_id_item = self.table_widget.item(row_index, 0)
        if order_id_item:
            order_id = int(order_id_item.text())  # Get order ID
            self.deleted_orders.append(order_id)  # Store for deletion
        self.table_widget.removeRow(row_index)  # Remove from UI

    def save_changes(self):
        """Save the updated orders to the database."""
        updated_orders = []

        for row_index in range(self.table_widget.rowCount()):
            menu_dropdown = self.table_widget.cellWidget(row_index, 1)
            menu_name = menu_dropdown.currentText()
            menu_id = self.model.get_menu_id_by_name(menu_name)  # Convert to menu_id

            qty = int(self.table_widget.item(row_index, 2).text())
            tax = float(self.table_widget.item(row_index, 3).text())
            discount = float(self.table_widget.item(row_index, 4).text())
            order_id = int(self.table_widget.item(row_index, 0).text())  # Read-only column

            updated_orders.append((menu_id, qty, tax, discount, order_id))

        # 🔹 Update existing orders
        self.model.update_orders(updated_orders)

        # 🔹 Delete removed orders
        for order_id in self.deleted_orders:
            self.model.delete_order(order_id)

        self.accept()  # Close dialog