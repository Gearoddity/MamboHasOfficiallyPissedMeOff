import tkinter as tk
from datetime import datetime
import time
import threading
import subprocess
import platform
import os
# Import external utility managers
from weather_manager import get_weather
from medication_manager import get_medications, DAYS as PULL_DAYS
from calendar_manager import get_upcoming_events
from news_manager import get_news

# --- Aesthetic Theme Constants ---
BG = '#101A27'
CARD = '#1E3042'
WHITE = '#FFFFFF'
ACCENT = '#63DCC1'
MUTED = '#A4B6CB'


class MamboScreens(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Mambo Smart Assistant")
        self.geometry("800x480")
        self.minsize(640, 400)
        self.configure(bg=BG)

        # Main container with theme background to stack all screens
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.active_screen = None
        self.pill_day = datetime.now().strftime('%A')
        self.wake_indicators = []

        # Track active auto-return timer ID
        self.idle_timer_id = None

        screen_names = ["Home", "Weather", "Pills", "News", "Schedule", "Number5"]

        for name in screen_names:
            frame = tk.Frame(container, bg=BG)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

            build_method = getattr(self, f"build_{name.lower()}")
            build_method(frame)

        self.show_screen("Home")
        self.update_clock()
        # Track active audio process for stopping
        self.audio_process = None

    # --- UI Helper Methods ---
    def _text(self, parent, value, size=18, color=WHITE, bold=False, **kwargs):
        return tk.Label(parent, text=value, bg=kwargs.pop('bg', BG), fg=color,
                        font=('Arial', size, 'bold' if bold else 'normal'),
                        justify='left', **kwargs)

    def _create_header_and_body(self, frame, title):
        for widget in frame.winfo_children():
            widget.destroy()

        header = tk.Frame(frame, bg=BG)
        header.pack(fill='x', padx=24, pady=(18, 10))
        self._text(header, title, 24, ACCENT, True).pack(side='left')

        # Wake word / Active status indicator badge for this specific header
        wake_indicator = self._text(header, "", 14, ACCENT, bold=True, bg=BG)
        wake_indicator.pack(side='left', padx=20)
        self.wake_indicators.append(wake_indicator)

        self.time_label = self._text(header, '', 16)
        self.time_label.pack(side='right')

        body = tk.Frame(frame, bg=CARD, padx=28, pady=24)
        body.pack(fill='both', expand=True, padx=22, pady=(4, 24))
        return body

    def set_wake_status(self, is_active):
        """Updates the visual indicator across all screen headers."""
        for indicator in self.wake_indicators:
            if indicator.winfo_exists():
                if is_active:
                    indicator.config(text="● LISTENING...", fg=ACCENT)
                else:
                    indicator.config(text="")

    # --- Screen Switching Function ---
    def show_screen(self, screen_name):
        if screen_name in self.frames:
            frame = self.frames[screen_name]
            frame.tkraise()
            self.active_screen = screen_name

            if screen_name == "Weather":
                threading.Thread(target=self.refresh_weather, daemon=True).start()
            elif screen_name == "Pills":
                self.pill_day = datetime.now().strftime('%A')
                self.refresh_pills()
            elif screen_name == "News":
                threading.Thread(target=self.refresh_news, daemon=True).start()
            elif screen_name == "Schedule":
                threading.Thread(target=self.refresh_schedule, daemon=True).start()
            elif screen_name == "Number5":
                # Trigger audio playback in a background thread
                threading.Thread(target=self.play_mambo_audio, daemon=True).start()

            self._reset_idle_timer()

    def get_current_screen(self):
        """Returns the string name of the screen currently in front"""
        return getattr(self, 'active_screen', "Unknown")

    # --- Clock Update Function ---
    def update_clock(self):
        """Updates live clock widgets across headers and idle views every second"""
        current_time = datetime.now().strftime('%I:%M %p').lstrip('0')

        if hasattr(self, 'time_label') and self.time_label.winfo_exists():
            self.time_label.config(text=current_time)

        if hasattr(self, 'idle_clock') and self.idle_clock.winfo_exists():
            self.idle_clock.config(text=current_time)
            self.idle_date.config(text=datetime.now().strftime('%A, %B %d, %Y'))

        self.after(1000, self.update_clock)

    def _reset_idle_timer(self):
        """Cancels existing idle timer and starts a 2-minute countdown if off Home."""
        if self.idle_timer_id is not None:
            self.after_cancel(self.idle_timer_id)
            self.idle_timer_id = None

        if self.active_screen != "Home":
            self.idle_timer_id = self.after(120000, self._return_to_home)

    def _return_to_home(self):
        """Switches back to Home screen after timer expires."""
        self.show_screen("Home")

    # --- Screen Setup & Data Integration Functions ---
    def build_home(self, frame):
        body = self._create_header_and_body(frame, "MAMBO ASSISTANT HOME")
        self.idle_clock = self._text(body, '', 36, ACCENT, True, bg=CARD)
        self.idle_clock.pack(pady=(20, 5))
        self.idle_date = self._text(body, '', 16, MUTED, bg=CARD)
        self.idle_date.pack(pady=(0, 20))
        self._text(body, "Welcome back! Use the voice command 'Hey Mambo' to get started.", 15,
                   WHITE, bg=CARD, wraplength=600).pack(anchor='w')

    def build_weather(self, frame):
        body = self._create_header_and_body(frame, "TAMPA, FL | WEATHER")
        self.weather_label = self._text(body, "Loading weather data...", 20, WHITE, bg=CARD,
                                        anchor='nw')
        self.weather_label.pack(fill='both', expand=True)

    def refresh_weather(self):
        try:
            data = get_weather()
            text = (f"Temperature: {data.get('temperature')}°F\n"
                    f"Condition: {data.get('condition')}\n"
                    f"Humidity: {data.get('humidity')}%")
        except Exception as e:
            text = f"Could not load weather: {e}"

        self.after(0, lambda: self._update_weather_label(text))

    def _update_weather_label(self, text):
        if hasattr(self, 'weather_label') and self.weather_label.winfo_exists():
            self.weather_label.config(text=text)

    def build_schedule(self, frame):
        body = self._create_header_and_body(frame, "UPCOMING SCHEDULE")
        self.schedule_label = self._text(body, "Loading schedule events...", 16, WHITE, bg=CARD,
                                         anchor='nw')
        self.schedule_label.pack(fill='both', expand=True)

    def refresh_schedule(self):
        try:
            events = get_upcoming_events(limit=5)
            if events is None:
                text = "Calendar not connected. Set MAMBO_ICS_URL or calendar.ics."
            elif not events:
                text = "No upcoming events found in the next 30 days."
            else:
                text = "\n\n".join(events)
        except Exception as e:
            text = f"Error loading schedule: {e}"

        self.after(0, lambda: self._update_schedule_label(text))

    def _update_schedule_label(self, text):
        if hasattr(self, 'schedule_label') and self.schedule_label.winfo_exists():
            self.schedule_label.config(text=text)

    def build_pills(self, frame):
        body = self._create_header_and_body(frame, "MEDICATION SCHEDULE")
        self.pills_label = self._text(body, "Loading medication schedule...", 18, WHITE, bg=CARD, anchor='nw')
        self.pills_label.pack(fill='both', expand=True)
        self._text(body, "Demo data only — not medical instructions", 12, MUTED, bg=CARD).pack(anchor='w', pady=(10, 0))

    def refresh_pills(self):
        try:
            items = get_medications(self.pill_day)
            if not items:
                text = f"No medications scheduled for today ({self.pill_day})."
            else:
                lines = [f"• {entry.get('time', '--:--')} - {entry.get('name', 'Medication')}" for entry in items]
                text = f"Today's Schedule ({self.pill_day}):\n\n" + "\n".join(lines)
        except Exception as e:
            text = f"Error loading schedule: {e}"
        if hasattr(self, 'pills_label') and self.pills_label.winfo_exists():
            self.pills_label.config(text=text)

    def build_messages(self, frame):
        body = self._create_header_and_body(frame, "MESSAGES & ALERTS")
        self.message_label = self._text(body, "No new messages.", 20, WHITE, bg=CARD, anchor='nw')
        self.message_label.pack(fill='both', expand=True)

    def build_profile(self, frame):
        body = self._create_header_and_body(frame, "USER PROFILE & SETTINGS")
        self._text(body, "System Name: Mambo Smart Display\nStatus: Active & Connected\nVersion: 1.0.0", 18, WHITE,
                   bg=CARD).pack(anchor='w', pady=10)

    def build_number5(self, frame):
        body = self._create_header_and_body(frame, "NUMBER FIVE VIEW")
        self._text(body, "Number Five custom layout active.", 18, WHITE, bg=CARD, anchor='nw').pack(
            fill='both', expand=True)

    def build_news(self, frame):
        body = self._create_header_and_body(frame, "NEWS FEED")
        self.news_label = self._text(body, "Loading headlines...", 16, WHITE, bg=CARD, anchor='nw')
        self.news_label.pack(fill='both', expand=True)

    def refresh_news(self):
        try:
            headlines = get_news(limit=5)
            formatted_text = "\n\n".join([f"• {headline}" for headline in headlines])
        except Exception as e:
            formatted_text = f"Error loading news feed: {e}"

        self.after(0, lambda: self._update_news_label(formatted_text))

    def _update_news_label(self, text):
        if hasattr(self, 'news_label') and self.news_label.winfo_exists():
            self.news_label.config(text=text)

    # --- WAV Audio Management Methods ---
        # --- WAV Audio Management Methods ---
        def play_mambo_audio(self):
            """Plays the Mambo No 5 audio file using native OS media players (.wav format)."""
            audio_path = os.path.join(os.path.dirname(__file__), "Audio", "Number5.wav")

            if not os.path.exists(audio_path):
                print(f"[AUDIO] File not found at: {audio_path}")
                return

            # Stop any currently playing audio first
            self.stop_mambo_audio()

            try:
                system_name = platform.system()
                print(f"[AUDIO] Playing on {system_name}: {audio_path}")

                if system_name == "Darwin":  # macOS
                    self.audio_process = subprocess.Popen(["afplay", audio_path])
                elif system_name == "Windows":  # Windows native SoundPlayer (.wav) with PlaySync
                    safe_path = audio_path.replace("'", "''").replace("\\", "/")
                    ps_command = f"(New-Object System.Media.SoundPlayer '{safe_path}').PlaySync()"
                    self.audio_process = subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_command])
                else:  # Linux / Raspberry Pi 5 (ALSA aplay)
                    self.audio_process = subprocess.Popen(["aplay", audio_path])

            except Exception as e:
                print(f"[AUDIO] Error playing sound: {e}")

        def stop_mambo_audio(self):
            """Stops the native audio process immediately when requested via voice."""
            if self.audio_process and self.audio_process.poll() is None:
                print("[AUDIO] Stopping music playback.")
                try:
                    self.audio_process.terminate()
                    self.audio_process.wait(timeout=1)
                except Exception:
                    self.audio_process.kill()
                self.audio_process = None

        def play_wake_audio(self):
            """Plays the short wake chime (.wav format) instantly with zero latency."""
            wake_audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Audio", "MamboChime.wav")

            if not os.path.exists(wake_audio_path):
                print(f"[AUDIO] Chime file not found at: {wake_audio_path}")
                return

            try:
                system_name = platform.system()

                if system_name == "Darwin":  # macOS
                    subprocess.Popen(["afplay", wake_audio_path])
                elif system_name == "Windows":  # Windows native SoundPlayer (.wav) with PlaySync
                    safe_path = wake_audio_path.replace("'", "''").replace("\\", "/")
                    ps_command = f"(New-Object System.Media.SoundPlayer '{safe_path}').PlaySync()"
                    subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_command])
                else:  # Linux / Raspberry Pi 5 (ALSA aplay)
                    subprocess.Popen(["aplay", wake_audio_path])

            except Exception as e:
                print(f"[AUDIO] Wake sound error: {e}")
if __name__ == "__main__":
    app = MamboScreens()
    app.mainloop()

def main():
    app = MamboScreens()
    app.after(2000, lambda: app.show_screen("Pills"))
    app.after(4000, lambda: app.show_screen("News"))
    app.after(6000, lambda: app.show_screen("Weather"))
    app.after(8000, lambda: app.show_screen("Number5"))
    app.after(10000, lambda: app.show_screen("Schedule"))
    app.after(12000, lambda: app.show_screen("Home"))
    app.mainloop()