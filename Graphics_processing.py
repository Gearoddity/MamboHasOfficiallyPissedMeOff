import tkinter as tk
from datetime import datetime
import time


class MamboScreens(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Mambo Strikes")
        self.geometry("500x400")

        # 1. Main container to stack all screens on top of each other
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary to hold references to all our screen frames
        self.frames = {}

        # 2. Define the names of your 6 screens
        screen_names = ["Home", "Weather", "Pills", "Schedule", "News", "Number5"]
        # 3. Create, grid, and build each screen dynamically
        for name in screen_names:
            frame = tk.Frame(container)
            self.frames[name] = frame
            # Stack all frames in the exact same grid cell (0, 0)
            frame.grid(row=0, column=0, sticky="nsew")

            # Dynamically call the respective build function (e.g., self.build_screen1)
            build_method = getattr(self, f"build_{name.lower()}")
            build_method(frame)

        # 4. Show the starting screen (Screen 1)
        self.show_screen("Home")
        # 5. Initialize your background clock ticker
        self.update_clock()

    # --- Screen Switching Function ---
    def show_screen(self, screen_name):
        """Universal screen switcher that also tracks the active screen"""
        if screen_name in self.frames:
            # 1. Bring the requested frame to the front
            frame = self.frames[screen_name]
            frame.tkraise()

            # 2. Record it as the current active screen
            self.active_screen = screen_name

    def get_current_screen(self):
        """Returns the string name of the screen currently in front"""
        # Returns self.active_screen if set, otherwise defaults to "Unknown"
        return getattr(self, 'active_screen', "Unknown")

    # --- Clock Update Function ---
    def update_clock(self):
        """Updates the live clock label every second if it exists on the active screen"""
        current_time = datetime.now().strftime("%H:%M:%S %p")

        # Safely update only if the clock label has been rendered
        if hasattr(self, 'clock_label'):
            self.clock_label.config(text=current_time)

        # Schedule this function to run again after 1000 milliseconds (1 second)
        self.after(1000, self.update_clock)

    # --- 6 Screen Setup Functions ---
    def build_home(self, frame):
        tk.Label(frame, text="🏠 Screen 1: Home", font=("Arial", 16, "bold")).pack(pady=30)

    def build_weather(self, frame):
        tk.Label(frame, text="⏰ Screen 2: Live Clock", font=("Arial", 16, "bold")).pack(pady=20)

        # Store reference to the label so update_clock() can find it
        self.clock_label = tk.Label(frame, text="", font=("Arial", 20), fg="blue")
        self.clock_label.pack(pady=20)


    def build_pills(self, frame):
        tk.Label(frame, text="⚙️ Screen 3: Settings", font=("Arial", 16, "bold")).pack(pady=30)

    def build_schedule(self, frame):
        tk.Label(frame, text="📊 Screen 4: Analytics", font=("Arial", 16, "bold")).pack(pady=30)


    def build_news(self, frame):
        tk.Label(frame, text="💬 Screen 5: Messages", font=("Arial", 16, "bold")).pack(pady=30)


    def build_number5(self, frame):
        tk.Label(frame, text="👤 Screen 6: Profile", font=("Arial", 16, "bold")).pack(pady=30)


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