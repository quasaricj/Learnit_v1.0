import sys
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QTreeWidget, QTreeWidgetItem, QLabel,
                             QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt

from ..core.course_parser import parse_course_structure

class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upload New Course")
        self.setGeometry(200, 200, 600, 400)
        self.setAcceptDrops(True)
        self.course_path = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Drop instruction label
        self.info_label = QLabel("Drag and drop a course folder here, or click 'Select Folder'")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setObjectName("dropLabel")
        layout.addWidget(self.info_label)

        # Folder selection button
        select_folder_button = QPushButton("Select Course Folder")
        select_folder_button.clicked.connect(self.select_folder)
        layout.addWidget(select_folder_button)

        # Course structure preview
        self.preview_tree = QTreeWidget()
        self.preview_tree.setHeaderLabels(["Course Structure"])
        layout.addWidget(self.preview_tree)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Action buttons
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload")
        self.upload_button.setEnabled(False)
        self.upload_button.clicked.connect(self.upload_course)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def select_folder(self):
        """Opens a dialog to select a course folder."""
        path = QFileDialog.getExistingDirectory(self, "Select Course Folder")
        if path:
            self.process_folder(path)

    def process_folder(self, path):
        """Validates and previews the structure of the selected folder."""
        self.course_path = path
        course_name = os.path.basename(path)
        self.info_label.setText(f"Course to upload: <b>{course_name}</b>")
        self.preview_tree.clear()

        # Simple validation: check for markdown files
        has_markdown = any(f.endswith('.md') for f in os.listdir(path))
        if not has_markdown:
             # Look in subdirectories
            has_markdown = any(
                f.endswith('.md')
                for _, _, files in os.walk(path)
                for f in files
            )

        if not has_markdown:
            QMessageBox.warning(self, "Invalid Course", "The selected folder does not contain any Markdown files.")
            self.upload_button.setEnabled(False)
            return

        # Preview structure (simplified)
        root_item = QTreeWidgetItem(self.preview_tree, [course_name])
        for root, dirs, files in os.walk(path):
            parent_item = root_item
            for d in dirs:
                QTreeWidgetItem(parent_item, [d])
            for f in files:
                if f.endswith('.md'):
                    QTreeWidgetItem(parent_item, [f])

        self.preview_tree.expandAll()
        self.upload_button.setEnabled(True)

    def upload_course(self):
        """Handles the course upload process."""
        if not self.course_path:
            return

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0) # Indeterminate progress

            # This is where the actual parsing and DB insertion happens
            parse_course_structure(self.course_path)

            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

            QMessageBox.information(self, "Success", "Course uploaded successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload course: {e}")
            self.progress_bar.setVisible(False)

    # --- Drag and Drop Handlers ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.process_folder(path)

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = UploadDialog()
    dialog.show()
    sys.exit(app.exec())
