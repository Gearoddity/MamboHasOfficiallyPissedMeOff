import queue
import threading
import tkinter as tk
from datetime import datetime
from voice_listener import SimpleListener
from Active_Variable import wake
from Graphics_processing import MamboScreens
from tts_manager import speak_text
import news_manager
from weather_manager import get_weather
from medication_manager import get_medications, DAYS as PULL_DAYS
from calendar_manager import get_upcoming_events
from news_manager import get_news

def main():
    mambo = MamboScreens()
    wake_word = wake()
    command_queue = queue.Queue()

    def handle_spoken_text(text):
        print(f"[MAIN RECEIVED]: {text}")
        text = text.lower().strip()

        if text in ["mambo", "hey mambo"]:
            mambo.play_wake_audio()

        if "main" in text or "mambo" in text:
            wake_word.active_timer()
            command_queue.put("Home")

        if "weather" in text or "whether" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("Weather")

                # Fetch data and speak it in a background thread
                def speak_weather_thread():
                    try:
                        data = get_weather()
                        spoken_phrase = (
                            f"The current temperature is {data.get('temperature')} degrees Fahrenheit "
                            f"with {data.get('condition')}. Humidity is at {data.get('humidity')} percent."
                        )
                        speak_text(spoken_phrase)
                    except Exception as e:
                        speak_text("Sorry, I couldn't load the weather details right now.")

                threading.Thread(target=speak_weather_thread, daemon=True).start()

        elif "pills" in text or "hills" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("Pills")

                def speak_pills_thread():
                    try:
                        current_day = datetime.now().strftime('%A')
                        items = get_medications(current_day)
                        if not items:
                            speak_text(f"You have no medications scheduled for today, {current_day}.")
                        else:
                            med_names = ", ".join([entry.get('name', 'Medication') for entry in items])
                            speak_text(f"For today, {current_day}, your scheduled medications include: {med_names}.")
                    except Exception as e:
                        speak_text("Error loading your medication schedule.")

                threading.Thread(target=speak_pills_thread, daemon=True).start()

        elif "news" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("News")

                def speak_news_thread():
                    try:
                        headlines = get_news(limit=2)  # Keep it concise for spoken output
                        if headlines:
                            news_speech = "Here are the top headlines: " + ". ".join(headlines)
                            speak_text(news_speech)
                        else:
                            speak_text("No top headlines are available right now.")
                    except Exception as e:
                        speak_text("Could not load the news feed.")

                threading.Thread(target=speak_news_thread, daemon=True).start()


        elif "schedule" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("Schedule")
                def speak_schedule_thread():
                    try:
                        events = get_upcoming_events(limit=3)  # Limit to 3 items for concise speech
                        if events is None:
                            speak_text("Calendar feed is not connected.")
                        elif not events:
                            speak_text("You have no upcoming events found in the next 30 days.")
                        else:
                            # Clean up event formatting slightly for a smoother text-to-speech read
                            schedule_speech = "Here are your upcoming events: " + ". ".join(events)
                            speak_text(schedule_speech)
                    except Exception as e:
                        speak_text("Error loading your schedule.")
                threading.Thread(target=speak_schedule_thread, daemon=True).start()

        elif "number five" in text:
            if wake_word.check_active():
                wake_word.force_stop()
                command_queue.put("Number5")

        elif "stop" in text or "pause" in text:
            if wake_word.check_active():
                mambo.stop_mambo_audio()
                mambo.show_screen("Home")
        else:
            if wake_word.check_active() and "mambo" not in text:
                speak_text("Sorry, I didn't catch that")

    # Clean lambda wrapper so SimpleListener passes text into our scoped function
    listener = SimpleListener(
        model_path="model",
        callback=lambda text: handle_spoken_text(text)
    )

    def process_commands():
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