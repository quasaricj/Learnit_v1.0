import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTreeView, QTextBrowser, QSplitter)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.course_parser import get_course_structure

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

        # Create a splitter to allow resizing of sidebar and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # --- Sidebar ---
        self.sidebar = QTreeView()
        self.sidebar.setHeaderHidden(True)
        self.sidebar_model = QStandardItemModel()
        self.sidebar.setModel(self.sidebar_model)
        splitter.addWidget(self.sidebar)

        # --- Main Content Area ---
        self.content_area = QTextBrowser()
        self.content_area.setOpenExternalLinks(True)
        splitter.addWidget(self.content_area)

        # Set initial sizes for the splitter
        splitter.setSizes([300, 900])

        # Populate the sidebar with course data
        self.populate_sidebar()

        # Connect sidebar clicks to content updates
        self.sidebar.clicked.connect(self.on_topic_selected)

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
        course_data = get_course_structure()
        if not course_data:
            return

        root_item = self.sidebar_model.invisibleRootItem()

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
        file_path = item.data(Qt.ItemDataRole.UserRole)

        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                    self.content_area.setMarkdown(markdown_content)
            except Exception as e:
                self.content_area.setText(f"Error loading file: {e}")
        elif not file_path:
            self.content_area.setText("<h1>Select a topic to begin learning.</h1>")


if __name__ == '__main__':
    # Get the path to the course_app directory
    course_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_course_path = os.path.join(course_app_dir, "sample_course")

    # Ensure a sample course exists for testing
    if not os.path.exists(sample_course_path):
        os.makedirs(os.path.join(sample_course_path, "Phase 1/Module 1"))
        with open(os.path.join(sample_course_path, "Phase 1/Module 1/Topic 1.md"), "w") as f:
            f.write("# Welcome to Learnit!")

    from core.course_parser import parse_course_structure
    parse_course_structure(sample_course_path)

    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
