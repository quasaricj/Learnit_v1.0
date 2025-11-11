import sys
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QFileDialog, QLabel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.course_parser import parse_course_structure

class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upload Course")
        self.layout = QVBoxLayout()

        self.label = QLabel("Select the root folder of your course.")
        self.upload_button = QPushButton("Browse")
        self.upload_button.clicked.connect(self.open_file_dialog)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.upload_button)

        self.setLayout(self.layout)

    def open_file_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Course Folder")
        if folder_path:
            parse_course_structure(folder_path)
            self.accept()
