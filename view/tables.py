from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, \
    QDialog, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QTextEdit, QHeaderView
from model.model import Model


class TableView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tables")
        self.resize(600, 400)
        self.model = Model()

        self.layout = QVBoxLayout(self)

        # Top Layout for Add Table Button
        top_layout = QHBoxLayout()
        self.add_table_button = QPushButton("Add Table")
        self.add_table_button.setStyleSheet("""
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
        self.add_table_button.clicked.connect(self.open_add_table_dialog)
        top_layout.addWidget(self.add_table_button)
        top_layout.addStretch()  # Push button to the left
        self.layout.addLayout(top_layout)

        # Table Widget
        self.table_widget = QTableWidget()

        self.layout.addWidget(self.table_widget)

        self.load_table_data()

    def load_table_data(self):
        """Reload table data from the model."""
        self.table_widget.setRowCount(0)  # Clear table before reloading
        data = self.model.get_tables()  # Get table data

        self.table_widget.rowHeight(50)
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Table Number", "Description", "Action"])
        self.table_widget.setColumnWidth(0, 100)
        self.table_widget.setColumnWidth(1, 300)
        self.table_widget.setColumnWidth(2, 200)

        self.table_widget.verticalHeader().setDefaultSectionSize(60)  # Increase row height
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Make table uneditable
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        for row_index, (table_number, description) in enumerate(data):
            self.table_widget.insertRow(row_index)
            self.table_widget.setItem(row_index, 0, QTableWidgetItem(str(table_number)))
            self.table_widget.setItem(row_index, 1, QTableWidgetItem(description))

            # Action buttons with styling
            action_layout = QHBoxLayout()
            update_button = QPushButton("Update")
            delete_button = QPushButton("Delete")

            # Set button colors
            # update_button.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
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
            # delete_button.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
            delete_button.setFixedHeight(40)
            delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c; 
                        color: white;               
                        font-weight: bold;         
                        padding: 10px 20px;        
                        border-radius: 10px;         
                        border: none;      
                    }
                    QPushButton:hover {
                        background-color: red;  
                    }
                """)

            update_button.clicked.connect(
                lambda _, tn=table_number, desc=description: self.open_update_dialog(tn, desc))
            delete_button.clicked.connect(lambda _, tn=table_number: self.delete_table(tn))

            action_layout.addWidget(update_button)
            action_layout.addWidget(delete_button)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table_widget.setCellWidget(row_index, 2, action_widget)

    def delete_table(self, table_number):
        """Delete a table after confirmation."""
        confirmation = QMessageBox.question(self, "Delete Table", f"Are you sure to delete table {table_number}?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmation == QMessageBox.StandardButton.Yes:
            self.model.delete_table(table_number)
            self.load_table_data()  # Refresh table after deletion

    def open_update_dialog(self, table_number, description):
        """Open the dialog to update the table."""
        dialog = UpdateTableDialog(self.model, table_number, description, self)
        if dialog.exec():
            self.load_table_data()  # Refresh table after update

    def open_add_table_dialog(self):
        """Open the dialog to add a new table."""
        dialog = AddTableDialog(self.model, self)
        if dialog.exec():
            self.load_table_data()  # Refresh table after adding


class UpdateTableDialog(QDialog):
    def __init__(self, model, table_number, description, parent=None):
        super().__init__(parent)
        self.model = model
        self.table_number = table_number
        self.setWindowTitle("Update Table")
        self.init_ui(description)

    def init_ui(self, description):
        layout = QFormLayout(self)

        # Table Number (Read-only)
        self.table_number_label = QLabel(str(self.table_number))
        layout.addRow("Table Number:", self.table_number_label)

        # Description (Editable - Increased Size)
        self.description_input = QTextEdit()
        self.description_input.setText(description)
        self.description_input.setFixedHeight(30)  # Increase height for better editing
        layout.addRow("Description:", self.description_input)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.update_table)
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



    def update_table(self):
        new_description = self.description_input.toPlainText().strip()  # Get multiline text
        if new_description:
            self.model.update_table(self.table_number, new_description)
        self.accept()


class AddTableDialog(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Add New Table")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        # Table Number (Editable by user)
        self.table_number_input = QLineEdit()
        layout.addRow("Table Number:", self.table_number_input)

        # Description (Editable)
        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(30)  # Set height for better editing
        layout.addRow("Description:", self.description_input)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.add_table)
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

    def add_table(self):
        table_number = self.table_number_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if table_number and description:
            self.model.add_table(table_number, description)
        self.accept()