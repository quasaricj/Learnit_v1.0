import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTreeView, QTextBrowser, QSplitter,
                             QLineEdit, QMenu, QPushButton)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QSortFilterProxyModel

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.course_parser import get_course_structure
from ..core.database import create_connection

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
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search topics...")
        self.search_bar.textChanged.connect(self.filter_sidebar)
        sidebar_layout.addWidget(self.search_bar)

        self.sidebar = QTreeView()
        self.sidebar.setHeaderHidden(True)
        self.sidebar_model = QStandardItemModel()

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.sidebar_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setRecursiveFilteringEnabled(True)

        self.sidebar.setModel(self.proxy_model)
        self.sidebar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sidebar.customContextMenuRequested.connect(self.show_sidebar_context_menu)

        sidebar_layout.addWidget(self.sidebar)
        splitter.addWidget(sidebar_widget)

        # --- Main Content Area ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.content_area = QTextBrowser()
        self.content_area.setOpenExternalLinks(True)
        content_layout.addWidget(self.content_area)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("<< Previous")
        self.prev_button.clicked.connect(self.go_to_previous_topic)
        self.next_button = QPushButton("Next >>")
        self.next_button.clicked.connect(self.go_to_next_topic)
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        content_layout.addLayout(nav_layout)

        splitter.addWidget(content_widget)

        # Set initial sizes for the splitter
        splitter.setSizes([300, 900])

        # Populate the sidebar with course data
        self.populate_sidebar()

        # Connect sidebar clicks to content updates
        self.sidebar.clicked.connect(self.on_topic_selected_proxy)

        self.current_topic_index = None

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

        self.sidebar_model.clear()
        root_item = self.sidebar_model.invisibleRootItem()

        for course in course_data:
            course_item = QStandardItem(course['course_name'])
            course_item.setEditable(False)
            root_item.appendRow(course_item)

            # Group topics by phase and module to calculate progress
            phases = {}
            for topic_data in course['topics']:
                topic_id, phase_name, module_name, topic_name, file_path, completed = topic_data
                if phase_name not in phases:
                    phases[phase_name] = {}
                if module_name not in phases[phase_name]:
                    phases[phase_name][module_name] = []
                phases[phase_name][module_name].append((topic_name, file_path, completed, topic_id))

            # Populate the tree, calculating progress as we go
            for phase_name, modules in phases.items():
                phase_topics_total = sum(len(topics) for topics in modules.values())
                phase_topics_completed = sum(1 for topics in modules.values() for t in topics if t[2])
                phase_progress = int((phase_topics_completed / phase_topics_total) * 100) if phase_topics_total > 0 else 0

                phase_item = QStandardItem(f"{phase_name} ({phase_progress}%)")
                phase_item.setEditable(False)
                course_item.appendRow(phase_item)

                for module_name, topics in modules.items():
                    module_topics_total = len(topics)
                    module_topics_completed = sum(1 for t in topics if t[2])
                    module_progress = int((module_topics_completed / module_topics_total) * 100) if module_topics_total > 0 else 0

                    module_item = QStandardItem(f"{module_name} ({module_progress}%)")
                    module_item.setEditable(False)
                    phase_item.appendRow(module_item)

                    for topic_name, file_path, completed, topic_id in topics:
                        display_text = f"✓ {topic_name}" if completed else topic_name
                        topic_item = QStandardItem(display_text)
                        topic_item.setData(file_path, Qt.ItemDataRole.UserRole)
                        topic_item.setData(topic_id, Qt.ItemDataRole.UserRole + 1) # Store topic_id
                        topic_item.setEditable(False)
                        if completed:
                            topic_item.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton')))
                        module_item.appendRow(topic_item)

        self.sidebar.expandAll()

    def on_topic_selected_proxy(self, proxy_index):
        """Handles topic selection when using a proxy model."""
        source_index = self.proxy_model.mapToSource(proxy_index)
        self.on_topic_selected(source_index)

    def on_topic_selected(self, index):
        """Handles the selection of a topic in the sidebar."""
        item = self.sidebar_model.itemFromIndex(index)
        if not item:
            return

        self.current_topic_index = index
        file_path = item.data(Qt.ItemDataRole.UserRole)

        if file_path and os.path.exists(file_path):
            try:
                import markdown
                with open(file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()

                    # Generate CSS for syntax highlighting (can be cached)
                    from pygments.formatters import HtmlFormatter
                    css = HtmlFormatter().get_style_defs('.codehilite')

                    # Convert markdown to HTML with syntax highlighting
                    html = markdown.markdown(markdown_content, extensions=['fenced_code', 'codehilite'])

                    # Combine CSS and HTML
                    full_html = f"<style>{css}</style>{html}"

                    self.content_area.setHtml(full_html)
            except Exception as e:
                self.content_area.setText(f"Error loading file: {e}")
        elif not file_path:
            # If a non-topic item is clicked, do nothing or show dashboard
            pass

    def go_to_previous_topic(self):
        """Navigates to the previous topic in the sidebar."""
        if self.current_topic_index is None:
            return

        prev_index = self.sidebar.indexAbove(self.current_topic_index)
        if prev_index.isValid():
            self.sidebar.setCurrentIndex(prev_index)
            self.on_topic_selected_proxy(prev_index)

    def go_to_next_topic(self):
        """Navigates to the next topic in the sidebar."""
        if self.current_topic_index is None:
            return

        next_index = self.sidebar.indexBelow(self.current_topic_index)
        if next_index.isValid():
            self.sidebar.setCurrentIndex(next_index)
            self.on_topic_selected_proxy(next_index)

    def show_sidebar_context_menu(self, position):
        """Shows a context menu for sidebar items."""
        index = self.sidebar.indexAt(position)
        if not index.isValid():
            return

        source_index = self.proxy_model.mapToSource(index)
        item = self.sidebar_model.itemFromIndex(source_index)
        topic_id = item.data(Qt.ItemDataRole.UserRole + 1)

        # Only show the menu for actual topics (which have a topic_id)
        if not topic_id:
            return

        menu = QMenu()
        toggle_action = menu.addAction("Mark as Complete/Incomplete")
        favorite_action = menu.addAction("Mark as Favorite")
        details_action = menu.addAction("View Details")

        action = menu.exec(self.sidebar.viewport().mapToGlobal(position))

        if action == toggle_action:
            self.toggle_topic_completion(topic_id)
        elif action == favorite_action:
            self.mark_as_favorite(topic_id)
        elif action == details_action:
            self.view_topic_details(topic_id)

    def toggle_topic_completion(self, topic_id):
        """Toggles the completion status of a topic."""
        conn = create_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            # Assuming user_id = 1
            cursor.execute("SELECT completed FROM progress WHERE topic_id = ? AND user_id = 1", (topic_id,))
            result = cursor.fetchone()

            if result:
                new_status = not result[0]
                cursor.execute("UPDATE progress SET completed = ? WHERE topic_id = ? AND user_id = 1", (new_status, topic_id))
            else:
                new_status = True
                cursor.execute("INSERT INTO progress (user_id, topic_id, completed) VALUES (1, ?, ?)", (topic_id, new_status))

            conn.commit()
            print(f"Set topic {topic_id} completion to {new_status}")
        except Exception as e:
            print(f"Error toggling completion status: {e}")
        finally:
            conn.close()

        # After updating the DB, refresh the sidebar
        self.populate_sidebar()

    def mark_as_favorite(self, topic_id):
        """Marks a topic as a favorite."""
        # Placeholder for favorite functionality
        print(f"Marking topic ID as favorite: {topic_id}")

    def view_topic_details(self, topic_id):
        """Shows a dialog with details about the topic."""
        # Placeholder for details view
        print(f"Viewing details for topic ID: {topic_id}")

    def filter_sidebar(self, text):
        """Filters the sidebar tree view based on the search text."""
        self.proxy_model.setFilterFixedString(text)


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
