from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout
from model.model import Model


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
            # Set the items and set flags to make them uneditable
            invoice_item = QTableWidgetItem(str(invoice_id))
            invoice_item.setFlags(invoice_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make uneditable
            self.table_widget.setItem(row_index, 0, invoice_item)

            created_date_item = QTableWidgetItem(str(created_date))
            created_date_item.setFlags(created_date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make uneditable
            self.table_widget.setItem(row_index, 1, created_date_item)

            grand_total_item = QTableWidgetItem(f"${grand_total:.2f}")
            grand_total_item.setFlags(grand_total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make uneditable
            self.table_widget.setItem(row_index, 2, grand_total_item)

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

    # work when call it
    def refresh_report_data(self):
        try:
            print("Refresh Invoice...")
            self.load_invoice_data()

        except Exception as e:
            print(f"Failed to refresh invoice data: {e}")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = ReportView()
    window.show()
    sys.exit(app.exec())
