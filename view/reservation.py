from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, \
    QDialog, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QDateEdit, QTimeEdit, QHeaderView, QDateTimeEdit, \
    QSpinBox
from PyQt6.QtCore import QDate, QTime, QDateTime
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
        self.table_widget.setHorizontalHeaderLabels(["Reserve Number", "Table", "Name", "Phone", "Start Time", "End Time", "Action"])
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
    def __init__(self, model, reserve_number, tables, name, phone, start_time, end_time, parent=None):
        super().__init__(parent)
        self.model = model
        self.reserve_number = reserve_number
        self.setWindowTitle("Update Reservation")
        self.init_ui(tables, name, phone, start_time, end_time)

    def init_ui(self, tables, name, phone, start_time, end_time):
        layout = QFormLayout(self)

        # Reserve Number (Read-only)
        self.reserve_number_label = QLabel(str(self.reserve_number))
        layout.addRow("Reserve Number:", self.reserve_number_label)

        # Tables (Editable)
        # self.tables_input = QLineEdit(str(tables))
        # layout.addRow("Table:", self.tables_input)

        valid_table_numbers = self.model.get_valid_table_numbers()

        self.tables_input = QSpinBox()
        if valid_table_numbers:
            min_table = min(valid_table_numbers)
            max_table = max(valid_table_numbers)
            self.tables_input.setRange(min_table, max_table)  # Restrict to valid table numbers
            self.tables_input.setValue(tables)

        layout.addRow("Table:", self.tables_input)

        # Name (Editable)
        self.name_input = QLineEdit(name)
        layout.addRow("Customer Name:", self.name_input)

        # Phone (Editable)
        self.phone_input = QLineEdit(phone)
        layout.addRow("Phone:", self.phone_input)

        self.start_datetime_edit = QDateTimeEdit(self, calendarPopup=True)
        self.start_datetime_edit.setFixedWidth(400)
        self.start_datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_datetime_edit.setDateTime(QDateTime.fromString(start_time, "yyyy-MM-dd HH:mm:ss"))  # Default to current date/time
        layout.addRow("Star Time:", self.start_datetime_edit)

        self.end_datetime_edit = QDateTimeEdit(self, calendarPopup=True)
        self.end_datetime_edit.setFixedWidth(400)
        self.end_datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_datetime_edit.setDateTime(QDateTime.fromString(end_time, "yyyy-MM-dd HH:mm:ss"))  # Default to current date/time
        layout.addRow("End Time:", self.end_datetime_edit)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.update_reservation)
        buttons.rejected.connect(self.reject)

        # Access individual buttons for styling
        save_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)

        # Style the Save button
        save_button.setStyleSheet("""
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

        # Style the Cancel button
        cancel_button.setStyleSheet("""
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

        # Add buttons to layout
        layout.addRow(buttons)

    def update_reservation(self):
        tables = self.tables_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        start_time = self.start_datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_time = self.end_datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        if tables and name and phone and start_time and end_time:
            self.model.update_reservation(self.reserve_number, tables, name, phone, start_time, end_time)
        self.accept()


class AddReservationDialog(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Add New Reservation")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        # Fetch valid table numbers from the model
        valid_table_numbers = self.model.get_valid_table_numbers()  # Ensure this method exists

        # Table Number Input (Restricted to valid numbers)
        self.tables_input = QSpinBox()
        if valid_table_numbers:
            min_table = min(valid_table_numbers)
            max_table = max(valid_table_numbers)
            self.tables_input.setRange(min_table, max_table)  # Restrict to valid table numbers

        layout.addRow("Table:", self.tables_input)

        # Name (Editable)
        self.name_input = QLineEdit()
        layout.addRow("Customer Name:", self.name_input)

        # Phone (Editable)
        self.phone_input = QLineEdit()
        layout.addRow("Phone:", self.phone_input)

        self.start_datetime_edit = QDateTimeEdit(self, calendarPopup=True)
        self.start_datetime_edit.setFixedWidth(400)
        self.start_datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_datetime_edit.setDateTime(datetime.now())  # Default to current date/time
        layout.addRow("Start Time:", self.start_datetime_edit)

        self.end_datetime_edit = QDateTimeEdit(self, calendarPopup=True)
        self.end_datetime_edit.setFixedWidth(400)
        self.end_datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_datetime_edit.setDateTime(datetime.now())  # Default to current date/time
        layout.addRow("End Time:", self.end_datetime_edit)


        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.add_reservation)
        buttons.rejected.connect(self.reject)

        # Access individual buttons for styling
        save_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)

        # Style the Save button
        save_button.setStyleSheet("""
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

        # Style the Cancel button
        cancel_button.setStyleSheet("""
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

        layout.addRow(buttons)

    def add_reservation(self):
        tables = self.tables_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        start_time = self.start_datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_time = self.end_datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        if not name or not phone:
            QMessageBox.warning(self, "Input Error", "Customer Name and Phone Number are required!")
            return

            # Check if the table is already reserved
        if self.model.is_table_reserved(tables, start_time, end_time):
            QMessageBox.warning(self, "Reservation Conflict",
                                "The selected table is already reserved during this time.")
            return

        if tables and name and phone and start_time and end_time:
            self.model.add_reservation(tables, name, phone, start_time, end_time)
        self.accept()