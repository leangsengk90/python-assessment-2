from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QToolBar, QStackedWidget

from view.menu import MenuView
from view.order import OrderView
from view.tables import TableView


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.resize(1200, 800)
        self.center_window()

        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.pages = {
            "Order": OrderView(),
            "Menu": MenuView(),
            "Table": TableView(),
            "Reservation": QLabel("Reservation Page"),
            "Bill": QLabel("Bill Page"),
            "Report": QLabel("Report Page"),
        }

        for key, widget in self.pages.items():
            self.stacked_widget.addWidget(widget)

        icons = {
            "Order": "../icons/order.png",
            "Menu": "../icons/menu.png",
            "Table": "../icons/table.png",
            "Reservation": "../icons/reservation.png",
            "Bill": "../icons/bill.png",
            "Report": "../icons/report.png",
        }

        for name, icon_path in icons.items():
            action = QAction(QIcon(icon_path), name, self)
            action.setToolTip(name)
            action.triggered.connect(lambda checked, n=name: self.show_page(n))
            self.toolbar.addAction(action)

        self.show_page("Order")  # Show "Order" page by default

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def show_page(self, page_name):
        widget = self.pages.get(page_name)
        if widget:
            self.stacked_widget.setCurrentWidget(widget)

            # Error when call it
            # Check if the "Order" page is selected and refresh data
            # if page_name == "Order":
            #     order_view = self.pages.get("Order")
            #     if order_view:
            #         order_view.refresh_menu_data()  # Reload data from the database
