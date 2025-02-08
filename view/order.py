from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QHeaderView, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import sqlite3
import os


class OrderView(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout
        main_layout = QHBoxLayout(self)

        # Left Layout (80%)
        self.left_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.setup_table()

        self.left_layout.addWidget(self.table)
        main_layout.addLayout(self.left_layout, 7)  # 80%

        # Right Layout (20%) - Placeholder
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(QLabel("Order Summary"))  # Placeholder for now
        main_layout.addLayout(self.right_layout, 3)  # 20%

        self.load_menu_data()

    def setup_table(self):
        self.table.setColumnCount(5)  # ID, Name, Unit Price, Image, Action
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Unit Price", "Image", "Action"])

        # Resize columns to fit left layout
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(100)  # Increase row height

        # Expanding size policy
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


    def load_menu_data(self):
        db_path = "/Users/kaoleangseng/PycharmProjects/RMS/controller/rms.db"
        image_base_path = "/Users/kaoleangseng/PycharmProjects/RMS/controller/images"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, unit_price, image FROM menu")
        menu_items = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(menu_items))

        for row_idx, (id_, name, unit_price, image_name) in enumerate(menu_items):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(id_)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"${unit_price:.2f}"))

            # Make cells in columns 0, 1, and 2 uneditable
            self.table.item(row_idx, 0).setFlags(self.table.item(row_idx, 0).flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.item(row_idx, 1).setFlags(self.table.item(row_idx, 1).flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.item(row_idx, 2).setFlags(self.table.item(row_idx, 2).flags() & ~Qt.ItemFlag.ItemIsEditable)

            # Set row height
            row_height = self.table.verticalHeader().defaultSectionSize()
            self.table.setRowHeight(row_idx, row_height)

            # Load Image (Perfect Fit)
            image_path = os.path.join(image_base_path, image_name)
            image_label = QLabel()
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path).scaledToHeight(row_height, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                image_label.setText("No Image")
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setCellWidget(row_idx, 3, image_label)

            # Add & Remove Buttons
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)

            add_btn = QPushButton("Add")
            remove_btn = QPushButton("Remove")
            add_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            remove_btn.setStyleSheet("background-color: #8B0000; color: white;")

            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(remove_btn)

            self.table.setCellWidget(row_idx, 4, btn_container)

    def refresh_menu_data(self):
        # Code to refresh the data from the database
        self.load_menu_data()  # Reload the menu data