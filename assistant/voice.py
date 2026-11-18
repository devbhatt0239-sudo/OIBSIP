
import speech_recognition as sr
import subprocess
import platform
import pyttsx3


class VoiceEngine:
    def __init__(self, rate: int = 170, language: str = "en-IN"):
        self.rate = rate
        self.language = language
        self.recognizer = sr.Recognizer()

    def speak(self, text: str) -> None:
        print(f"Assistant: {text}")

        if platform.system() == "Darwin":
            words_per_minute = self.rate
            subprocess.run(
                ["say", "-r", str(words_per_minute), text],
                check=True
            )
        else:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.say(text)
            engine.runAndWait()
            engine.stop()

    def listen(self, timeout: int = 5, phrase_time_limit: int = 12) -> str:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(
                    source, duration=0.5
                )
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            print("Recognizing...")
            text = self.recognizer.recognize_google(
                audio, language=self.language
            )
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
