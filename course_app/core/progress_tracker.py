import sqlite3
import sys
import os
from datetime import datetime

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_connection

def mark_topic_complete(user_id, topic_id, time_spent_seconds=0, bonus_earned=0):
    """Marks a topic as complete for a given user."""
    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Check if a progress entry already exists
        cursor.execute("SELECT id FROM progress WHERE user_id = ? AND topic_id = ?", (user_id, topic_id))
        progress_entry = cursor.fetchone()

        if progress_entry:
            # Update existing entry
            cursor.execute("""
                UPDATE progress
                SET completed = 1, completion_date = ?, time_spent_seconds = time_spent_seconds + ?, bonus_earned = bonus_earned + ?
                WHERE id = ?
            """, (datetime.now(), time_spent_seconds, bonus_earned, progress_entry[0]))
        else:
            # Create a new entry
            cursor.execute("""
                INSERT INTO progress (user_id, topic_id, completed, completion_date, time_spent_seconds, bonus_earned)
                VALUES (?, ?, 1, ?, ?, ?)
            """, (user_id, topic_id, datetime.now(), time_spent_seconds, bonus_earned))

        conn.commit()
        print(f"Topic {topic_id} marked as complete for user {user_id}.")
    except sqlite3.Error as e:
        print(f"Error updating progress: {e}")
    finally:
        conn.close()

def get_user_progress(user_id):
    """Retrieves all progress for a given user."""
    conn = create_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.topic_name, p.completed, p.completion_date, p.time_spent_seconds
            FROM progress p
            JOIN topics t ON p.topic_id = t.id
            WHERE p.user_id = ?
        """, (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving user progress: {e}")
        return None
    finally:
        conn.close()

if __name__ == '__main__':
    # Test the progress tracker
    user_id = None
    topic_id = None

    # Step 1: Setup user and get topic ID
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", ('test_user',))
            conn.commit()

            cursor.execute("SELECT id FROM users WHERE username = ?", ('test_user',))
            user_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM topics LIMIT 1")
            topic_id_result = cursor.fetchone()
            if topic_id_result:
                topic_id = topic_id_result[0]

            conn.close()
    except sqlite3.Error as e:
        print(f"Database error during setup: {e}")

    # Step 2: Mark topic as complete (if setup was successful)
    if user_id and topic_id:
        mark_topic_complete(user_id, topic_id, time_spent_seconds=1500)

        # Step 3: Verify progress
        progress = get_user_progress(user_id)
        if progress:
            print("\nUser Progress:")
            for item in progress:
                print(f"  - Topic: {item[0]}, Completed: {'Yes' if item[1] else 'No'}, Date: {item[2]}, Time: {item[3]}s")
    else:
        print("Could not find user or topic to test progress.")
