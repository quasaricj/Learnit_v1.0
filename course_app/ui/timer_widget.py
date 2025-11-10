from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, QTime

class TimerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.target_time = QTime(0, 30, 0) # Default 30 minutes
        self.elapsed_time = QTime(0, 0, 0)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.time_label = QLabel("30:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 48px; font-weight: bold;")
        layout.addWidget(self.time_label)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_timer)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.reset_button)
        layout.addLayout(button_layout)

    def start_timer(self):
        self.timer.start(1000) # Update every second
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)

    def pause_timer(self):
        self.timer.stop()
        self.start_button.setText("Resume")
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)

    def reset_timer(self):
        self.timer.stop()
        self.elapsed_time = QTime(0, 0, 0)
        self.update_display()
        self.start_button.setText("Start")
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)

    def update_time(self):
        self.elapsed_time = self.elapsed_time.addSecs(1)
        self.update_display()

    def update_display(self):
        elapsed_secs = QTime(0, 0, 0).secsTo(self.elapsed_time)
        target_secs = QTime(0, 0, 0).secsTo(self.target_time)
        remaining_secs = target_secs - elapsed_secs

        if remaining_secs <= 0:
            self.time_label.setText("00:00")
            self.timer.stop()
        else:
            time = QTime(0, 0, 0).addSecs(remaining_secs)
            self.time_label.setText(time.toString("mm:ss"))

    def get_elapsed_seconds(self):
        """Returns the total elapsed seconds."""
        return self.elapsed_time.hour() * 3600 + self.elapsed_time.minute() * 60 + self.elapsed_time.second()

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    timer_widget = TimerWidget()
    timer_widget.show()
    sys.exit(app.exec())
