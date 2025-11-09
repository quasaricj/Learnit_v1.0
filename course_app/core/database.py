import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'course_app.db')

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
        conn = sqlite3.connect(DATABASE_FILE)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables():
    """Create the tables in the database."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # User Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_points INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0
                );
            """)

            # Courses Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Topics Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    phase_name TEXT NOT NULL,
                    module_name TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    file_path TEXT NOT NULL UNIQUE,
                    order_number INTEGER,
                    target_time_minutes INTEGER,
                    FOREIGN KEY (course_id) REFERENCES courses (id)
                );
            """)

            # Progress Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    topic_id INTEGER,
                    completed BOOLEAN DEFAULT 0,
                    completion_date TIMESTAMP,
                    time_spent_seconds INTEGER DEFAULT 0,
                    bonus_earned INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (topic_id) REFERENCES topics (id)
                );
            """)

            # Badges Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    icon_path TEXT,
                    unlock_criteria TEXT
                );
            """)

            # User Badges Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    badge_id INTEGER,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (badge_id) REFERENCES badges (id)
                );
            """)

            conn.commit()
            print("Database tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    create_tables()
