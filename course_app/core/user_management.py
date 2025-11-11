import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_connection

def create_user(username, db_file=None):
    """Creates a new user and returns the user ID."""
    conn = create_connection(db_file) if db_file else create_connection()
    user_id = None
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
            conn.commit()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_id = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error creating user: {e}")
        finally:
            conn.close()
    return user_id

def get_current_user(db_file=None):
    """Gets the current user, creating one if none exist."""
    conn = create_connection(db_file) if db_file else create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE username = 'default_user'")
            user = cursor.fetchone()
            if user:
                return user
            else:
                create_user("default_user", db_file)
                cursor.execute("SELECT id, username FROM users WHERE username = 'default_user'")
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting current user: {e}")
            return None
        finally:
            conn.close()
