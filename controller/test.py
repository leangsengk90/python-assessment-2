import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QToolBar, QMessageBox, QFileDialog
from PyQt6.QtGui import QAction,QIcon


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu")
        self.setGeometry(100, 100, 600,400)

        # Create text edit
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        # Create toolbar
        self.create_toolbar()

    def create_toolbar(self):
        toolbar = QToolBar("Menu Toolbar")
        self.addToolBar(toolbar)

        # Create action
        new_action = QAction(QIcon("/Users/kaoleangseng/PycharmProjects/RMS/images/new.png"), "New", self)
        new_action.setStatusTip("Create new document")
        new_action.triggered.connect(self.new_file)

        cut_action = QAction(QIcon("/Users/kaoleangseng/PycharmProjects/RMS/images/cut.png"), "Cut", self)
        cut_action.setStatusTip("Cut the selected text")
        cut_action.triggered.connect(self.cut_action)

        copy_action = QAction(QIcon("/Users/kaoleangseng/PycharmProjects/RMS/images/copy.png"), "Copy", self)
        copy_action.setStatusTip("Copy the selected text")
        copy_action.triggered.connect(self.copy_action)

        paste_action = QAction(QIcon("/Users/kaoleangseng/PycharmProjects/RMS/images/paste.png"), "Paste", self)
        paste_action.setStatusTip("Paste text")
        paste_action.triggered.connect(self.paste_action)

        open_file = QAction(QIcon("/Users/kaoleangseng/PycharmProjects/RMS/images/open.png"), "Paste", self)
        open_file.setStatusTip("Paste text")
        open_file.triggered.connect(self.open_file)

        # Add action to toolbar
        toolbar.addAction(new_action)
        toolbar.addAction(cut_action)
        toolbar.addAction(copy_action)
        toolbar.addAction(paste_action)
        toolbar.addAction(open_file)


    def new_file(self):
        response = QMessageBox.question(self, "Confirm new file", "Do you want to create new file?", QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
        if response == QMessageBox.StandardButton.Yes:
            self.text_edit.clear()

    def cut_action(self):
        pass

    def copy_action(self):
        pass

    def paste_action(self):
        pass

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open file","", "All files (*);;Text files (*.txt)")
        if file_name:
            try:
                with open(file_name, "r") as file:
                    self.text_edit.setText(file.read())
            except Exception as err:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(err)}")


if __name__ == '__main__':
    app =  QApplication(sys.argv)
    window = TextEditor()
    window.show()
    sys.exit(app.exec())