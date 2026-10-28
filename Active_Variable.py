import tkinter as tk
import time
import threading


class wake:
    def __init__(self):
        self.active = False
        self._timer = None
        self._lock = threading.Lock()


    def active_timer(self):
        with self._lock:
            if self._timer and self._timer.is_alive():
                self._timer.cancel()
            self.active = True
            self._timer = threading.Timer(30, self.force_stop)
            self._timer.daemon = True
            self._timer.start()

    def force_stop(self):
        with self._lock:
            if self._timer and self._timer.is_alive():
                self._timer.cancel()
            if self.active:
                self.active = False

    def check_active(self):
        with self._lock:
            return self.active