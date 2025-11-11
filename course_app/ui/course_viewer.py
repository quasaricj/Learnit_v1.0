import os
import sys
from PyQt6.QtWidgets import QWidget, QTextBrowser, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.timer_manager import TimerManager

class CourseViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer_manager = TimerManager(self.update_timer_label)

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Timer UI ---
        timer_layout = QHBoxLayout()
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.reset_button = QPushButton("Reset")

        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.pause_timer)
        self.reset_button.clicked.connect(self.reset_timer)

        timer_layout.addWidget(self.timer_label)
        timer_layout.addWidget(self.start_button)
        timer_layout.addWidget(self.pause_button)
        timer_layout.addWidget(self.reset_button)

        layout.addLayout(timer_layout)

        # --- Content Area ---
        self.content_area = QTextBrowser()
        self.content_area.setOpenExternalLinks(True)
        layout.addWidget(self.content_area)

        self.setLayout(layout)

    def load_topic(self, file_path):
        """Loads and displays the content of a markdown file."""
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                    self.content_area.setMarkdown(markdown_content)
            except Exception as e:
                self.content_area.setText(f"Error loading file: {e}")

    def start_timer(self):
        self.timer_manager.start_timer()

    def pause_timer(self):
        self.timer_manager.pause_timer()

    def reset_timer(self):
        self.timer_manager.reset_timer()
        self.update_timer_label()

    def update_timer_label(self):
        self.timer_manager.time_elapsed += 1
        mins = self.timer_manager.time_elapsed // 60
        secs = self.timer_manager.time_elapsed % 60
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")
