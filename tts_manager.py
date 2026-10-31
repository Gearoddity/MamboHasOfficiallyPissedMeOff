import pyttsx3
import threading

class TTSManager:
    def __init__(self):
        # Initialize the speech engine once
        try:
            self.engine = pyttsx3.init()
            # Optional: adjust rate (speed) and volume
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 1.0)
        except Exception as e:
            print(f"[TTS] Initialization error: {e}")
            self.engine = None

    def _speak_task(self, text):
        """Internal synchronous speech method run inside a worker thread."""
        if not self.engine:
            return
        try:
            # Note: pyttsx3 engine calls need to be thread-safe or re-initialized
            # if used across multiple concurrent threads, so we lock/re-init per utterance
            # for maximum stability on multi-threaded assistants.
            local_engine = pyttsx3.init()
            local_engine.say(text)
            local_engine.runAndWait()
        except Exception as e:
            print(f"[TTS] Error during speech output: {e}")

    def speak(self, text):
        """Asynchronously speaks text in the background without freezing the UI or listener."""
        if not text:
            return
        print(f"[TTS Speaking]: {text}")
        # Run speech in a background daemon thread
        threading.Thread(target=self._speak_task, args=(text,), daemon=True).strart() if hasattr(threading.Thread(target=self._speak_task, args=(text,), daemon=True), 'strart') else threading.Thread(target=self._speak_task, args=(text,), daemon=True).start()

# Global singleton instance for easy import
_tts = TTSManager()

def speak_text(text):
    _tts.speak(text)