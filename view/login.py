from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QHBoxLayout


# View: Defines UI components
class LoginView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("RMS Login")
        self.setGeometry(600, 300, 500, 300)
        self.setFixedSize(800, 600)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 20, 0)  # Remove margins

        # Left side - Image
        self.image_label = QLabel()
        self.image_label.setPixmap(
            QPixmap("../icons/login.png"))
        self.image_label.setFixedSize(360, 600)
        self.image_label.setScaledContents(True)

        # Right side - Login form
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center form elements

        self.label_user = QLabel("Username")
        self.input_user = QLineEdit()
        self.input_user.setFixedHeight(30)

        self.label_pass = QLabel("Password")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setFixedHeight(30)

        self.btn_login = QPushButton("Login")
        self.btn_login.setFixedHeight(40)
        self.btn_login.clicked.connect(self.controller.handle_login)

        form_layout.addStretch()
        form_layout.addWidget(self.label_user)
        form_layout.addWidget(self.input_user)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.label_pass)
        form_layout.addWidget(self.input_pass)
        form_layout.addWidget(self.btn_login)
        form_layout.addStretch()

        main_layout.addWidget(self.image_label)
        main_layout.addLayout(form_layout)

        self.setLayout(main_layout)
        self.center_window()

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)