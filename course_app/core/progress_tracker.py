import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_connection
from core.rewards_engine import award_points, unlock_badge

def mark_topic_complete(user_id, topic_id, db_file=None):
    """Marks a topic as complete for a user."""
    conn = create_connection(db_file) if db_file else create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO progress (user_id, topic_id, completed, completion_date) VALUES (?, ?, 1, ?)",
                           (user_id, topic_id, datetime.now()))

            # Award points for completing the topic
            award_points(user_id, 10, conn)

            # Check for badge unlocks
            check_badge_unlocks(user_id, conn)

            # Update streak
            update_streak(user_id, conn)

            conn.commit()

        except Exception as e:
            print(f"Error marking topic complete: {e}")
        finally:
            conn.close()

def update_streak(user_id, conn):
    """Updates the user's learning streak."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT completion_date FROM progress WHERE user_id = ? ORDER BY completion_date DESC LIMIT 1", (user_id,))
        last_completion_date_str = cursor.fetchone()

        if last_completion_date_str:
            last_completion_date = datetime.fromisoformat(last_completion_date_str[0])
            today = datetime.now().date()

            if last_completion_date.date() == today - timedelta(days=1):
                cursor.execute("UPDATE users SET current_streak = current_streak + 1 WHERE id = ?", (user_id,))
            elif last_completion_date.date() != today:
                cursor.execute("UPDATE users SET current_streak = 1 WHERE id = ?", (user_id,))
        else:
            cursor.execute("UPDATE users SET current_streak = 1 WHERE id = ?", (user_id,))

    except Exception as e:
        print(f"Error updating streak: {e}")

def check_badge_unlocks(user_id, conn):
    """Checks if the user has unlocked any new badges."""
    try:
        cursor = conn.cursor()

        # Get user stats
        cursor.execute("SELECT COUNT(*) FROM progress WHERE user_id = ?", (user_id,))
        completed_topics = cursor.fetchone()[0]

        cursor.execute("SELECT current_streak FROM users WHERE id = ?", (user_id,))
        current_streak = cursor.fetchone()[0]

        # Check for each badge
        if completed_topics >= 1:
            unlock_badge(user_id, "First Step", conn)
        if current_streak >= 7:
            unlock_badge(user_id, "Dedicated Student", conn)
        if current_streak >= 30:
            unlock_badge(user_id, "Streak Legend", conn)

        # These are more complex and would require more logic to implement correctly
        # unlock_badge(user_id, "Module Master")
        # unlock_badge(user_id, "Phase Champion")
        # unlock_badge(user_id, "Speed Learner")
        # unlock_badge(user_id, "Time Master")
        # unlock_badge(user_id, "Course Conqueror")

    except Exception as e:
        print(f"Error checking badge unlocks: {e}")
