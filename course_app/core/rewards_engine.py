import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_connection

def award_points(user_id, points):
    """Awards a specified number of points to a user."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET total_points = total_points + ? WHERE id = ?", (points, user_id))
            conn.commit()
        except Exception as e:
            print(f"Error awarding points: {e}")
        finally:
            conn.close()

def unlock_badge(user_id, badge_name):
    """Unlocks a badge for a user."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM badges WHERE name = ?", (badge_name,))
            badge_id = cursor.fetchone()[0]
            cursor.execute("INSERT OR IGNORE INTO user_badges (user_id, badge_id) VALUES (?, ?)", (user_id, badge_id))
            conn.commit()
        except Exception as e:
            print(f"Error unlocking badge: {e}")
        finally:
            conn.close()
