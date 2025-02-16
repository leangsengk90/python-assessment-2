from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QHBoxLayout, QHeaderView, QSizePolicy, QSpacerItem, QMessageBox, QWidget, QDialog, QFormLayout, QSpinBox, QComboBox,
    QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from functools import partial
from model.model import Model  # Ensure this matches your existing model

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
        filter_layout.addWidget(QLabel("Table Number:"))

        self.table_number_dropdown = QComboBox()
        self.table_number_dropdown.currentIndexChanged.connect(self.load_invoice_data)  # Reload on selection change
        filter_layout.addWidget(self.table_number_dropdown)

        main_layout.addLayout(filter_layout)

        # Table widget for displaying invoices
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Order ID", "Table Number", "Order Date", "Menu Name", "Unit Price", "Quantity", "Tax", "Discount", "Total",
            "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(QLabel("Invoice Records"))
        main_layout.addWidget(self.table)

        # self.refresh_button = QPushButton("Refresh")
        # self.refresh_button.clicked.connect(self.load_invoice_data)
        # main_layout.addWidget(self.refresh_button)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)


        self.setLayout(main_layout)

    def load_table_numbers(self):
        """Load available table numbers from the 'tables' database into the dropdown."""
        try:
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
            self.table.setRowCount(len(invoices))

            for row_idx, (order_id, table_number, order_date, menu_name, unit_price, qty, tax, discount) in enumerate(
                    invoices):
                total = (unit_price * qty) + ((tax / 100) * unit_price * qty) - ((discount / 100) * unit_price * qty)

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
                update_button.setStyleSheet("background-color: #4CAF50; color: white;")
                update_button.clicked.connect(partial(self.open_update_dialog, order_id, table_number, order_date, menu_name, unit_price, qty, tax, discount))

                delete_button = QPushButton("Delete")
                delete_button.setStyleSheet("background-color: #e74c3c; color: white;")
                delete_button.clicked.connect(partial(self.confirm_delete, order_id))

                action_layout.addWidget(update_button)
                action_layout.addWidget(delete_button)
                action_widget.setLayout(action_layout)

                self.table.setCellWidget(row_idx, 9, action_widget)

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

        except Exception as e:
            print(f"Failed to refresh invoice data: {e}")


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

        # Table Number Input
        self.table_number_input = QSpinBox()
        self.table_number_input.setValue(self.invoice_data[1])  # Set initial value
        form_layout.addRow("Table Number:", self.table_number_input)

        # Menu Name Input (ComboBox with existing menu names)
        self.menu_name_input = QComboBox()
        menu_names = self.model.get_menu_names()  # This method should return a list of menu names
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

        self.setLayout(layout)

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

        # Close the dialog after saving
        self.accept()
