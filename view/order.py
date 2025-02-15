from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QHBoxLayout, QHeaderView, QSizePolicy, QSpacerItem, QDoubleSpinBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
from functools import partial
from model.model import Model  # Importing the MenuModel

image_base_path = "/Users/kaoleangseng/PycharmProjects/RMS/controller/images"

class OrderView(QWidget):
    def __init__(self):
        super().__init__()
        self.menu_model = Model()
        self.order_data = {}
        self.setup_ui()
        self.load_menu_data()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Left Layout (Menu Table)
        self.left_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.setup_menu_table()
        self.left_layout.addWidget(self.table)
        main_layout.addLayout(self.left_layout, 6)

        # Right Layout (Order Summary)
        self.right_layout = QVBoxLayout()
        self.order_summary_table = QTableWidget()
        self.setup_order_summary_table()
        self.right_layout.addWidget(QLabel("Order Summary"))
        self.right_layout.addWidget(self.order_summary_table)

        # Summary Labels
        self.subtotal_label = QLabel("Subtotal: $0.00")
        self.right_layout.addWidget(self.subtotal_label)

        self.tax_input = QDoubleSpinBox()
        self.tax_input.setPrefix("Tax (%): ")
        self.tax_input.setValue(10.0)
        self.tax_input.valueChanged.connect(self.update_totals)
        self.right_layout.addWidget(self.tax_input)

        self.discount_input = QDoubleSpinBox()
        self.discount_input.setPrefix("Discount (%): ")
        self.discount_input.setValue(0.0)
        self.discount_input.valueChanged.connect(self.update_totals)
        self.right_layout.addWidget(self.discount_input)

        self.grand_total_label = QLabel("Grand Total: $0.00")
        self.right_layout.addWidget(self.grand_total_label)

        # Spacer
        self.right_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addLayout(self.right_layout, 4)

    def setup_menu_table(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Unit Price", "Image", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(120)

    def setup_order_summary_table(self):
        self.order_summary_table.setColumnCount(4)
        self.order_summary_table.setHorizontalHeaderLabels(["Name", "Quantity", "Unit Price", "Total"])
        self.order_summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_summary_table.verticalHeader().setDefaultSectionSize(50)

    def load_menu_data(self):
        menu_items = self.menu_model.get_menu_items()  # Get the latest data from the SQLite database
        self.table.setRowCount(len(menu_items))

        for row_idx, (id_, name, unit_price, image_name) in enumerate(menu_items):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(id_)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"${unit_price:.2f}"))

            for col in range(3):
                item = self.table.item(row_idx, col)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            image_label = QLabel()
            image_path = os.path.join(image_base_path, image_name)
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path).scaledToHeight(100, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                image_label.setText("No Image")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setCellWidget(row_idx, 3, image_label)

            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)

            # Add and Remove buttons
            add_btn = QPushButton("Add")
            add_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            add_btn.clicked.connect(partial(self.add_to_order, id_, name, unit_price))
            remove_btn.clicked.connect(partial(self.remove_from_order, id_))

            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(remove_btn)
            self.table.setCellWidget(row_idx, 4, btn_container)

    def add_to_order(self, menu_id, name, price):
        if menu_id in self.order_data:
            self.order_data[menu_id]["quantity"] += 1
        else:
            self.order_data[menu_id] = {"name": name, "quantity": 1, "unit_price": price}
        self.update_order_summary()

    def remove_from_order(self, menu_id):
        if menu_id in self.order_data:
            if self.order_data[menu_id]["quantity"] > 1:
                self.order_data[menu_id]["quantity"] -= 1
            else:
                del self.order_data[menu_id]
        self.update_order_summary()

    def update_order_summary(self):
        self.order_summary_table.setRowCount(len(self.order_data))
        subtotal = sum(data["quantity"] * data["unit_price"] for data in self.order_data.values())

        for row_idx, (menu_id, data) in enumerate(self.order_data.items()):
            total_price = data["quantity"] * data["unit_price"]
            self.order_summary_table.setItem(row_idx, 0, QTableWidgetItem(data["name"]))
            self.order_summary_table.setItem(row_idx, 1, QTableWidgetItem(str(data["quantity"])))
            self.order_summary_table.setItem(row_idx, 2, QTableWidgetItem(f"${data['unit_price']:.2f}"))
            self.order_summary_table.setItem(row_idx, 3, QTableWidgetItem(f"${total_price:.2f}"))

        self.subtotal_label.setText(f"Subtotal: ${subtotal:.2f}")
        self.update_totals()

    def update_totals(self):
        subtotal = sum(data["quantity"] * data["unit_price"] for data in self.order_data.values())
        tax = (self.tax_input.value() / 100) * subtotal
        discount = (self.discount_input.value() / 100) * subtotal
        grand_total = subtotal + tax - discount
        self.grand_total_label.setText(f"Grand Total: ${grand_total:.2f}")

    # Error when call it
    def refresh_menu_data(self):
        try:
            print("Ordering init...")
            # self.refresh_ui()
            # self.table.setRowCount(0)  # Clear current table contents
            self.load_menu_data()  # Reload menu data again
            # self.update_order_summary()  # Optionally update the order summary

        except Exception as e:
            print(f"Failed to refresh menu data: {e}")
