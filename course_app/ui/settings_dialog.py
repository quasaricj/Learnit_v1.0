from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QSpinBox, QDialogButtonBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.layout = QVBoxLayout()

        # --- Timer Setting ---
        self.timer_label = QLabel("Default Topic Timer (minutes):")
        self.timer_spinbox = QSpinBox()
        self.timer_spinbox.setRange(1, 120)
        # In a real application, you would load the saved value
        self.timer_spinbox.setValue(25)

        self.layout.addWidget(self.timer_label)
        self.layout.addWidget(self.timer_spinbox)

        # --- Dialog Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def get_timer_value(self):
        return self.timer_spinbox.value()
