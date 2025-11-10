import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QProgressBar, QGridLayout, QLineEdit,
                             QListWidget, QMessageBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from .upload_dialog import UploadDialog
from .points_history_dialog import PointsHistoryDialog
from .trophy_room_dialog import TrophyRoomDialog
from ..core.course_parser import get_course_structure, delete_course
from ..core.database import create_connection

# Placeholder for qtawesome
def icon(*args, **kwargs):
    return QIcon()

class Dashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.populate_course_list()
        self.refresh_stats()

    def init_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(20)

        # --- Create Widgets for each section ---
        user_profile_widget = self._create_user_profile_section()
        progress_overview_widget = self._create_progress_overview_section()
        gamification_panel_widget = self._create_gamification_panel()
        quick_stats_widget = self._create_quick_stats_section()
        course_management_widget = self._create_course_management_section()
        action_buttons_widget = self._create_action_buttons_section()

        # --- Add widgets to the layout ---
        layout.addWidget(user_profile_widget, 0, 0, 1, 2)
        layout.addWidget(progress_overview_widget, 1, 0)
        layout.addWidget(gamification_panel_widget, 1, 1)
        layout.addWidget(quick_stats_widget, 2, 0)
        layout.addWidget(course_management_widget, 2, 1)
        layout.addWidget(action_buttons_widget, 3, 0, 1, 2)

        # Set column stretch factors to make them resize proportionally
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)


    def _create_user_profile_section(self):
        """Creates the user profile section of the dashboard."""
        widget = QWidget()
        widget.setObjectName("userProfileSection")
        layout = QGridLayout(widget)

        # Username
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit("DefaultUser")

        # Stats Labels
        self.total_points_label = QLabel("Total Points: <b>...</b>")
        self.daily_streak_label = QLabel("Daily Streak: 🔥 <b>...</b>")
        self.longest_streak_label = QLabel("Longest Streak: <b>...</b>")
        self.topics_completed_label = QLabel("Topics Completed: <b>...</b>")
        self.time_spent_label = QLabel("Total Time: <b>...</b>")

        layout.addWidget(username_label, 0, 0)
        layout.addWidget(self.username_edit, 0, 1)
        layout.addWidget(self.total_points_label, 1, 0)
        layout.addWidget(self.daily_streak_label, 1, 1)
        layout.addWidget(self.longest_streak_label, 2, 0)
        layout.addWidget(self.topics_completed_label, 2, 1)
        layout.addWidget(self.time_spent_label, 3, 0, 1, 2)

        return widget


    def _create_progress_overview_section(self):
        """Creates the progress overview section."""
        widget = QWidget()
        widget.setObjectName("progressOverviewSection")
        layout = QVBoxLayout(widget)

        title = QLabel("<h2>Progress Overview</h2>")

        # Overall Progress
        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setValue(0)
        self.overall_progress_bar.setTextVisible(True)
        self.overall_progress_bar.setFormat("Overall: %p%")

        # Phase Breakdown
        self.phase_progress_layout = QVBoxLayout()

        self.next_topic_label = QLabel("Next Topic: <i>...</i>")

        layout.addWidget(title)
        layout.addWidget(self.overall_progress_bar)
        layout.addLayout(self.phase_progress_layout)
        layout.addWidget(self.next_topic_label)

        return widget

    def _create_gamification_panel(self):
        """Creates the gamification panel."""
        widget = QWidget()
        widget.setObjectName("gamificationPanel")
        layout = QVBoxLayout(widget)

        title = QLabel("<h2>Gamification</h2>")
        self.points_today_label = QLabel("Points Today: <b>0</b>")
        self.streak_status_label = QLabel("Daily Streak: <b>...</b>")

        view_history_button = QPushButton("View Points History")
        view_history_button.clicked.connect(self.open_points_history)

        layout.addWidget(title)
        layout.addWidget(self.points_today_label)
        layout.addWidget(self.streak_status_label)
        layout.addWidget(view_history_button)

        return widget

    def _create_quick_stats_section(self):
        """Creates the quick stats section."""
        widget = QWidget()
        widget.setObjectName("quickStatsSection")
        layout = QVBoxLayout(widget)

        title = QLabel("<h3>Quick Stats</h3>")
        self.topics_this_week_label = QLabel("Topics this week: <b>0</b>")
        self.avg_time_label = QLabel("Avg. learning time: <b>0 min</b>")
        self.consistency_label = QLabel("Consistency: <b>...</b>")

        layout.addWidget(title)
        layout.addWidget(self.topics_this_week_label)
        layout.addWidget(self.avg_time_label)
        layout.addWidget(self.consistency_label)

        return widget

    def _create_action_buttons_section(self):
        """Creates the main action buttons section."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        upload_button = QPushButton("Upload New Course")
        upload_button.setIcon(icon("fa.upload", color="white"))
        upload_button.clicked.connect(self.open_upload_dialog)

        continue_button = QPushButton("Continue Learning")
        continue_button.setIcon(icon("fa.play", color="white"))

        view_badges_button = QPushButton("View All Badges")
        view_badges_button.setIcon(icon("fa.trophy", color="white"))
        view_badges_button.clicked.connect(self.open_trophy_room)

        settings_button = QPushButton("Settings")
        settings_button.setIcon(icon("fa.cog", color="white"))

        layout.addWidget(upload_button)
        layout.addWidget(continue_button)
        layout.addWidget(view_badges_button)
        layout.addWidget(settings_button)

        return widget

    def _create_course_management_section(self):
        """Creates the course management section."""
        widget = QWidget()
        widget.setObjectName("courseManagementSection")
        layout = QVBoxLayout(widget)

        title = QLabel("<h3>Course Management</h3>")
        self.course_list_widget = QListWidget()

        delete_button = QPushButton("Delete Selected Course")
        delete_button.setIcon(icon("fa.trash", color="white"))
        delete_button.clicked.connect(self.delete_selected_course)

        layout.addWidget(title)
        layout.addWidget(self.course_list_widget)
        layout.addWidget(delete_button)

        return widget

    def populate_course_list(self):
        """Populates the list of uploaded courses."""
        self.course_list_widget.clear()
        courses = get_course_structure()
        if courses:
            for course in courses:
                self.course_list_widget.addItem(course['course_name'])

    def refresh_stats(self):
        """Refreshes all the user stats on the dashboard."""
        conn = create_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()

            # Assuming user_id = 1 for now
            cursor.execute("SELECT username, total_points, current_streak, longest_streak FROM users WHERE id = 1")
            user_data = cursor.fetchone()
            if user_data:
                self.username_edit.setText(user_data[0])
                self.total_points_label.setText(f"Total Points: <b>{user_data[1]}</b>")
                self.daily_streak_label.setText(f"Daily Streak: 🔥 <b>{user_data[2]} days</b>")
                self.longest_streak_label.setText(f"Longest Streak: <b>{user_data[3]} days</b>")

            cursor.execute("SELECT COUNT(*) FROM progress WHERE completed = 1 AND user_id = 1")
            topics_completed = cursor.fetchone()[0]
            self.topics_completed_label.setText(f"Topics Completed: <b>{topics_completed}</b>")

            cursor.execute("SELECT SUM(time_spent_seconds) FROM progress WHERE user_id = 1")
            total_seconds = cursor.fetchone()[0] or 0
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            self.time_spent_label.setText(f"Total Time: <b>{hours}h {minutes}m</b>")

        except Exception as e:
            print(f"Error refreshing stats: {e}")
        finally:
            conn.close()

    def delete_selected_course(self):
        """Deletes the selected course from the database."""
        selected_item = self.course_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Course Selected", "Please select a course to delete.")
            return

        course_name = selected_item.text()
        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete the course '{course_name}'?\n"
                                     "This action cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_course(course_name)
                self.populate_course_list()
                # You might want to signal the main window to refresh the sidebar as well
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete course: {e}")

    def open_upload_dialog(self):
        """Opens the course upload dialog."""
        dialog = UploadDialog(self)
        if dialog.exec():
            self.populate_course_list()
            # You might want to signal the main window to refresh the sidebar as well

    def open_points_history(self):
        """Opens the points history dialog."""
        dialog = PointsHistoryDialog(self)
        dialog.exec()

    def open_trophy_room(self):
        """Opens the trophy room dialog."""
        dialog = TrophyRoomDialog(self)
        dialog.exec()

if __name__ == '__main__':
    # This is for testing the Dashboard widget independently
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    # Load stylesheet
    stylesheet_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'styles.qss')
    try:
        with open(stylesheet_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Warning: stylesheet.qss not found.")

    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())
