import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel,
                             QWidget, QScrollArea)
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt
from ..core.database import create_connection

class TrophyRoomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Trophy Room")
        self.setGeometry(200, 200, 800, 600)
        self.init_ui()
        self.populate_badges()

    def init_ui(self):
        layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.badge_container = QWidget()
        self.badge_layout = QGridLayout(self.badge_container)
        scroll_area.setWidget(self.badge_container)

    def populate_badges(self):
        """Populates the grid with all badges from the database."""
        conn = create_connection()
        if conn is None: return
        try:
            cursor = conn.cursor()
            # Get all badges and join with user_badges to see which are unlocked
            cursor.execute("""
                SELECT b.name, b.description, b.icon_path, ub.unlocked_at
                FROM badges b
                LEFT JOIN user_badges ub ON b.id = ub.badge_id AND ub.user_id = 1
            """)
            badges = cursor.fetchall()

            row, col = 0, 0
            for name, description, icon, unlocked_at in badges:
                badge_widget = self.create_badge_widget(name, description, icon, unlocked_at)
                self.badge_layout.addWidget(badge_widget, row, col)
                col += 1
                if col > 3:
                    col = 0
                    row += 1
        except Exception as e:
            print(f"Error populating badges: {e}")
        finally:
            conn.close()

    def create_badge_widget(self, name, description, icon, unlocked_at):
        """Creates a widget for a single badge."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addWidget(description_label)

        if not unlocked_at:
            widget.setEnabled(False) # Grays out the widget

        return widget

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = TrophyRoomDialog()
    dialog.show()
    sys.exit(app.exec())
