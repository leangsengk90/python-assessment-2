from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHBoxLayout, \
    QMessageBox
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

        for row_idx, (menu_id, name, unit_price, image_path) in enumerate(menu_items):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(menu_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"${unit_price:.2f}"))

            # Load Image with Smooth Scaling
            image_label = QLabel()
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

    def delete_item(self, menu_id):
        confirm = QMessageBox.question(self, "Delete Item", "Are you sure you want to delete this item?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.model.delete_menu_item(menu_id)
            self.load_data()

    def update_item(self, menu_id):
        QMessageBox.information(self, "Update Item", f"Update logic for Menu ID: {menu_id} will be implemented here.")
