import os
import sqlite3
import sys

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_connection

def parse_course_structure(course_path):
    """
    Parses the course structure from a given folder path and populates the database.
    """
    conn = create_connection()
    if conn is None:
        print("Error! Cannot create the database connection.")
        return

    try:
        cursor = conn.cursor()

        course_name = os.path.basename(course_path)
        cursor.execute("INSERT OR IGNORE INTO courses (name, path) VALUES (?, ?)", (course_name, course_path))
        conn.commit()

        # Get the course_id, whether it was just inserted or already existed
        cursor.execute("SELECT id FROM courses WHERE path = ?", (course_path,))
        course_id_result = cursor.fetchone()
        if not course_id_result:
            print(f"Could not find or create course '{course_name}' in the database.")
            return
        course_id = course_id_result[0]


        order_counter = 0
        for phase_dir in sorted(os.listdir(course_path)):
            phase_path = os.path.join(course_path, phase_dir)
            if os.path.isdir(phase_path):
                for module_dir in sorted(os.listdir(phase_path)):
                    module_path = os.path.join(phase_path, module_dir)
                    if os.path.isdir(module_path):
                        for topic_file in sorted(os.listdir(module_path)):
                            if topic_file.endswith(".md"):
                                topic_path = os.path.join(module_path, topic_file)
                                topic_name = os.path.splitext(topic_file)[0]

                                # Set a default target time (e.g., 25 minutes)
                                target_time = 25

                                cursor.execute("""
                                    INSERT OR IGNORE INTO topics
                                    (course_id, phase_name, module_name, topic_name, file_path, order_number, target_time_minutes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (course_id, phase_dir, module_dir, topic_name, topic_path, order_counter, target_time))

                                order_counter += 1

        conn.commit()
        print(f"Course '{course_name}' has been parsed and stored successfully.")
    except sqlite3.Error as e:
        print(f"Error parsing course structure: {e}")
    finally:
        conn.close()

def get_course_structure():
    """
    Retrieves the full course structure from the database.
    """
    conn = create_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM courses")
        courses = cursor.fetchall()

        structure = []
        for course_id, course_name in courses:
            # Assuming a single user with id=1 for now
            # The query now fetches topic_id and its completion status
            cursor.execute("""
                SELECT t.id, t.phase_name, t.module_name, t.topic_name, t.file_path, p.completed
                FROM topics t
                LEFT JOIN progress p ON t.id = p.topic_id AND p.user_id = 1
                WHERE t.course_id = ?
                ORDER BY t.order_number
            """, (course_id,))
            topics = cursor.fetchall()
            structure.append({
                "course_name": course_name,
                "topics": topics  # topics is now a list of tuples (id, phase, module, topic, path, completed)
            })
        return structure
    except sqlite3.Error as e:
        print(f"Error retrieving course structure: {e}")
        return None
    finally:
        conn.close()

def delete_course(course_name):
    """
    Deletes a course and all its related data from the database.
    """
    conn = create_connection()
    if conn is None:
        raise ConnectionError("Failed to connect to the database.")

    try:
        cursor = conn.cursor()

        # Get course_id
        cursor.execute("SELECT id FROM courses WHERE name = ?", (course_name,))
        course_id_result = cursor.fetchone()
        if not course_id_result:
            print(f"Course '{course_name}' not found.")
            return
        course_id = course_id_result[0]

        # Get topic_ids for the course
        cursor.execute("SELECT id FROM topics WHERE course_id = ?", (course_id,))
        topic_ids = [row[0] for row in cursor.fetchall()]

        # Delete from progress table
        if topic_ids:
            cursor.execute(f"DELETE FROM progress WHERE topic_id IN ({','.join('?'*len(topic_ids))})", topic_ids)

        # Delete from topics table
        cursor.execute("DELETE FROM topics WHERE course_id = ?", (course_id,))

        # Delete from courses table
        cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))

        conn.commit()
        print(f"Course '{course_name}' and all its data have been deleted.")
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


if __name__ == '__main__':
    # Change to the script's directory to ensure correct relative paths
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create a dummy course structure for testing
    sample_course_dir = "../sample_course"
    if not os.path.exists(f"{sample_course_dir}/Phase 1/Module 1"):
        os.makedirs(f"{sample_course_dir}/Phase 1/Module 1")
    with open(f"{sample_course_dir}/Phase 1/Module 1/Topic 1.md", "w") as f:
        f.write("# Welcome to Topic 1")

    if not os.path.exists(f"{sample_course_dir}/Phase 1/Module 2"):
        os.makedirs(f"{sample_course_dir}/Phase 1/Module 2")
    with open(f"{sample_course_dir}/Phase 1/Module 2/Topic 2.md", "w") as f:
        f.write("# Welcome to Topic 2")

    parse_course_structure(sample_course_dir)

    # Verify the parsed structure
    parsed_data = get_course_structure()
    if parsed_data:
        for course in parsed_data:
            print(f"Course: {course['course_name']}")
            for topic in course['topics']:
                print(f"  - {topic[0]} > {topic[1]} > {topic[2]}")
