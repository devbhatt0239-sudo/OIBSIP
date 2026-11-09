import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import ast
import operator
from urllib.parse import quote_plus

def speak(text):
    print("Assistant is saying:", text)

    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def wish():
    hour = datetime.datetime.now().hour

    if hour < 12:
        speak("Good morning")
    elif hour < 18:
        speak("Good afternoon")
    else:
        speak("Good evening")

    speak("I am your voice assistant. How can I help you?")

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

    except sr.UnknownValueError:
        print("Could not understand")
        return ""

    except sr.RequestError:
        print("Speech recognition service is unavailable")
        return ""



def calculate(expression):
    expression = expression.lower()

    replacements = {
        "multiplied by": "*",
        "multiply by": "*",
        "times": "*",
        "divided by": "/",
        "divide by": "/",
        "plus": "+",
        "minus": "-",
        "modulus": "%",
        "power": "**"
    }

    for word, symbol in replacements.items():
        expression = expression.replace(word, symbol)

    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos
    }

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        elif isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        elif isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
            return allowed_operators[type(node.op)](
                evaluate(node.left),
                evaluate(node.right)
            )

        elif isinstance(node, ast.UnaryOp) and type(node.op) in allowed_operators:
            return allowed_operators[type(node.op)](evaluate(node.operand))

        else:
            raise ValueError("Invalid calculation")

    try:
        tree = ast.parse(expression, mode="eval")
        result = evaluate(tree)
        speak(f"The answer is {result}")

    except Exception:
        speak("Sorry, I could not calculate that expression.")



def save_note(note):
    with open("notes.txt", "a") as file:
        file.write(note + "\n")

    speak("Your note has been saved successfully.")


# ---------- SHOW NOTES ----------

def show_notes():
    try:
        with open("notes.txt", "r") as file:
            notes = file.read()

        if notes.strip():
            print("Your saved notes:")
            print(notes)
            speak("Here are your saved notes. Please check the terminal.")
        else:
            speak("You have no saved notes.")

    except FileNotFoundError:
        speak("You have no saved notes yet.")


if __name__ == "__main__":

    wish()

    while True:

        query = take_command()

        if "time" in query:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {current_time}")

        elif "date" in query:
            current_date = datetime.datetime.now().strftime("%d %B %Y")
            speak(f"Today's date is {current_date}")

        elif "hello" in query:
            speak("Hello Dev, nice to meet you")

        elif "how are you" in query or "how r u" in query:
            speak("I am fine. Thank you for asking.")

        elif "thank you" in query or "thanks" in query or "thank u" in query:
            speak("You're welcome. Happy to help.")

        
        elif "calculate" in query or "what is" in query and any(
            word in query for word in ["plus", "minus", "times", "divided", "+", "-", "*", "/"]
        ):
            expression = query.replace("calculate", "", 1).strip()
            if expression.startswith("what is"):
                expression = expression.replace("what is", "", 1).strip()
            calculate(expression)

        # SAVE NOTES
        elif query.startswith("remember"):
            note = query.replace("remember", "", 1).strip()
            if note:
                save_note(note)
            else:
                speak("Please tell me what you want me to remember.")

        elif query.startswith("save note"):
            note = query.replace("save note", "", 1).strip()
            if note:
                save_note(note)
            else:
                speak("Please tell me what note you want to save.")

        elif "show notes" in query or "read my notes" in query:
            show_notes()

        
        elif "wikipedia" in query:
            search_query = query.replace("wikipedia", "", 1).strip()

            if search_query:
                speak("Searching Wikipedia for " + search_query)
                url = "https://en.wikipedia.org/w/index.php?search=" + quote_plus(search_query)
                webbrowser.open(url)
            else:
                speak("What would you like to search on Wikipedia?")

        elif "search" in query:
            search_query = query.split("search", 1)[1].strip()

            if search_query.startswith("for "):
                search_query = search_query[4:]
            elif search_query.startswith("about "):
                search_query = search_query[6:]

            if search_query:
                speak("Searching Google for " + search_query)
                url = "https://www.google.com/search?q=" + quote_plus(search_query)
                webbrowser.open(url)
            else:
                speak("What would you like me to search?")


        elif "exit" in query or "stop" in query:
            speak("Goodbye. Have a nice day")
            break

        elif query != "":
            speak("Sorry, I did not understand")
