import sys
import os

# Ensure the course_app directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.database import create_tables
from core.course_parser import parse_course_structure

def setup_initial_data():
    """
    Initializes the database and loads a sample course if none exist.
    """
    print("Performing first-time setup...")
    create_tables()

    # Check if a course is already loaded
    from core.database import create_connection
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM courses")
    course_count = cursor.fetchone()[0]
    conn.close()

    if course_count == 0:
        print("No courses found. Loading sample course...")
        sample_course_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_course")

        if not os.path.exists(sample_course_path):
            os.makedirs(os.path.join(sample_course_path, "Phase 1 - Welcome", "Module 1 - Introduction"))

            # Create a more detailed sample topic
            topic_content = """
# Welcome to Learnit!

This is a sample topic to get you started.

## Features

- **Offline Learning:** Learn anytime, anywhere.
- **Gamification:** Earn points and badges as you progress.
- **Progress Tracking:** See how far you've come.

Happy learning!
"""
            with open(os.path.join(sample_course_path, "Phase 1 - Welcome", "Module 1 - Introduction", "1. Getting Started.md"), "w") as f:
                f.write(topic_content)

        parse_course_structure(sample_course_path)
    else:
        print("Existing course data found.")


def main():
    """
    The main entry point for the Learnit application.
    """
    # Perform initial setup
    setup_initial_data()

    # Create and run the application
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
