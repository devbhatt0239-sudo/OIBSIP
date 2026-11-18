"""Speech input/output helpers for macOS and other desktop platforms."""
import platform
import subprocess
import speech_recognition as sr
import pyttsx3


class VoiceEngine:
    def __init__(self, rate: int = 170, language: str = "en-IN"):
        self.rate = rate
        self.language = language
        self.recognizer = sr.Recognizer()

    def speak(self, text: str) -> None:
        print(f"Assistant: {text}")
        if platform.system() == "Darwin":
            subprocess.run(["say", "-r", str(self.rate), text], check=True)
            return
        engine = pyttsx3.init()
        engine.setProperty("rate", self.rate)
        engine.say(text)
        engine.runAndWait()
        engine.stop()

    def listen(self, timeout: int = 5, phrase_time_limit: int = 12) -> str:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"You: {text}")
            return text.strip()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as exc:
            return f"__ERROR__:Speech recognition service unavailable: {exc}"
        except (OSError, AttributeError) as exc:
            return f"__ERROR__:Microphone problem: {exc}"
