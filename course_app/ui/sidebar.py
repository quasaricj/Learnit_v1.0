from PyQt6.QtWidgets import QTreeView
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import Qt
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.course_parser import get_course_structure
from core.database import create_connection
from core.user_management import get_current_user

class Sidebar(QTreeView):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.user = get_current_user()
        self.populate()

    def populate(self):
        """Fills the sidebar with the course structure and completion status."""
        self.model.clear()
        course_data = get_course_structure()
        completed_topics = self.get_completed_topics()

        root_item = self.model.invisibleRootItem()

        # Add a "Dashboard" item to the sidebar
        dashboard_item = QStandardItem("Dashboard")
        dashboard_item.setData({"type": "dashboard"}, Qt.ItemDataRole.UserRole)
        root_item.appendRow(dashboard_item)

        # Add a "Rewards" item to the sidebar
        rewards_item = QStandardItem("Rewards")
        rewards_item.setData({"type": "rewards"}, Qt.ItemDataRole.UserRole)
        root_item.appendRow(rewards_item)

        if not course_data:
            return

        for course in course_data:
            course_item = QStandardItem(course['course_name'])
            course_item.setEditable(False)
            root_item.appendRow(course_item)

            phases = {}
            for topic in course['topics']:
                topic_id, phase_name, module_name, topic_name, file_path = topic

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
                topic_item.setData({"type": "topic", "file_path": file_path, "topic_id": topic_id}, Qt.ItemDataRole.UserRole)
                topic_item.setEditable(False)

                if topic_id in completed_topics:
                    # In a real application, you would use an icon
                    topic_item.setText(f"✓ {topic_name}")

                phases[phase_name]["modules"][module_name].appendRow(topic_item)

    def get_completed_topics(self):
        """Returns a set of completed topic IDs for the current user."""
        conn = create_connection()
        if conn and self.user:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT topic_id FROM progress WHERE user_id = ? AND completed = 1", (self.user[0],))
                return {row[0] for row in cursor.fetchall()}
            except Exception as e:
                print(f"Error getting completed topics: {e}")
                return set()
            finally:
                conn.close()
        return set()
