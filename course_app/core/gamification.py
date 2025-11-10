import sqlite3
import sys
import os

from .database import create_connection

POINTS_MAP = {
    "complete_topic": 10,
    "complete_within_target_time": 5,
    "first_topic_of_day": 10,
    "complete_module": 50,
    "complete_phase": 200,
    "7_day_streak": 100,
    "30_day_streak": 500,
}

def award_points(user_id, action):
    """Awards points to a user for a specific action."""
    points = POINTS_MAP.get(action)
    if not points:
        print(f"Invalid action: {action}")
        return

    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        # Update total points
        cursor.execute("UPDATE users SET total_points = total_points + ? WHERE id = ?", (points, user_id))

        # Log the transaction
        cursor.execute("INSERT INTO points_history (user_id, action, points) VALUES (?, ?, ?)", (user_id, action, points))

        conn.commit()
        print(f"Awarded {points} points to user {user_id} for {action}.")

        # Check for badges after awarding points
        check_and_award_badges(user_id, action)

    except sqlite3.Error as e:
        print(f"Error awarding points: {e}")
    finally:
        conn.close()

def check_and_award_badges(user_id, action, **kwargs):
    """Checks badge criteria and awards badges to the user."""
    conn = create_connection()
    if conn is None: return

    try:
        cursor = conn.cursor()

        # --- Starter Badges ---
        cursor.execute("SELECT COUNT(*) FROM progress WHERE user_id = ? AND completed = 1", (user_id,))
        completed_topics = cursor.fetchone()[0]
        if completed_topics >= 1: award_badge_if_not_earned(cursor, user_id, "First Step")
        if completed_topics >= 5: award_badge_if_not_earned(cursor, user_id, "Getting Started")
        if completed_topics >= 10: award_badge_if_not_earned(cursor, user_id, "Committed Learner")

        # --- Achievement Badges ---
        if action == "complete_module": award_badge_if_not_earned(cursor, user_id, "Module Master")
        if action == "complete_phase": award_badge_if_not_earned(cursor, user_id, "Phase Champion")
        # 'Course Conqueror' logic is more complex, requires checking all topics in a course

        # --- Speed Badges ---
        cursor.execute("SELECT COUNT(*) FROM progress p JOIN topics t ON p.topic_id = t.id WHERE p.user_id = ? AND p.completed = 1 AND p.time_spent_seconds <= t.target_time_minutes * 60", (user_id,))
        completed_in_time = cursor.fetchone()[0]
        if completed_in_time >= 10: award_badge_if_not_earned(cursor, user_id, "Speed Learner")
        if completed_in_time >= 30: award_badge_if_not_earned(cursor, user_id, "Time Master")
        if completed_in_time >= 50: award_badge_if_not_earned(cursor, user_id, "Lightning Fast")

        # --- Streak Badges ---
        cursor.execute("SELECT current_streak FROM users WHERE id = ?", (user_id,))
        streak = cursor.fetchone()[0]
        if streak >= 7: award_badge_if_not_earned(cursor, user_id, "Dedicated Student")
        if streak >= 15: award_badge_if_not_earned(cursor, user_id, "Consistency King")
        if streak >= 30: award_badge_if_not_earned(cursor, user_id, "Streak Legend")

        # --- Special Badges ---
        from datetime import datetime
        now = datetime.now()
        if now.hour < 9: award_badge_if_not_earned(cursor, user_id, "Early Bird")
        if now.hour >= 22: award_badge_if_not_earned(cursor, user_id, "Night Owl")
        if now.weekday() >= 5: # Saturday or Sunday
            cursor.execute("SELECT COUNT(*) FROM progress WHERE user_id = ? AND completed = 1 AND strftime('%w', completion_date) IN ('0', '6')", (user_id,))
            weekend_topics = cursor.fetchone()[0]
            if weekend_topics >= 5: award_badge_if_not_earned(cursor, user_id, "Weekend Warrior")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error checking/awarding badges: {e}")
    finally:
        conn.close()

def award_badge_if_not_earned(cursor, user_id, badge_name):
    """Helper function to award a badge if the user doesn't have it."""
    cursor.execute("SELECT id FROM badges WHERE name = ?", (badge_name,))
    badge_id_res = cursor.fetchone()
    if not badge_id_res: return
    badge_id = badge_id_res[0]

    cursor.execute("SELECT id FROM user_badges WHERE user_id = ? AND badge_id = ?", (user_id, badge_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)", (user_id, badge_id))
        print(f"Awarded badge '{badge_name}' to user {user_id}!")

def update_streak(user_id):
    """Updates the user's daily streak."""
    conn = create_connection()
    if conn is None: return

    try:
        cursor = conn.cursor()
        # Get the user's current streak and the date of their last completed topic
        cursor.execute("SELECT current_streak, DATE(MAX(completion_date)) FROM users u LEFT JOIN progress p ON u.id = p.user_id WHERE u.id = ?", (user_id,))
        streak, last_completion_date = cursor.fetchone()

        if last_completion_date is None:
            # First topic ever completed
            new_streak = 1
        else:
            from datetime import date, timedelta
            today = date.today()
            last_date = date.fromisoformat(last_completion_date)

            if today - last_date == timedelta(days=1):
                new_streak = streak + 1 # Continue streak
            elif today == last_date:
                new_streak = streak # Already completed a topic today
            else:
                new_streak = 1 # Reset streak

        cursor.execute("UPDATE users SET current_streak = ?, longest_streak = MAX(longest_streak, ?) WHERE id = ?", (new_streak, new_streak, user_id))
        conn.commit()
        print(f"User {user_id}'s streak is now {new_streak}.")

    except sqlite3.Error as e:
        print(f"Error updating streak: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    # Test the function
    award_points(1, "complete_topic")
