import sys
import os
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.user_management import get_current_user
from core.database import create_connection

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.user = get_current_user()
        self.init_ui()
        self.update_stats()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Welcome Message ---
        self.welcome_label = QLabel(f"Welcome back, {self.user[1]}!")
        self.welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.welcome_label)

        # --- Stats Grid ---
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)

        self.total_points_box = self.create_stat_box("Total Points", "0")
        self.current_streak_box = self.create_stat_box("Current Streak", "0 Days")
        self.topics_completed_box = self.create_stat_box("Topics Completed", "0")

        stats_grid.addWidget(self.total_points_box, 0, 0)
        stats_grid.addWidget(self.current_streak_box, 0, 1)
        stats_grid.addWidget(self.topics_completed_box, 0, 2)

        layout.addLayout(stats_grid)

        # --- Badges Section ---
        badges_label = QLabel("Your Badges")
        badges_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 30px; margin-bottom: 10px;")
        layout.addWidget(badges_label)

        self.badges_grid = QGridLayout()
        self.badges_grid.setSpacing(15)

        layout.addLayout(self.badges_grid)

        self.setLayout(layout)

    def update_stats(self):
        """Updates the stats on the dashboard."""
        conn = create_connection()
        if conn and self.user:
            try:
                cursor = conn.cursor()

                # Update points and streak
                cursor.execute("SELECT total_points, current_streak FROM users WHERE id = ?", (self.user[0],))
                user_stats = cursor.fetchone()
                if user_stats:
                    self.total_points_box.findChild(QLabel, "value").setText(str(user_stats[0]))
                    self.current_streak_box.findChild(QLabel, "value").setText(f"{user_stats[1]} Days")

                # Update topics completed
                cursor.execute("SELECT COUNT(*) FROM progress WHERE user_id = ? AND completed = 1", (self.user[0],))
                topics_completed = cursor.fetchone()[0]
                self.topics_completed_box.findChild(QLabel, "value").setText(str(topics_completed))

                # Update badges
                cursor.execute("""
                    SELECT b.name, b.icon_path
                    FROM user_badges ub
                    JOIN badges b ON ub.badge_id = b.id
                    WHERE ub.user_id = ?
                """, (self.user[0],))
                badges = cursor.fetchall()

                # Clear existing badges
                for i in reversed(range(self.badges_grid.count())):
                    self.badges_grid.itemAt(i).widget().setParent(None)

                # Add new badges
                for i, badge in enumerate(badges):
                    badge_widget = self.create_badge(badge[0], badge[1])
                    self.badges_grid.addWidget(badge_widget, 0, i)

            except Exception as e:
                print(f"Error updating stats: {e}")
            finally:
                conn.close()

    def create_stat_box(self, title, value):
        """Creates a styled frame for displaying a statistic."""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setObjectName("stat_box")

        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; color: #888;")

        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet("font-size: 28px; font-weight: bold;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        frame.setLayout(layout)
        return frame

    def create_badge(self, name, icon_path):
        """Creates a widget to display a badge."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setFixedSize(64, 64)
            icon_label.setStyleSheet("background-color: #ddd; border-radius: 32px;") # Placeholder

        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)

        widget.setLayout(layout)
        return widget
