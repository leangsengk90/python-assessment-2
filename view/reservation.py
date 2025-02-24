from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, \
    QDialog, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QDateEdit, QTimeEdit, QHeaderView
from PyQt6.QtCore import QDate, QTime
from model.model import Model

class ReservationView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reservations")
        self.resize(800, 600)
        self.model = Model()

        self.layout = QVBoxLayout(self)

        # Top Layout for Add Reservation Button
        top_layout = QHBoxLayout()
        self.add_reservation_button = QPushButton("Add Reservation")
        self.add_reservation_button.setStyleSheet("""
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
        self.add_reservation_button.clicked.connect(self.open_add_reservation_dialog)
        top_layout.addWidget(self.add_reservation_button)
        top_layout.addStretch()  # Push button to the left
        self.layout.addLayout(top_layout)

        # Table Widget
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)
        self.load_reservation_data()

    def load_reservation_data(self):
        """Reload reservation data from the model."""
        self.table_widget.setRowCount(0)  # Clear table before reloading
        data = self.model.get_reservations()  # Get reservation data

        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["Reserve Number", "Table", "Name", "Phone", "Date", "Time", "Action"])
        self.table_widget.setColumnWidth(0, 100)
        self.table_widget.setColumnWidth(1, 100)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)
        self.table_widget.setColumnWidth(4, 100)
        self.table_widget.setColumnWidth(5, 100)
        self.table_widget.setColumnWidth(6, 200)

        self.table_widget.verticalHeader().setDefaultSectionSize(60)  # Increase row height
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Make table uneditable
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        for row_index, row_data in enumerate(data):
            reserve_number, tables, name, phone, date, time = row_data[:6]  # Unpack only the first 6 values

            self.table_widget.insertRow(row_index)

            self.table_widget.setItem(row_index, 0, QTableWidgetItem(str(reserve_number)))
            self.table_widget.setItem(row_index, 1, QTableWidgetItem(str(tables)))
            self.table_widget.setItem(row_index, 2, QTableWidgetItem(name))
            self.table_widget.setItem(row_index, 3, QTableWidgetItem(phone))
            self.table_widget.setItem(row_index, 4, QTableWidgetItem(date))
            self.table_widget.setItem(row_index, 5, QTableWidgetItem(time))

            # Action buttons with styling
            action_layout = QHBoxLayout()
            update_button = QPushButton("Update")
            delete_button = QPushButton("Delete")

            # Set button colors
            update_button.setFixedHeight(40)
            update_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;  /* Green background */
                        color: white;               /* White text */
                        font-weight: bold;          /* Bold text */
                        padding: 10px 20px;         /* Padding around the button */
                        border-radius: 10px;         /* Rounded corners */
                        border: none;               /* No border */
                    }
                    QPushButton:hover {
                        background-color: blue;  /* Darker green on hover */
                    }
                """)
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

            update_button.clicked.connect(
                lambda _, rn=reserve_number, tbl=tables, nm=name, ph=phone, dt=date, tm=time: self.open_update_dialog(rn, tbl, nm, ph, dt, tm))
            delete_button.clicked.connect(lambda _, rn=reserve_number: self.delete_reservation(rn))

            action_layout.addWidget(update_button)
            action_layout.addWidget(delete_button)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table_widget.setCellWidget(row_index, 6, action_widget)

    def delete_reservation(self, reserve_number):
        """Delete a reservation after confirmation."""
        confirmation = QMessageBox.question(self, "Delete Reservation", f"Are you sure to delete reservation {reserve_number}?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmation == QMessageBox.StandardButton.Yes:
            self.model.delete_reservation(reserve_number)
            self.load_reservation_data()  # Refresh table after deletion

    def open_update_dialog(self, reserve_number, tables, name, phone, date, time):
        """Open the dialog to update the reservation."""
        dialog = UpdateReservationDialog(self.model, reserve_number, tables, name, phone, date, time, self)
        if dialog.exec():
            self.load_reservation_data()  # Refresh table after update

    def open_add_reservation_dialog(self):
        """Open the dialog to add a new reservation."""
        dialog = AddReservationDialog(self.model, self)
        if dialog.exec():
            self.load_reservation_data()  # Refresh table after adding


class UpdateReservationDialog(QDialog):
    def __init__(self, model, reserve_number, tables, name, phone, date, time, parent=None):
        super().__init__(parent)
        self.model = model
        self.reserve_number = reserve_number
        self.setWindowTitle("Update Reservation")
        self.init_ui(tables, name, phone, date, time)

    def init_ui(self, tables, name, phone, date, time):
        layout = QFormLayout(self)

        # Reserve Number (Read-only)
        self.reserve_number_label = QLabel(str(self.reserve_number))
        layout.addRow("Reserve Number:", self.reserve_number_label)

        # Tables (Editable)
        self.tables_input = QLineEdit(str(tables))
        layout.addRow("Table(s):", self.tables_input)

        # Name (Editable)
        self.name_input = QLineEdit(name)
        layout.addRow("Customer Name:", self.name_input)

        # Phone (Editable)
        self.phone_input = QLineEdit(phone)
        layout.addRow("Phone:", self.phone_input)

        # Date (Editable, Calendar Picker)
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.fromString(date, "yyyy-MM-dd"))  # Set initial date
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        layout.addRow("Date:", self.date_input)

        # Time (Editable, Time Picker)
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.fromString(time, "HH:mm"))  # Set initial time
        layout.addRow("Time:", self.time_input)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.update_reservation)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def update_reservation(self):
        tables = self.tables_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")

        if tables and name and phone and date and time:
            self.model.update_reservation(self.reserve_number, tables, name, phone, date, time)
        self.accept()


class AddReservationDialog(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Add New Reservation")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        # Tables (Editable)
        self.tables_input = QLineEdit()
        layout.addRow("Table(s):", self.tables_input)

        # Name (Editable)
        self.name_input = QLineEdit()
        layout.addRow("Customer Name:", self.name_input)

        # Phone (Editable)
        self.phone_input = QLineEdit()
        layout.addRow("Phone:", self.phone_input)

        # Date (Editable, Calendar Picker)
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())  # Default to today
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        layout.addRow("Date:", self.date_input)

        # Time (Editable, Time Picker)
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())  # Default to current time
        layout.addRow("Time:", self.time_input)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.add_reservation)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def add_reservation(self):
        tables = self.tables_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")

        if tables and name and phone and date and time:
            self.model.add_reservation(tables, name, phone, date, time)
        self.accept()
