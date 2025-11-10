import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QCheckBox, QPushButton,
                             QMessageBox, QGroupBox)

class MasteryChecklistDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mastery Checklist")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Learning Objectives
        objectives_group = QGroupBox("Learning Objectives")
        objectives_layout = QVBoxLayout()
        self.obj1 = QCheckBox("Understood main concept")
        self.obj2 = QCheckBox("Can explain in own words")
        objectives_layout.addWidget(self.obj1)
        objectives_layout.addWidget(self.obj2)
        objectives_group.setLayout(objectives_layout)

        # Key Concepts
        concepts_group = QGroupBox("Key Concepts")
        concepts_layout = QVBoxLayout()
        self.concept1 = QCheckBox("Reviewed important terms")
        self.concept2 = QCheckBox("Understand how it applies to real-world")
        concepts_layout.addWidget(self.concept1)
        concepts_layout.addWidget(self.concept2)
        concepts_group.setLayout(concepts_layout)

        # Buttons
        self.complete_button = QPushButton("Mark Complete")
        self.complete_button.setEnabled(False)
        self.complete_button.clicked.connect(self.accept)

        layout.addWidget(objectives_group)
        layout.addWidget(concepts_group)
        layout.addWidget(self.complete_button)

        # Connect checkboxes to enable/disable button
        for checkbox in self.findChildren(QCheckBox):
            checkbox.stateChanged.connect(self.check_all_checked)

    def check_all_checked(self):
        """Checks if all checkboxes are checked."""
        all_checked = all(checkbox.isChecked() for checkbox in self.findChildren(QCheckBox))
        self.complete_button.setEnabled(all_checked)

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = MasteryChecklistDialog()
    dialog.show()
    sys.exit(app.exec())
