import speech_recognition as sr
import pyttsx3
import datetime

# ---------- SPEAK FUNCTION ----------
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# ---------- WISH ----------
def wish():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning")
    elif hour < 18:
        speak("Good afternoon")
    else:
        speak("Good evening")

    speak("I am your voice assistant. How can I help you?")

# ---------- TAKE COMMAND ----------
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print("You said:", query)
        return query.lower()
    except:
        print("Could not understand")
        return ""

# ---------- MAIN ----------
if __name__ == "__main__":
    wish()

    while True:
        query = take_command()

        if "time" in query:
            time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {time}")

        elif "date" in query:
            date = datetime.datetime.now().strftime("%d %B %Y")
            speak(f"Today's date is {date}")

        elif "hello" in query:
            speak("Hello Dev, nice to meet you")

        elif "exit" in query or "stop" in query:
            speak("Goodbye. Have a nice day")
            break





