import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTreeView, QSplitter, QStackedWidget, QPushButton)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.course_parser import get_course_structure, parse_course_structure
from ui.dashboard import Dashboard
from ui.course_viewer import CourseViewer
from ui.upload_dialog import UploadDialog


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
        self.sidebar = QTreeView()
        self.sidebar.setHeaderHidden(True)
        self.sidebar_model = QStandardItemModel()
        self.sidebar.setModel(self.sidebar_model)
        left_layout.addWidget(self.sidebar)

        # --- Upload Button ---
        self.upload_button = QPushButton("Upload Course")
        self.upload_button.clicked.connect(self.open_upload_dialog)
        left_layout.addWidget(self.upload_button)

        # Create a splitter to allow resizing of sidebar and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        main_layout.addWidget(splitter)

        # --- Main Content Area ---
        self.stacked_widget = QStackedWidget()
        self.dashboard = Dashboard()
        self.course_viewer = CourseViewer()
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.addWidget(self.course_viewer)
        splitter.addWidget(self.stacked_widget)

        # Set initial sizes for the splitter
        splitter.setSizes([300, 900])

        # Populate the sidebar with course data
        self.populate_sidebar()

        # Connect sidebar clicks to content updates
        self.sidebar.clicked.connect(self.on_topic_selected)

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

    def populate_sidebar(self):
        """Fills the sidebar with the course structure from the database."""
        self.sidebar_model.clear()
        course_data = get_course_structure()

        root_item = self.sidebar_model.invisibleRootItem()

        # Add a "Dashboard" item to the sidebar
        dashboard_item = QStandardItem("Dashboard")
        dashboard_item.setData("dashboard", Qt.ItemDataRole.UserRole)
        root_item.appendRow(dashboard_item)

        if not course_data:
            return

        for course in course_data:
            course_item = QStandardItem(course['course_name'])
            course_item.setEditable(False)
            root_item.appendRow(course_item)

            phases = {}
            for topic in course['topics']:
                phase_name, module_name, topic_name, file_path = topic

                if phase_name not in phases:
                    phase_item = QStandardItem(phase_name)
                    phase_item.setEditable(False)
                    course_item.appendRow(phase_item)
                    phases[phase_name] = {"item": phase_item, "modules": {}}

                if module_name not in phases[phase_name]["modules"]:
                    module_item = QStandardItem(module_name)
                    module_item.setEditable(False)
                    phases[phase_name]["item"].appendRow(module_item)
                    phases[phase_name]["modules"][module_name] = module_item

                topic_item = QStandardItem(topic_name)
                topic_item.setData(file_path, Qt.ItemDataRole.UserRole)
                topic_item.setEditable(False)
                phases[phase_name]["modules"][module_name].appendRow(topic_item)

    def on_topic_selected(self, index):
        """Handles the selection of a topic in the sidebar."""
        item = self.sidebar_model.itemFromIndex(index)
        data = item.data(Qt.ItemDataRole.UserRole)

        if data == "dashboard":
            self.stacked_widget.setCurrentWidget(self.dashboard)
        elif data and os.path.exists(data):
            self.course_viewer.load_topic(data)
            self.stacked_widget.setCurrentWidget(self.course_viewer)
        else:
            # Fallback to dashboard if the content is not found or is not a file
            self.stacked_widget.setCurrentWidget(self.dashboard)

    def open_upload_dialog(self):
        """Opens the course upload dialog."""
        dialog = UploadDialog(self)
        if dialog.exec():
            # The dialog handles the folder selection and parsing
            self.populate_sidebar()


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
