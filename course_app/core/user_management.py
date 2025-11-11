import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_connection

def create_user(username):
    """Creates a new user."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
            conn.commit()
        except Exception as e:
            print(f"Error creating user: {e}")
        finally:
            conn.close()

def get_current_user():
    """Gets the current user."""
    # For now, we'll hardcode the user. In a real application, you would
    # implement a login system.
    create_user("default_user")
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE username = 'default_user'")
            return cursor.fetchone()
        except Exception as e:
            print(f"Error getting current user: {e}")
            return None
        finally:
            conn.close()
