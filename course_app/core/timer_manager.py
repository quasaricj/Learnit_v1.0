from PyQt6.QtCore import QTimer

class TimerManager:
    def __init__(self, update_callback):
        self.timer = QTimer()
        self.time_elapsed = 0
        self.timer.timeout.connect(update_callback)

    def start_timer(self):
        self.timer.start(1000)

    def pause_timer(self):
        self.timer.stop()

    def reset_timer(self):
        self.timer.stop()
        self.time_elapsed = 0
