from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

# View: Defines UI components
class LoginView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label_user = QLabel("Username:")
        self.input_user = QLineEdit()
        self.label_pass = QLabel("Password:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.controller.handle_login)

        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.input_pass)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)