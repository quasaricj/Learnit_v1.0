import sys
import os
import unittest
import shutil
import sqlite3

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from course_app.core.course_parser import parse_course_structure, get_course_structure
from course_app.core.database import create_tables, create_connection

# Set a dedicated test database
TEST_DB_FILE = os.path.join(os.path.dirname(__file__), "test_app.db")


class TestCourseParser(unittest.TestCase):
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
        """Set up a test course directory before each test."""
        self.test_course_dir = "test_course"
        os.makedirs(os.path.join(self.test_course_dir, "Phase 1", "Module 1"), exist_ok=True)
        with open(os.path.join(self.test_course_dir, "Phase 1", "Module 1", "Topic 1.md"), "w") as f:
            f.write("# Test Topic 1")

        # Also create a default user for progress tracking tests later
        conn = create_connection(TEST_DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", ('test_user',))
        conn.commit()
        conn.close()


    def tearDown(self):
        """Clean up the test course directory and database entries after each test."""
        shutil.rmtree(self.test_course_dir)
        conn = create_connection(TEST_DB_FILE)
        if conn:
            try:
                cursor = conn.cursor()
                # Use DELETE without WHERE to clear the tables for the next test
                cursor.execute("DELETE FROM topics")
                cursor.execute("DELETE FROM courses")
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error cleaning database: {e}")
            finally:
                conn.close()

    def test_parse_course_structure(self):
        """Test if the course structure is parsed and stored correctly."""
        parse_course_structure(self.test_course_dir, TEST_DB_FILE)

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
        self.assertEqual(topic_details[0], "Phase 1")
        self.assertEqual(topic_details[1], "Module 1")
        self.assertEqual(topic_details[2], "Topic 1")


if __name__ == '__main__':
    unittest.main()
