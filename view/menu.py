import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHBoxLayout, \
    QMessageBox, QDialog, QLineEdit, QFileDialog
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
            image_path = os.path.join("images", image_filename)  # Get image path from 'images' folder
            pixmap = QPixmap(image_path)
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
            btn_update.setStyleSheet("background-color: green; color: white; font-weight: bold;")
            btn_delete.setStyleSheet("background-color: #8B0000; color: white; font-weight: bold;")

            btn_update.clicked.connect(lambda _, id=menu_id: self.update_item(id))
            btn_delete.clicked.connect(lambda _, id=menu_id: self.delete_item(id))

            action_layout.addWidget(btn_update)
            action_layout.addWidget(btn_delete)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)

            self.table.setCellWidget(row_idx, 4, action_widget)

    def open_add_item_dialog(self):
        self.dialog = AddItemDialog(self)
        self.dialog.show()

    def delete_item(self, menu_id):
        confirm = QMessageBox.question(self, "Delete Item", "Are you sure you want to delete this item?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.model.delete_menu_item(menu_id)
            self.load_data()

    def update_item(self, menu_id):
        QMessageBox.information(self, "Update Item", f"Update logic for Menu ID: {menu_id} will be implemented here.")


class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Menu Item")
        self.setGeometry(600, 300, 400, 250)

        self.layout = QVBoxLayout()

        # Input Fields
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()

        self.unit_price_label = QLabel("Unit Price:")
        self.unit_price_input = QLineEdit()

        self.image_label = QLabel("Image Path:")
        self.image_input = QLineEdit()
        self.image_button = QPushButton("Browse...")
        self.image_button.clicked.connect(self.select_image)

        # Add Button
        self.add_button = QPushButton("Add Item")
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
