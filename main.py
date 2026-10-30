
import queue
import threading
import tkinter as tk

from voice_listener import SimpleListener
from Active_Variable import wake
from Graphics_processing import MamboScreens


def main():

    mambo = MamboScreens()
    wake_word = wake()
    command_queue = queue.Queue()

    def handle_spoken_text(text):
        print(f"[MAIN RECEIVED]: {text}")
        text = text.lower().strip()

        if "main" in text or "mambo" in text:
            wake_word.active_timer()
            command_queue.put("Home")

        if "weather" in text or "whether" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("Weather")

        elif "pills" in text or "hills" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("Pills")

        elif "news" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("News")

        elif "schedule" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("Schedule")

        elif "number five" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("Number5")

    listener = SimpleListener(
        model_path="model",
        callback=handle_spoken_text
    )

    def process_commands():
        # Update the UI on-screen listening indicator based on the wake variable
        mambo.set_wake_status(wake_word.check_active())

        try:
            while True:
                screen = command_queue.get_nowait()
                if mambo.get_current_screen() != screen:
                    mambo.show_screen(screen)
        except queue.Empty:
            pass

        if mambo.winfo_exists():
            mambo.after(100, process_commands)

    # Start polling on Tkinter's main thread.
    mambo.after(100, process_commands)

    # Start listening in the background.
    listener_thread = threading.Thread(
        target=listener.start,
        daemon=True
    )
    listener_thread.start()

    # Keep Tkinter on the main thread.
    try:
        mambo.mainloop()
    finally:
        listener.stop()


if __name__ == "__main__":
    main()
