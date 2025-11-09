import sqlite3
import sys
import os
from datetime import datetime

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_connection

# --- Gamification Rules ---
POINTS = {
    "complete_topic": 10,
    "complete_within_target_time": 5,
    "first_topic_of_day": 10,
    "complete_module": 50,
    "complete_phase": 200,
    "7_day_streak": 100,
}

BADGES = {
    "First Step": "Complete your first topic",
    "Module Master": "Complete any module",
    "Phase Champion": "Complete any phase",
    "Speed Learner": "Complete 10 topics within target time",
    "Dedicated Student": "Maintain 7-day learning streak",
    "Course Conqueror": "Complete entire course",
}

def add_points(user_id, points_category):
    """Adds points to a user's total."""
    points_to_add = POINTS.get(points_category, 0)
    if points_to_add == 0:
        return

    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET total_points = total_points + ? WHERE id = ?", (points_to_add, user_id))
        conn.commit()
        print(f"Awarded {points_to_add} points to user {user_id} for '{points_category}'.")
    except sqlite3.Error as e:
        print(f"Error adding points: {e}")
    finally:
        conn.close()

def unlock_badge(user_id, badge_name):
    """Unlocks a badge for a user."""
    if badge_name not in BADGES:
        return

    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Get badge_id
        cursor.execute("SELECT id FROM badges WHERE name = ?", (badge_name,))
        badge_id_result = cursor.fetchone()
        if not badge_id_result:
            # Badge not in DB, insert it
            cursor.execute("INSERT INTO badges (name, description) VALUES (?, ?)", (badge_name, BADGES[badge_name]))
            badge_id = cursor.lastrowid
        else:
            badge_id = badge_id_result[0]

        # Check if user already has this badge
        cursor.execute("SELECT id FROM user_badges WHERE user_id = ? AND badge_id = ?", (user_id, badge_id))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)", (user_id, badge_id))
            conn.commit()
            print(f"User {user_id} unlocked the '{badge_name}' badge!")
    except sqlite3.Error as e:
        print(f"Error unlocking badge: {e}")
    finally:
        conn.close()

def check_achievements(user_id, topic_id):
    """Checks for and awards new achievements after a topic is completed."""
    # 1. Basic points for completing a topic
    add_points(user_id, "complete_topic")

    # 2. Check for "First Step" badge
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM progress WHERE user_id = ?", (user_id,))
    completed_topics = cursor.fetchone()[0]
    if completed_topics == 1:
        unlock_badge(user_id, "First Step")

    # In a real app, we would have more complex checks here for other badges and streaks.
    # For now, this is a good starting point.
    conn.close()


if __name__ == '__main__':
    # Test the rewards engine
    test_user_id = 1 # Assumes user with ID 1 exists
    test_topic_id = 1 # Assumes topic with ID 1 exists

    print(f"--- Checking achievements for User {test_user_id} after completing Topic {test_topic_id} ---")

    # Simulate completing a topic
    from core.progress_tracker import mark_topic_complete
    mark_topic_complete(test_user_id, test_topic_id)

    # Check for achievements
    check_achievements(test_user_id, test_topic_id)

    # Verify points and badges
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT total_points FROM users WHERE id = ?", (test_user_id,))
        points = cursor.fetchone()[0]
        print(f"\nUser's total points: {points}")

        cursor.execute("""
            SELECT b.name
            FROM user_badges ub
            JOIN badges b ON ub.badge_id = b.id
            WHERE ub.user_id = ?
        """, (test_user_id,))
        badges = cursor.fetchall()
        print("User's unlocked badges:")
        for badge in badges:
            print(f"  - {badge[0]}")

        conn.close()
