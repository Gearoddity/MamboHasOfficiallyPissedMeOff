import os
import json
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer


class SimpleListener:
    def __init__(self, model_path="model", callback=None):
        self.model_path = model_path
        self.callback = callback
        self.is_running = False

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Error: '{self.model_path}' folder not found. Make sure your Vosk model is here.")

        print("Loading model...")
        self.model = Model(self.model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)

        self.stream = None

    def start(self):
        """Starts the microphone stream and listening loop using sounddevice."""
        self.is_running = True
        print("\n--- LISTENING --- (Speak into your mic, press Ctrl+C to exit)")

        try:
            with sd.RawInputStream(samplerate=48000, blocksize=8000, dtype='int16',
                                   channels=1) as self.stream:
                while self.is_running:
                    # Read raw data (1600 frames at 48kHz)
                    data, overflow = self.stream.read(1600)

                    # Convert raw buffer to numpy array of 16-bit integers
                    audio_data = np.frombuffer(data, dtype=np.int16)

                    # Downsample from 48kHz to 16kHz by taking every 3rd sample (48000 / 16000 = 3)
                    resampled = audio_data[::3]

                    # Convert back to bytes for Vosk
                    data_bytes = resampled.tobytes()

                    if self.recognizer.AcceptWaveform(data_bytes):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").strip()

                        if text:
                            if self.callback:
                                self.callback(text)
                            else:
                                print(f"Heard (no callback): {text}")

        except Exception as e:
            if self.is_running:  # Only print if it wasn't an intentional shutdown
                print(f"Error: {e}")
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        if self.stream:
            try:
                self.stream.abort()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        print("Listener stopped.")