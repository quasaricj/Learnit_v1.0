from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_connection
from core.user_management import get_current_user

class RewardsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.user = get_current_user()
        self.init_ui()
        self.update_rewards()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Title ---
        title_label = QLabel("Rewards & Achievements")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # --- Points Display ---
        self.points_label = QLabel("Total Points: 0")
        self.points_label.setStyleSheet("font-size: 18px; margin-bottom: 20px;")
        layout.addWidget(self.points_label)

        # --- Badges Grid ---
        self.badges_grid = QGridLayout()
        self.badges_grid.setSpacing(15)

        layout.addLayout(self.badges_grid)

        self.setLayout(layout)

    def update_rewards(self):
        """Updates the rewards panel with the latest data."""
        conn = create_connection()
        if conn and self.user:
            try:
                cursor = conn.cursor()

                # Update points
                cursor.execute("SELECT total_points FROM users WHERE id = ?", (self.user[0],))
                total_points = cursor.fetchone()[0]
                self.points_label.setText(f"Total Points: {total_points}")

                # Update badges
                cursor.execute("SELECT name, icon_path FROM badges")
                all_badges = cursor.fetchall()

                cursor.execute("SELECT b.name FROM user_badges ub JOIN badges b ON ub.badge_id = b.id WHERE ub.user_id = ?", (self.user[0],))
                unlocked_badges = {row[0] for row in cursor.fetchall()}

                # Clear existing badges
                for i in reversed(range(self.badges_grid.count())):
                    self.badges_grid.itemAt(i).widget().setParent(None)

                # Add badges
                row, col = 0, 0
                for name, icon_path in all_badges:
                    unlocked = name in unlocked_badges
                    badge_widget = self.create_badge(name, icon_path, unlocked)
                    self.badges_grid.addWidget(badge_widget, row, col)
                    col += 1
                    if col >= 5:
                        col = 0
                        row += 1

            except Exception as e:
                print(f"Error updating rewards: {e}")
            finally:
                conn.close()

    def create_badge(self, name, icon_path, unlocked):
        """Creates a widget to display a badge."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setFixedSize(128, 128)
            icon_label.setStyleSheet("background-color: #ddd; border-radius: 64px;") # Placeholder

        if not unlocked:
            icon_label.setStyleSheet("background-color: #ddd; border-radius: 64px; opacity: 0.3;")

        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)

        widget.setLayout(layout)
        return widget
