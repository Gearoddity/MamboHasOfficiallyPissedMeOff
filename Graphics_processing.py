import tkinter as tk
from datetime import datetime
import time

# Import external utility managers
from weather_manager import get_weather
from medication_manager import get_medications, DAYS as PULL_DAYS
from calendar_manager import get_upcoming_events

# --- Aesthetic Theme Constants (from mambo_gui.py) ---
BG = '#101A27'
CARD = '#1E3042'
WHITE = '#FFFFFF'
ACCENT = '#63DCC1'
MUTED = '#A4B6CB'
DAYS = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')


class MamboScreens(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Mambo Smart Assistant")
        self.geometry("800x480")
        self.minsize(640, 400)
        self.configure(bg=BG)

        # 1. Main container with theme background to stack all screens
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary to hold references to all screen frames
        self.frames = {}
        self.active_screen = None
        self.pill_day = datetime.now().strftime('%A')

        # 2. Define the screen names
        screen_names = ["Home", "Weather", "Calendar", "Pills", "Messages", "Profile"]

        # 3. Create, grid, and build each screen dynamically
        for name in screen_names:
            frame = tk.Frame(container, bg=BG)
            self.frames[name] = frame
            # Stack all frames in the exact same grid cell (0, 0)
            frame.grid(row=0, column=0, sticky="nsew")

            # Dynamically call the respective build function (e.g., self.build_weather)
            build_method = getattr(self, f"build_{name.lower()}")
            build_method(frame)

        # 4. Show the starting screen
        self.show_screen("Home")

        # 5. Initialize background clock ticker
        self.update_clock()

    # --- UI Helper Methods (from mambo_gui.py style) ---
    def _text(self, parent, value, size=18, color=WHITE, bold=False, **kwargs):
        return tk.Label(parent, text=value, bg=kwargs.pop('bg', BG), fg=color,
                        font=('Arial', size, 'bold' if bold else 'normal'),
                        justify='left', **kwargs)

    def _create_header_and_body(self, frame, title):
        """Clears frame content and generates the standard Mambo card layout with header and body."""
        for widget in frame.winfo_children():
            widget.destroy()

        header = tk.Frame(frame, bg=BG)
        header.pack(fill='x', padx=24, pady=(18, 10))
        self._text(header, title, 24, ACCENT, True).pack(side='left')

        # Live header clock reference
        self.time_label = self._text(header, '', 16)
        self.time_label.pack(side='right')

        body = tk.Frame(frame, bg=CARD, padx=28, pady=24)
        body.pack(fill='both', expand=True, padx=22, pady=(4, 24))
        return body

    # --- Screen Switching Function ---
    def show_screen(self, screen_name):
        """Universal screen switcher that brings the requested frame to the front"""
        if screen_name in self.frames:
            frame = self.frames[screen_name]
            frame.tkraise()
            self.active_screen = screen_name

            # Refresh data dynamically when navigating to specific views
            if screen_name == "Weather":
                self.refresh_weather()
            elif screen_name == "Calendar":
                self.refresh_calendar()
            elif screen_name == "Pills":
                self.refresh_pills()

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

    # --- 6 Screen Setup & Data Integration Functions ---
    def build_home(self, frame):
        body = self._create_header_and_body(frame, "MAMBO ASSISTANT HOME")
        self.idle_clock = self._text(body, '', 36, ACCENT, True, bg=CARD)
        self.idle_clock.pack(pady=(20, 5))
        self.idle_date = self._text(body, '', 16, MUTED, bg=CARD)
        self.idle_date.pack(pady=(0, 20))
        self._text(body, "Welcome back! Use the navigation controls or voice command 'Hey Mambo' to get started.", 15,
                   WHITE, bg=CARD, wraplength=600).pack(anchor='w')

    def build_weather(self, frame):
        body = self._create_header_and_body(frame, "TAMPA, FL | WEATHER")
        self.weather_label = self._text(body, "Loading weather data...", 20, WHITE, bg=CARD, wraplength=660,
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
        if hasattr(self, 'weather_label'):
            self.weather_label.config(text=text)

    def build_calendar(self, frame):
        body = self._create_header_and_body(frame, "UPCOMING CALENDAR")
        self.calendar_label = self._text(body, "Loading calendar events...", 16, WHITE, bg=CARD, wraplength=660,
                                         anchor='nw')
        self.calendar_label.pack(fill='both', expand=True)

    def refresh_calendar(self):
        try:
            events = get_upcoming_events(limit=5)
            if events is None:
                text = "Calendar not connected. Set MAMBO_ICS_URL or calendar.ics."
            elif not events:
                text = "No upcoming events found in the next 30 days."
            else:
                text = "\n\n".join(events)
        except Exception as e:
            text = f"Error loading calendar: {e}"
        if hasattr(self, 'calendar_label'):
            self.calendar_label.config(text=text)

    def build_pills(self, frame):
        body = self._create_header_and_body(frame, "MEDICATION SCHEDULE")

        # Day selector dropdown
        choices = tk.Frame(body, bg=CARD)
        choices.pack(fill='x', pady=(0, 15))
        self.day_choice = tk.StringVar(value=self.pill_day)
        tk.OptionMenu(choices, self.day_choice, *DAYS, command=self.on_pill_day_change).pack(anchor='w')

        self.pills_label = self._text(body, "", 18, WHITE, bg=CARD, wraplength=660, anchor='nw')
        self.pills_label.pack(fill='both', expand=True)
        self._text(body, "Demo data only — not medical instructions", 12, MUTED, bg=CARD).pack(anchor='w')

    def on_pill_day_change(self, selected_day):
        self.pill_day = selected_day
        self.refresh_pills()

    def refresh_pills(self):
        try:
            items = get_medications(self.pill_day)
            if not items:
                text = f"No medications scheduled for {self.pill_day}."
            else:
                lines = [f"• {entry.get('time', '--:--')} - {entry.get('name', 'Medication')}" for entry in items]
                text = f"Schedule for {self.pill_day}:\n\n" + "\n".join(lines)
        except Exception as e:
            text = f"Error loading schedule: {e}"
        if hasattr(self, 'pills_label'):
            self.pills_label.config(text=text)

    def build_messages(self, frame):
        body = self._create_header_and_body(frame, "MESSAGES & ALERTS")
        self.message_label = self._text(body, "No new messages.", 20, WHITE, bg=CARD, wraplength=660, anchor='nw')
        self.message_label.pack(fill='both', expand=True)

    def build_profile(self, frame):
        body = self._create_header_and_body(frame, "USER PROFILE & SETTINGS")
        self._text(body, "System Name: Mambo Smart Display\nStatus: Active & Connected\nVersion: 1.0.0", 18, WHITE,
                   bg=CARD).pack(anchor='w', pady=10)


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
if __name__ == "__main__":
    main()