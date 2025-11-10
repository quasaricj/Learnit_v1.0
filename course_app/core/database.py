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

            # Points History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS points_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
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

def create_default_user():
    """Creates a default user if one doesn't exist."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE id = 1")
            user = cursor.fetchone()
            if not user:
                cursor.execute("INSERT INTO users (id, username) VALUES (1, 'Learner')")
                conn.commit()
                print("Default user created.")
        except sqlite3.Error as e:
            print(f"Error creating default user: {e}")
        finally:
            conn.close()

def populate_badges():
    """Populates the badges table with the default set of badges."""
    badges = [
        ('First Step', 'Complete your first topic', '👣', 'complete_topic:1'),
        ('Getting Started', 'Complete 5 topics', '🌱', 'complete_topic:5'),
        ('Committed Learner', 'Complete 10 topics', '📚', 'complete_topic:10'),
        ('Module Master', 'Complete any module', '🎓', 'complete_module:1'),
        ('Phase Champion', 'Complete any phase', '🏆', 'complete_phase:1'),
        ('Course Conqueror', 'Complete entire course', '👑', 'complete_course:1'),
        ('Speed Learner', 'Complete 10 topics within target time', '⚡', 'complete_within_time:10'),
        ('Time Master', 'Complete 30 topics within target time', '⏱️', 'complete_within_time:30'),
        ('Lightning Fast', 'Complete 50 topics within target time', '🚀', 'complete_within_time:50'),
        ('Dedicated Student', 'Maintain 7-day streak', '🔥', 'streak:7'),
        ('Consistency King', 'Maintain 15-day streak', '⭐', 'streak:15'),
        ('Streak Legend', 'Maintain 30-day streak', '💎', 'streak:30'),
        ('Early Bird', 'Complete a topic before 9 AM', '🌅', 'early_bird:1'),
        ('Night Owl', 'Complete a topic after 10 PM', '🦉', 'night_owl:1'),
        ('Weekend Warrior', 'Complete 5 topics on a weekend', '💪', 'weekend_warrior:5'),
    ]

    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            for name, description, icon, criteria in badges:
                cursor.execute("INSERT OR IGNORE INTO badges (name, description, icon_path, unlock_criteria) VALUES (?, ?, ?, ?)",
                               (name, description, icon, criteria))
            conn.commit()
            print("Badges populated successfully.")
        except sqlite3.Error as e:
            print(f"Error populating badges: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    create_tables()
    create_default_user()
    populate_badges()
