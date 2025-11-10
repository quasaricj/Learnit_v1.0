import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QHBoxLayout, QHeaderView)
from PyQt6.QtCore import Qt
from ..core.database import create_connection

class PointsHistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Points History")
        self.setGeometry(200, 200, 600, 400)
        self.init_ui()
        self.populate_history()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Date", "Action", "Points"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table)

        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def populate_history(self):
        """Populates the table with the user's points history."""
        conn = create_connection()
        if conn is None: return
        try:
            cursor = conn.cursor()
            # Assuming user_id = 1
            cursor.execute("SELECT created_at, action, points FROM points_history WHERE user_id = 1 ORDER BY created_at DESC")
            history = cursor.fetchall()

            self.history_table.setRowCount(len(history))
            for row_num, (date, action, points) in enumerate(history):
                self.history_table.setItem(row_num, 0, QTableWidgetItem(str(date)))
                self.history_table.setItem(row_num, 1, QTableWidgetItem(action))
                self.history_table.setItem(row_num, 2, QTableWidgetItem(str(points)))
        except Exception as e:
            print(f"Error populating points history: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = PointsHistoryDialog()
    dialog.show()
    sys.exit(app.exec())
