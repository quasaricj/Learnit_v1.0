import os
import sqlite3
import sys

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_connection

def parse_course_structure(course_path, db_file=None):
    """
    Parses the course structure from a given folder path and populates the database.
    """
    conn = create_connection(db_file) if db_file else create_connection()
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

def get_course_structure(db_file=None):
    """
    Retrieves the full course structure from the database.
    """
    conn = create_connection(db_file) if db_file else create_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM courses")
        courses = cursor.fetchall()

        structure = []
        for course_id, course_name in courses:
            cursor.execute("""
                SELECT phase_name, module_name, topic_name, file_path
                FROM topics
                WHERE course_id = ?
                ORDER BY order_number
            """, (course_id,))
            topics = cursor.fetchall()
            structure.append({
                "course_name": course_name,
                "topics": topics
            })
        return structure
    except sqlite3.Error as e:
        print(f"Error retrieving course structure: {e}")
        return None
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
