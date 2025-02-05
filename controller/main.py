from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import sys
from view.login import LoginView
from view.main import MainView
from model.model import Model

# Controller: Handles user interaction and business logic
class Controller:
    def __init__(self):
        self.model = Model()
        self.model.add_user("admin", "123")  # Adding a default user immediately
        self.login_view = LoginView(self)
        self.main_view = None

    def handle_login(self):
        username = self.login_view.input_user.text()
        password = self.login_view.input_pass.text()

        if self.model.check_user(username, password):
            # QMessageBox.information(self.login_view, "Login Successful", "Welcome!")
            self.main_view = MainView()
            self.main_view.show()
            self.login_view.close()
        else:
            QMessageBox.warning(self.login_view, "Login Failed", "Invalid username or password")


# Main application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    controller.login_view.show()
    sys.exit(app.exec())
