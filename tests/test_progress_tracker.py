import sys
import os
import unittest
import shutil
import sqlite3

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from course_app.core.progress_tracker import mark_topic_complete
from course_app.core.database import create_tables, create_connection
from course_app.core.user_management import create_user

# Set a dedicated test database
TEST_DB_FILE = os.path.join(os.path.dirname(__file__), "test_app.db")


class TestProgressTracker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the database and tables once for all tests."""
        # Ensure there's no old test database
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
        create_tables(TEST_DB_FILE)

    @classmethod
    def tearDownClass(cls):
        """Remove the test database file after all tests are done."""
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)

    def setUp(self):
        """Set up a test user and topic before each test."""
        self.conn = create_connection(TEST_DB_FILE)
        self.cursor = self.conn.cursor()

        # Create user
        self.user_id = create_user("test_user", TEST_DB_FILE)

        # Create topic
        self.cursor.execute("INSERT INTO courses (name, path) VALUES ('test_course', 'test_path')")
        self.cursor.execute("SELECT id FROM courses WHERE name = 'test_course'")
        course_id = self.cursor.fetchone()[0]
        self.cursor.execute("INSERT INTO topics (course_id, phase_name, module_name, topic_name, file_path, order_number) VALUES (?, ?, ?, ?, ?, ?)",
                           (course_id, "p1", "m1", "t1", "path1", 1))
        self.cursor.execute("SELECT id FROM topics WHERE file_path = 'path1'")
        self.topic_id = self.cursor.fetchone()[0]

        self.conn.commit()

    def tearDown(self):
        """Clean up the database entries after each test."""
        self.cursor.execute("DELETE FROM progress")
        self.cursor.execute("DELETE FROM user_badges")
        self.cursor.execute("DELETE FROM users")
        self.cursor.execute("DELETE FROM topics")
        self.cursor.execute("DELETE FROM courses")
        self.conn.commit()
        self.conn.close()

    def test_mark_topic_complete(self):
        """Test if marking a topic as complete works correctly."""
        mark_topic_complete(self.user_id, self.topic_id, TEST_DB_FILE)

        # Check if progress is recorded
        self.cursor.execute("SELECT completed FROM progress WHERE user_id = ? AND topic_id = ?", (self.user_id, self.topic_id))
        completed = self.cursor.fetchone()[0]
        self.assertEqual(completed, 1)

        # Check if points are awarded
        self.cursor.execute("SELECT total_points FROM users WHERE id = ?", (self.user_id,))
        points = self.cursor.fetchone()[0]
        self.assertEqual(points, 10)

        # Check if "First Step" badge is unlocked
        self.cursor.execute("SELECT b.name FROM user_badges ub JOIN badges b ON ub.badge_id = b.id WHERE ub.user_id = ?", (self.user_id,))
        unlocked_badges = {row[0] for row in self.cursor.fetchall()}
        self.assertIn("First Step", unlocked_badges)


if __name__ == '__main__':
    unittest.main()
