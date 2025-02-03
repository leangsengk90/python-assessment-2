from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QToolBar, QStackedWidget


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
            "Order": QLabel("Order Page"),
            "Menu": QLabel("Menu Page"),
            "Table": QLabel("Table Page"),
            "Reservation": QLabel("Reservation Page"),
            "Bill": QLabel("Bill Page"),
            "Report": QLabel("Report Page"),
        }

        for key, widget in self.pages.items():
            self.stacked_widget.addWidget(widget)

        icons = {
            "Order": "../images/order.png",
            "Menu": "../images/menu.png",
            "Table": "../images/table.png",
            "Reservation": "../images/reservation.png",
            "Bill": "../images/bill.png",
            "Report": "../images/report.png",
        }

        for name, icon_path in icons.items():
            action = QAction(QIcon(icon_path), name, self)
            action.setToolTip(name)
            action.triggered.connect(lambda checked, n=name: self.show_page(n))
            self.toolbar.addAction(action)

        self.show_page("Order")

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def show_page(self, page_name):
        widget = self.pages.get(page_name)
        if widget:
            self.stacked_widget.setCurrentWidget(widget)