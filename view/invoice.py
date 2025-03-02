import os
import webbrowser

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QHBoxLayout, QHeaderView, QSizePolicy, QSpacerItem, QMessageBox, QWidget, QDialog, QFormLayout, QSpinBox, QComboBox,
    QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from functools import partial
from model.model import Model  # Ensure this matches your existing model
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime

class InvoiceView(QWidget):
    def __init__(self):
        super().__init__()
        self.model = Model()  # Use the model to fetch data
        self.setup_ui()
        self.load_table_numbers()  # Load available table numbers
        self.load_invoice_data()  # Load invoices initially

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Row for table number dropdown
        filter_layout = QHBoxLayout()

        table_label = QLabel("Table Number:")
        table_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Prevents stretching
        filter_layout.addWidget(table_label)

        self.table_number_dropdown = QComboBox()
        self.table_number_dropdown.setFixedWidth(200)
        self.table_number_dropdown.currentIndexChanged.connect(self.load_invoice_data)

        filter_layout.addWidget(self.table_number_dropdown)
        filter_layout.addStretch()  # Push everything to the left

        main_layout.addLayout(filter_layout)

        # Table widget for displaying invoices
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Order ID", "Table Number", "Order Date", "Menu Name", "Unit Price", "Quantity", "Tax", "Discount", "Total",
            "Actions"
        ])
        self.table.verticalHeader().setDefaultSectionSize(60)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(QLabel("Order Records"))
        main_layout.addWidget(self.table)

        # self.refresh_button = QPushButton("Refresh")
        # self.refresh_button.clicked.connect(self.load_invoice_data)
        # main_layout.addWidget(self.refresh_button)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # Grand Total Layout
        total_layout = QHBoxLayout()
        total_layout.addStretch()  # Push total to the right

        self.grand_total_label = QLabel("Grand Total: $0.00")
        self.grand_total_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 100px;")

        total_layout.addWidget(self.grand_total_label)
        main_layout.addLayout(total_layout)

        # Generate Invoice Button (Export to PDF)
        self.generate_invoice_button = QPushButton("Generate Invoice")
        self.generate_invoice_button.setStyleSheet("""
                            QPushButton {
                                background-color: #4CAF50;  /* Green background */
                                color: white;               /* White text */
                                font-weight: bold;          /* Bold text */
                                padding: 10px 20px;         /* Padding around the button */
                                border-radius: 10px;         /* Rounded corners */
                                border: none;               /* No border */
                            }
                            QPushButton:hover {
                                background-color: #45a049;  /* Darker green on hover */
                            }
                        """)
        self.generate_invoice_button.clicked.connect(self.generate_invoice_pdf)
        filter_layout.addWidget(self.generate_invoice_button)

        self.setLayout(main_layout)

    def load_table_numbers(self):
        """Load available table numbers from the 'orders' database into the dropdown."""
        try:
            self.table_number_dropdown.clear()  # Clear existing items first
            table_numbers = self.model.get_table_numbers()
            self.table_number_dropdown.addItem("All", None)  # Default: Show all invoices
            for table_number in table_numbers:
                self.table_number_dropdown.addItem(str(table_number), table_number)
        except Exception as e:
            print(f"Failed to load table numbers: {e}")

    def load_invoice_data(self):
        """Fetch and display invoices based on the selected table number."""
        try:
            selected_table = self.table_number_dropdown.currentData()  # Get selected table number
            invoices = self.model.get_invoices(selected_table)  # Pass selected table for filtering
            self.table.setRowCount(0)  # Clear existing table data first
            self.table.setRowCount(len(invoices))

            grand_total = 0  # Initialize grand total

            for row_idx, (order_id, table_number, order_date, menu_name, unit_price, qty, tax, discount) in enumerate(
                    invoices):
                total = (unit_price * qty) + ((tax / 100) * unit_price * qty) - ((discount / 100) * unit_price * qty)
                grand_total += total  # Accumulate grand total

                # Create table items and disable editing
                items = [
                    QTableWidgetItem(str(order_id)),
                    QTableWidgetItem(str(table_number)),
                    QTableWidgetItem(str(order_date)),
                    QTableWidgetItem(menu_name),
                    QTableWidgetItem(f"${unit_price:.2f}"),
                    QTableWidgetItem(str(qty)),
                    QTableWidgetItem(f"{tax:.2f}"),
                    QTableWidgetItem(f"{discount:.2f}"),
                    QTableWidgetItem(f"${total:.2f}")
                ]

                for item in items:
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Disable editing

                for col_idx, item in enumerate(items):
                    self.table.setItem(row_idx, col_idx, item)

                # Create action buttons (Update & Delete)
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)

                update_button = QPushButton("Update")
                update_button.setFixedHeight(40)
                update_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db; 
                        color: white;               
                        font-weight: bold;         
                        padding: 5px 10px;        
                        border-radius: 10px;         
                        border: none;      
                    }
                    QPushButton:hover {
                        background-color: blue;  
                    }
                """)
                update_button.clicked.connect(
                    partial(self.open_update_dialog, order_id, table_number, order_date, menu_name, unit_price, qty,
                            tax, discount))

                delete_button = QPushButton("Delete")
                delete_button.setFixedHeight(40)
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c; 
                        color: white;               
                        font-weight: bold;         
                        padding: 5px 10px;        
                        border-radius: 10px;         
                        border: none;      
                    }
                    QPushButton:hover {
                        background-color: red;  
                    }
                """)
                delete_button.clicked.connect(partial(self.confirm_delete, order_id))

                action_layout.addWidget(update_button)
                action_layout.addWidget(delete_button)
                action_widget.setLayout(action_layout)

                self.table.setCellWidget(row_idx, 9, action_widget)

            # Update the Grand Total label
            self.grand_total_label.setText(f"Grand Total: ${grand_total:.2f}")

        except Exception as e:
            print(f"Failed to load invoices: {e}")

    def confirm_delete(self, order_id):
        # Show a confirmation dialog before deletion
        reply = QMessageBox.question(self, "Confirm Deletion",
                                     "Are you sure you want to delete this invoice?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_invoice(order_id)  # Proceed with deletion if confirmed

    def delete_invoice(self, order_id):
        try:
            self.model.disable_invoice(order_id)
            self.load_invoice_data()  # Refresh table after deletion
            self.load_table_numbers()
        except Exception as e:
            print(f"Failed to delete invoice: {e}")

    def open_update_dialog(self, order_id, table_number, order_date, menu_name, unit_price, qty, tax, discount):
        invoice_data = (order_id, table_number, order_date, menu_name, unit_price, qty, tax, discount)
        dialog = UpdateDialog(invoice_data, self.model, self)
        dialog.exec()  # Opens the dialog and waits for user action

    # work when call it
    def refresh_invoice_data(self):
        try:
            print("Refresh Invoice...")
            self.load_invoice_data()
            self.load_table_numbers()

        except Exception as e:
            print(f"Failed to refresh invoice data: {e}")

    def generate_invoice_pdf(self):
        """Generate the invoice as a PDF with dynamic height and view it."""
        try:
            invoice_id = self.model.get_last_invoice_id()
            pdf_filename = "invoice.pdf"

            selected_table = self.table_number_dropdown.currentData()
            if selected_table is None:
                QMessageBox.warning(self, "Error", "Please select a table number before generating the invoice.")
                return

            invoice_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Fetch invoice data
            invoices = self.model.get_invoices(selected_table)
            num_items = len(invoices)

            # Define base height and calculate extra height based on the number of items
            base_height = 600  # Minimum height
            extra_height_per_item = 30  # Additional height per item
            dynamic_height = base_height + (num_items * extra_height_per_item)

            # Create the PDF canvas with the dynamic height
            custom_size = (360, dynamic_height)
            c = canvas.Canvas(pdf_filename, pagesize=custom_size)

            # Adjusted positions
            left_margin = 30
            column_width = 80
            y_pos1 = dynamic_height - 50  # Adjusted based on total height

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(130, y_pos1, f"Restaurant MS")

            y_pos2 = y_pos1 - 40
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left_margin, y_pos2, f"Table Number: {selected_table}")
            c.drawString(left_margin, y_pos2 - 20, f"Date: {invoice_date}")
            c.drawString(left_margin, y_pos2 - 40, f"Invoice: {invoice_id}")

            # Table Header
            y_pos3 = y_pos2 - 80
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left_margin, y_pos3, "Menu Name")
            c.drawString(left_margin + column_width, y_pos3, "Unit Price")
            c.drawString(left_margin + 2 * column_width, y_pos3, "Quantity")
            c.drawString(left_margin + 3 * column_width, y_pos3, "Total")

            # Print invoice items
            y_position = y_pos3 - 20
            total_tax = total_discount = grand_total = subtotal = 0
            total_tax_amount = total_discount_amount = 0

            for (order_id, table_number, order_date, menu_name, unit_price, qty, tax, discount) in invoices:
                total = unit_price * qty
                tax_amount = (tax / 100) * total
                discount_amount = (discount / 100) * total

                total_tax += tax_amount
                total_discount += discount_amount
                grand_total += total + tax_amount - discount_amount
                subtotal += total

                total_tax_amount += tax_amount
                total_discount_amount += discount_amount

                c.setFont("Helvetica", 10)
                c.drawString(left_margin, y_position, menu_name)
                c.drawString(left_margin + column_width, y_position, f"${unit_price:.2f}")
                c.drawString(left_margin + 2 * column_width, y_position, str(qty))
                c.drawString(left_margin + 3 * column_width, y_position, f"${total:.2f}")

                y_position -= 40  # Move down for next row

            # Calculate average tax and discount
            avg_tax_percentage = (total_tax_amount / subtotal) * 100 if subtotal > 0 else 0
            avg_discount_percentage = (total_discount_amount / subtotal) * 100 if subtotal > 0 else 0

            # Add totals
            c.setFont("Helvetica-Bold", 10)
            c.drawString(left_margin + 2 * column_width, y_position - 10, f"Subtotal: ${subtotal:.2f}")
            c.drawString(left_margin + 2 * column_width, y_position - 30,
                         f"Tax ({avg_tax_percentage:.2f}%): ${total_tax:.2f}")
            c.drawString(left_margin + 2 * column_width, y_position - 50,
                         f"Discount ({avg_discount_percentage:.2f}%): -${total_discount:.2f}")
            c.drawString(left_margin + 2 * column_width, y_position - 70, f"Grand Total: ${grand_total:.2f}")

            # Save PDF
            c.save()

            # Update data in DB
            self.model.insert_new_invoice(invoice_date)
            self.model.update_order_invoice(selected_table, invoice_id)
            self.model.update_order_status_by_invoice(invoice_id)

            self.load_invoice_data()
            self.load_table_numbers()

            # Open the generated PDF
            if os.name == 'nt':  # Windows
                os.startfile(pdf_filename)
            elif os.name == 'posix':  # macOS/Linux
                webbrowser.open(f"file://{os.path.realpath(pdf_filename)}")

        except Exception as e:
            print(f"Failed to generate invoice PDF: {e}")
            QMessageBox.warning(self, "Error", "Failed to generate PDF.")

class UpdateDialog(QDialog):
    def __init__(self, invoice_data, model, parent=None):
        super().__init__(parent)
        self.invoice_data = invoice_data  # Holds the current invoice data
        self.model = model
        self.setWindowTitle("Update Invoice")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # Fetch valid table numbers from the model
        valid_table_numbers = self.model.get_valid_table_numbers()  # Ensure this method exists

        # Table Number Input (Restricted to valid numbers)
        self.table_number_input = QSpinBox()
        if valid_table_numbers:
            min_table = min(valid_table_numbers)
            max_table = max(valid_table_numbers)
            self.table_number_input.setRange(min_table, max_table)  # Restrict to valid table numbers
            self.table_number_input.setValue(self.invoice_data[1])  # Set initial value

        form_layout.addRow("Table Number:", self.table_number_input)

        # Menu Name Input (ComboBox with existing menu names)
        self.menu_name_input = QComboBox()
        menu_names = self.model.get_menu_names()  # Ensure this method exists
        self.menu_name_input.addItems(menu_names)
        self.menu_name_input.setCurrentText(self.invoice_data[3])  # Set initial value
        form_layout.addRow("Menu Name:", self.menu_name_input)

        # Quantity Input
        self.qty_input = QSpinBox()
        self.qty_input.setValue(self.invoice_data[5])
        form_layout.addRow("Quantity:", self.qty_input)

        # Tax Input
        self.tax_input = QDoubleSpinBox()
        self.tax_input.setValue(self.invoice_data[6])
        form_layout.addRow("Tax (%):", self.tax_input)

        # Discount Input
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setValue(self.invoice_data[7])
        form_layout.addRow("Discount (%):", self.discount_input)

        # Save and Cancel Buttons
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_update)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        # Style buttons
        self.apply_button_styles()

        self.setLayout(layout)

    def apply_button_styles(self):
        # Style Save button
        self.save_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                margin: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
            QPushButton:disabled {
                background-color: #9e9e9e;
                color: #d3d3d3;
            }
        """)

        # Style Cancel button
        self.cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                margin: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #9e9e9e;
                color: #d3d3d3;
            }
        """)

    def save_update(self):
        # Get updated values from inputs
        updated_data = (
            self.table_number_input.value(),
            self.menu_name_input.currentText(),
            self.qty_input.value(),
            self.tax_input.value(),
            self.discount_input.value(),
            self.invoice_data[0]  # Passing the original Order ID
        )

        # Call the model to update the database
        self.model.update_invoice(updated_data)

        # Refresh the data in the parent (InvoiceView) and close the dialog
        self.parent().load_invoice_data()
        self.parent().load_table_numbers()

        # Close the dialog after saving
        self.accept()
