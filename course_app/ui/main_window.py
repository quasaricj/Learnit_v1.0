import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QSplitter, QStackedWidget, QPushButton)
from PyQt6.QtCore import Qt

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.course_parser import parse_course_structure
from ui.dashboard import Dashboard
from ui.course_viewer import CourseViewer
from ui.upload_dialog import UploadDialog
from ui.sidebar import Sidebar
from ui.rewards_panel import RewardsPanel
from ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Learnit - Your Offline Learning Companion")
        self.setGeometry(100, 100, 1200, 800)

        # Load stylesheet
        self.load_stylesheet()

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- Left Panel ---
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # --- Sidebar ---
        self.sidebar = Sidebar()
        left_layout.addWidget(self.sidebar)

        # --- Bottom Buttons ---
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload Course")
        self.upload_button.clicked.connect(self.open_upload_dialog)
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.settings_button)
        left_layout.addLayout(button_layout)

        # Create a splitter to allow resizing of sidebar and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        main_layout.addWidget(splitter)

        # --- Main Content Area ---
        self.stacked_widget = QStackedWidget()
        self.dashboard = Dashboard()
        self.course_viewer = CourseViewer()
        self.rewards_panel = RewardsPanel()
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.addWidget(self.course_viewer)
        self.stacked_widget.addWidget(self.rewards_panel)
        splitter.addWidget(self.stacked_widget)

        # Set initial sizes for the splitter
        splitter.setSizes([300, 900])

        # Connect sidebar clicks to content updates
        self.sidebar.clicked.connect(self.on_topic_selected)

        # Connect the topic completed signal
        self.course_viewer.topic_completed.connect(self.on_topic_completed)

        # Connect the topic changed signal
        self.course_viewer.topic_changed.connect(self.on_topic_changed)

        # Set the dashboard as the initial view
        self.stacked_widget.setCurrentWidget(self.dashboard)

    def load_stylesheet(self):
        """Loads the application's stylesheet."""
        stylesheet_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'styles.qss')
        try:
            with open(stylesheet_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Warning: stylesheet.qss not found.")

    def on_topic_selected(self, index):
        """Handles the selection of a topic in the sidebar."""
        item = self.sidebar.model.itemFromIndex(index)
        if not item:
            return

        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        if data["type"] == "dashboard":
            self.stacked_widget.setCurrentWidget(self.dashboard)
        elif data["type"] == "rewards":
            self.stacked_widget.setCurrentWidget(self.rewards_panel)
        elif data["type"] == "topic" and os.path.exists(data["file_path"]):
            self.course_viewer.load_topic(data["file_path"], data["topic_id"])
            self.stacked_widget.setCurrentWidget(self.course_viewer)

    def open_upload_dialog(self):
        """Opens the course upload dialog."""
        dialog = UploadDialog(self)
        if dialog.exec():
            # The dialog handles the folder selection and parsing
            self.sidebar.populate()

    def open_settings_dialog(self):
        """Opens the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            timer_value = dialog.get_timer_value()
            # In a real application, you would save this value
            print(f"New timer value: {timer_value}")

    def on_topic_completed(self):
        """Handles the topic completed signal."""
        self.dashboard.update_stats()
        self.rewards_panel.update_rewards()
        self.sidebar.populate()

    def on_topic_changed(self, topic_id):
        """Handles the topic changed signal."""
        self.select_topic_in_sidebar(topic_id)

    def select_topic_in_sidebar(self, topic_id):
        """Finds and selects a topic in the sidebar by its ID."""
        for row in range(self.sidebar.model.rowCount()):
            course_item = self.sidebar.model.item(row)
            if course_item:
                for phase_row in range(course_item.rowCount()):
                    phase_item = course_item.child(phase_row)
                    if phase_item:
                        for module_row in range(phase_item.rowCount()):
                            module_item = phase_item.child(module_row)
                            if module_item:
                                for topic_row in range(module_item.rowCount()):
                                    topic_item = module_item.child(topic_row)
                                    if topic_item:
                                        data = topic_item.data(Qt.ItemDataRole.UserRole)
                                        if data["type"] == "topic" and data["topic_id"] == topic_id:
                                            self.sidebar.setCurrentIndex(topic_item.index())
                                            self.on_topic_selected(topic_item.index())
                                            return


if __name__ == '__main__':
    # Get the path to the course_app directory
    course_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_course_path = os.path.join(course_app_dir, "sample_course")

    # Ensure a sample course exists for testing
    if not os.path.exists(sample_course_path):
        os.makedirs(os.path.join(sample_course_path, "Phase 1/Module 1"))
        with open(os.path.join(sample_course_path, "Phase 1/Module 1/Topic 1.md"), "w") as f:
            f.write("# Welcome to Learnit!")

    parse_course_structure(sample_course_path)

    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
