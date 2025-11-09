import time
import sys
import os

# Add the parent directory to the path to resolve module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.progress_tracker import mark_topic_complete

class TimerManager:
    def __init__(self, user_id, topic_id):
        self.user_id = user_id
        self.topic_id = topic_id
        self.start_time = None
        self.elapsed_time = 0
        self.is_running = False

    def start(self):
        """Starts the timer."""
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True
            print("Timer started.")

    def pause(self):
        """Pauses the timer."""
        if self.is_running:
            self.elapsed_time += time.time() - self.start_time
            self.is_running = False
            print("Timer paused.")

    def resume(self):
        """Resumes the timer."""
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True
            print("Timer resumed.")

    def stop_and_save(self):
        """Stops the timer and saves the progress."""
        if self.is_running:
            self.elapsed_time += time.time() - self.start_time
            self.is_running = False

        time_spent = int(self.elapsed_time)
        mark_topic_complete(self.user_id, self.topic_id, time_spent_seconds=time_spent)
        print(f"Timer stopped. Time spent: {time_spent} seconds. Progress saved.")

        # Reset timer
        self.elapsed_time = 0

if __name__ == '__main__':
    # This is a simple test to demonstrate the timer's functionality.
    # In the actual app, this would be controlled by UI events.

    # Assume we have a user_id and topic_id
    test_user_id = 1
    test_topic_id = 1 # Assuming this topic exists from previous tests

    timer = TimerManager(test_user_id, test_topic_id)

    print("Simulating a learning session...")
    timer.start()
    time.sleep(2) # Simulate learning for 2 seconds
    timer.pause()
    print(f"Paused. Elapsed time so far: {timer.elapsed_time:.2f}s")

    time.sleep(1) # User takes a break

    timer.resume()
    time.sleep(3) # Learns for another 3 seconds
    timer.stop_and_save()

    # Verify the progress was updated
    from core.progress_tracker import get_user_progress
    progress = get_user_progress(test_user_id)
    if progress:
        print("\nUpdated User Progress:")
        for item in progress:
            print(f"  - Topic: {item[0]}, Completed: {'Yes' if item[1] else 'No'}, Time: {item[3]}s")
