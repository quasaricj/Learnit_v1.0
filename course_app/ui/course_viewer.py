import os
import sys
from PyQt6.QtWidgets import QWidget, QTextBrowser, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.timer_manager import TimerManager
from core.progress_tracker import mark_topic_complete
from core.user_management import get_current_user
from utils.markdown_renderer import render_markdown
from core.course_parser import get_topic_navigation
from core.database import create_connection

class CourseViewer(QWidget):
    topic_completed = pyqtSignal()
    topic_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.current_topic_id = None
        self.user = get_current_user()
        self.init_ui()
        self.timer_manager = TimerManager(self.update_timer_label)

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Top Bar ---
        top_bar_layout = QHBoxLayout()

        # Navigation buttons
        self.prev_button = QPushButton("Previous Topic")
        self.next_button = QPushButton("Next Topic")
        self.complete_button = QPushButton("Mark as Complete")

        top_bar_layout.addWidget(self.prev_button)
        top_bar_layout.addWidget(self.next_button)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.complete_button)

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

        # Add layouts to main layout
        layout.addLayout(top_bar_layout)
        layout.addLayout(timer_layout)

        # --- Content Area ---
        self.content_area = QTextBrowser()
        self.content_area.setOpenExternalLinks(True)
        layout.addWidget(self.content_area)

        self.setLayout(layout)

        # Connect signals
        self.complete_button.clicked.connect(self.mark_complete)
        self.prev_button.clicked.connect(self.load_prev_topic)
        self.next_button.clicked.connect(self.load_next_topic)

    def load_topic(self, file_path, topic_id):
        """Loads and displays the content of a markdown file."""
        self.current_topic_id = topic_id
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                    html_content = render_markdown(markdown_content)
                    self.content_area.setHtml(html_content)
            except Exception as e:
                self.content_area.setText(f"Error loading file: {e}")

        self.update_nav_buttons()

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

    def mark_complete(self):
        if self.current_topic_id and self.user:
            mark_topic_complete(self.user[0], self.current_topic_id)
            self.topic_completed.emit()

    def update_nav_buttons(self):
        prev_topic, next_topic = get_topic_navigation(self.current_topic_id)
        self.prev_button.setEnabled(prev_topic is not None)
        self.next_button.setEnabled(next_topic is not None)

    def load_prev_topic(self):
        prev_topic_id, _ = get_topic_navigation(self.current_topic_id)
        if prev_topic_id:
            self.topic_changed.emit(prev_topic_id)

    def load_next_topic(self):
        _, next_topic_id = get_topic_navigation(self.current_topic_id)
        if next_topic_id:
            self.topic_changed.emit(next_topic_id)
