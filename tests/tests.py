import sys
import os
import unittest
import shutil
import sqlite3

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from course_app.core.course_parser import parse_course_structure, get_course_structure
from course_app.core.progress_tracker import mark_topic_complete
from course_app.core.database import create_tables, create_connection
from course_app.core.user_management import create_user

# Set a dedicated test database
TEST_DB_FILE = os.path.join(os.path.dirname(__file__), "test_app.db")


class TestApp(unittest.TestCase):
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
        """Set up a test course directory, user and topic before each test."""
        self.test_course_dir = "test_course"
        os.makedirs(os.path.join(self.test_course_dir, "Phase 1", "Module 1"), exist_ok=True)
        with open(os.path.join(self.test_course_dir, "Phase 1", "Module 1", "Topic 1.md"), "w") as f:
            f.write("# Test Topic 1")

        parse_course_structure(self.test_course_dir, TEST_DB_FILE)

        self.conn = create_connection(TEST_DB_FILE)
        self.cursor = self.conn.cursor()

        # Create user
        self.user_id = create_user("test_user", TEST_DB_FILE)

        self.cursor.execute("SELECT id FROM topics WHERE file_path = 'test_course/Phase 1/Module 1/Topic 1.md'")
        self.topic_id = self.cursor.fetchone()[0]

        self.conn.commit()


    def tearDown(self):
        """Clean up the test course directory and database entries after each test."""
        shutil.rmtree(self.test_course_dir)
        self.cursor.execute("DELETE FROM progress")
        self.cursor.execute("DELETE FROM user_badges")
        self.cursor.execute("DELETE FROM users")
        self.cursor.execute("DELETE FROM topics")
        self.cursor.execute("DELETE FROM courses")
        self.conn.commit()
        self.conn.close()

    def test_parse_course_structure(self):
        """Test if the course structure is parsed and stored correctly."""
        # Get the course data
        all_courses = get_course_structure(TEST_DB_FILE)

        # Filter for the test course
        test_course_data = None
        for course in all_courses:
            if course['course_name'] == 'test_course':
                test_course_data = course
                break

        self.assertIsNotNone(test_course_data, "Test course was not found in the database.")
        self.assertEqual(len(test_course_data['topics']), 1)

        topic_details = test_course_data['topics'][0]
        self.assertEqual(topic_details[1], "Phase 1")
        self.assertEqual(topic_details[2], "Module 1")
        self.assertEqual(topic_details[3], "Topic 1")

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
