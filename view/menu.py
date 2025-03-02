import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHBoxLayout, \
    QMessageBox, QDialog, QLineEdit, QFileDialog, QHeaderView
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from model.model import Model

class MenuView(QWidget):
    def __init__(self):
        super().__init__()
        self.model = Model()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Add Item Button (top-right)
        self.btn_add_item = QPushButton("Add Item")
        self.btn_add_item.setFixedWidth(150)
        self.btn_add_item.setStyleSheet("""
            background-color: #4CAF50; 
            color: white; 
            font-weight: bold;
            border-radius: 10px;
            padding: 10px;
        """)
        self.btn_add_item.clicked.connect(self.open_add_item_dialog)

        layout.addWidget(self.btn_add_item)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["MenuID", "Name", "Unit Price", "Image", "Action"])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        self.load_data()

        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        menu_items = self.model.get_menu_items()
        self.table.setRowCount(len(menu_items))

        # Increase row height
        self.table.verticalHeader().setDefaultSectionSize(120)  # Set row height to 100px

        # Increase column width
        self.table.setColumnWidth(0, 80)  # MenuID
        self.table.setColumnWidth(1, 200)  # Name
        self.table.setColumnWidth(2, 100)  # Unit Price
        self.table.setColumnWidth(3, 140)  # Image
        self.table.setColumnWidth(4, 200)  # Action (Buttons)

        for row_idx, (menu_id, name, unit_price, image_filename) in enumerate(menu_items):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(menu_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"${unit_price:.2f}"))

            # Make cells in columns 0, 1, and 2 uneditable
            self.table.item(row_idx, 0).setFlags(self.table.item(row_idx, 0).flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.item(row_idx, 1).setFlags(self.table.item(row_idx, 1).flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.item(row_idx, 2).setFlags(self.table.item(row_idx, 2).flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Load Image with Smooth Scaling from the images folder
            image_label = QLabel()
            image_path = self.get_image_path(image_filename)
            pixmap = self.load_image(image_path)
            if pixmap:
                pixmap = pixmap.scaled(120, 140, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)  # Use smooth scaling
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setCellWidget(row_idx, 3, image_label)

            # Action Buttons
            action_layout = QHBoxLayout()
            btn_update = QPushButton("Update")
            btn_delete = QPushButton("Delete")

            # Set colors for the buttons
            # btn_update.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
            btn_update.setStyleSheet("""
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
            # btn_delete.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
            btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;  /* Green background */
                        color: white;               /* White text */
                        font-weight: bold;          /* Bold text */
                        padding: 10px 20px;         /* Padding around the button */
                        border-radius: 10px;         /* Rounded corners */
                        border: none;               /* No border */
                    }
                    QPushButton:hover {
                        background-color: red;  /* Darker green on hover */
                    }
                """)

            btn_update.clicked.connect(lambda _, id=menu_id: self.update_item(id))
            btn_delete.clicked.connect(lambda _, id=menu_id: self.delete_item(id))

            action_layout.addWidget(btn_update)
            action_layout.addWidget(btn_delete)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)

            self.table.setCellWidget(row_idx, 4, action_widget)

    def get_image_path(self, image_filename):
        """Convert relative image path to absolute path if needed."""
        image_path = os.path.join("images", image_filename)  # Assuming images folder
        if not os.path.isabs(image_path):  # If the path is not absolute
            image_path = os.path.abspath(image_path)  # Convert to absolute path
        return image_path

    def load_image(self, image_path):
        """Try loading image and handle errors."""
        if not os.path.exists(image_path):
            print(f"Error: Image file {image_path} not found.")
            return None
        return QPixmap(image_path)

    def update_item(self, menu_id):
        """Open the Update Dialog and pass the current item data"""
        current_item = self.model.get_menu_item(menu_id)
        self.dialog = UpdateItemDialog(self, menu_id, current_item)
        self.dialog.show()

    def open_add_item_dialog(self):
        """Open the Add Item Dialog"""
        self.dialog = AddItemDialog(self)
        self.dialog.show()

    def delete_item(self, menu_id):
        """Delete the item from the menu"""
        confirm = QMessageBox.question(self, "Delete Item", "Are you sure you want to delete this item?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.model.delete_menu_item(menu_id)
            self.load_data()  # Reload the menu data

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Menu Item")
        self.setGeometry(600, 300, 400, 250)

        self.layout = QVBoxLayout()

        # Input Fields
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(30)

        self.unit_price_label = QLabel("Unit Price:")
        self.unit_price_input = QLineEdit()
        self.unit_price_input.setFixedHeight(30)

        self.image_label = QLabel("Image Path:")
        self.image_input = QLineEdit()
        self.image_input.setFixedHeight(30)
        self.image_button = QPushButton("Browse...")
        self.image_button.setStyleSheet("""
                            background-color: darkblue; 
                            color: white; 
                            font-weight: bold;
                            border-radius: 10px;
                            padding: 10px;
                        """)
        self.image_button.clicked.connect(self.select_image)

        # Add Button
        self.add_button = QPushButton("Add Item")
        self.add_button.setStyleSheet("""
                            background-color: #4CAF50; 
                            color: white; 
                            font-weight: bold;
                            border-radius: 10px;
                            padding: 10px;
                        """)
        self.add_button.clicked.connect(self.add_item)

        # Layout
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.unit_price_label)
        self.layout.addWidget(self.unit_price_input)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.image_input)
        self.layout.addWidget(self.image_button)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg)")
        if file_path:
            self.image_input.setText(file_path)

    def add_item(self):
        name = self.name_input.text()
        unit_price = self.unit_price_input.text()
        image_path = self.image_input.text()

        if not name or not unit_price or not image_path:
            QMessageBox.warning(self, "Input Error", "All fields must be filled.")
            return

        try:
            unit_price = float(unit_price)
            self.parent().model.add_menu_item(name, unit_price, image_path)
            self.parent().load_data()  # Reload the menu data
            self.accept()  # Close the dialog
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid unit price.")

class UpdateItemDialog(QDialog):
    def __init__(self, parent, menu_id, current_item, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.menu_id = menu_id
        self.current_item = current_item
        self.setWindowTitle("Update Menu Item")
        self.setGeometry(600, 300, 400, 250)

        self.layout = QVBoxLayout()

        # Input Fields
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit(self.current_item['name'])
        self.name_input.setFixedHeight(30)

        self.unit_price_label = QLabel("Unit Price:")
        self.unit_price_input = QLineEdit(str(self.current_item['unit_price']))
        self.unit_price_input.setFixedHeight(30)

        self.image_label = QLabel("Image Path:")
        self.image_input = QLineEdit(self.get_absolute_path(self.current_item['image']))
        self.image_input.setFixedHeight(30)
        self.image_button = QPushButton("Browse...")
        self.image_button.setStyleSheet("""
                            QPushButton {
                                background-color: darkblue;  /* Green background */
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
        self.image_button.clicked.connect(self.select_image)

        # Update Button
        self.update_button = QPushButton("Update Item")
        self.update_button.setStyleSheet("""
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
        self.update_button.clicked.connect(self.update_item)

        # Layout
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.unit_price_label)
        self.layout.addWidget(self.unit_price_input)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.image_input)
        self.layout.addWidget(self.image_button)
        self.layout.addWidget(self.update_button)

        self.setLayout(self.layout)

    def get_absolute_path(self, image_path):
        """Convert relative image path to absolute path if needed."""
        if not os.path.isabs(image_path):  # If the path is not absolute
            image_path = os.path.abspath(os.path.join("images", image_path))  # Assuming images folder
        return image_path

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg)")
        if file_path:
            self.image_input.setText(file_path)

    def update_item(self):
        name = self.name_input.text()
        unit_price = self.unit_price_input.text()
        image_path = self.image_input.text()

        if not name or not unit_price or not image_path:
            QMessageBox.warning(self, "Input Error", "All fields must be filled.")
            return

        try:
            unit_price = float(unit_price)
            # Update the menu item in the database
            self.parent().model.update_menu_item(self.menu_id, name, unit_price, image_path)
            self.parent().load_data()  # Reload the menu data
            self.accept()  # Close the dialog
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid unit price.")
