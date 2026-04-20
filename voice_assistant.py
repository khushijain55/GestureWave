import random
import webbrowser
import pyttsx3
import speech_recognition as sr
import keyboard
import pyautogui
import time
from datetime import datetime
from googletrans import Translator, LANGUAGES
import wikipedia
import psutil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

translator = Translator()

# ✅ FINAL STABLE SPEAK FUNCTION
def speak(text):
    try:
        print(f"Assistant: {text}")
        time.sleep(0.2)  # small delay (VERY IMPORTANT)

        engine = pyttsx3.init('sapi5')   # fresh engine every time
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("Speech Error:", e)


# 🎤 Listen
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("\n🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)

            print("🔍 Recognizing...")
            command = recognizer.recognize_google(audio).lower()
            print(f"✅ Recognized: {command}")
            return command

        except:
            return None


# ✅ CLEAN QUERY
def clean_query(query):
    remove_words = ["what", "is", "who", "tell", "me", "about", "please", "define"]
    return " ".join([word for word in query.split() if word not in remove_words])


# 📚 IMPROVED WIKIPEDIA
def search_wikipedia(query):
    clean = clean_query(query)

    if not clean:
        speak("Please say something meaningful")
        return

    speak(f"Searching for {clean}")

    try:
        result = wikipedia.summary(clean, sentences=2)
        speak(result)
        webbrowser.open(f"https://en.wikipedia.org/wiki/{clean.replace(' ', '_')}")

    except wikipedia.DisambiguationError as e:
        try:
            result = wikipedia.summary(e.options[0], sentences=2)
            speak(result)
        except:
            speak("Could not find correct result")

    except wikipedia.PageError:
        speak("No result found")

    except:
        speak("Error in searching")


# 🌐 Translation
def voice_translate():
    speak("Which language?")
    target_language = listen()

    if not target_language:
        return

    lang_code = next((code for code, name in LANGUAGES.items()
                      if name.lower() == target_language), None)

    if not lang_code:
        speak("Language not found")
        return

    speak("Speak now")

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)

            translated = translator.translate(text, dest=lang_code).text
            speak(translated)

        except:
            speak("Error in translation")


# ▶️ YouTube
def play_youtube_video(query):
    speak(f"Playing {query} on YouTube")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")


# 🔊 Volume
def set_volume(level):
    try:
        level = max(0, min(level, 100))
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        speak(f"Volume set to {level} percent")
    except:
        speak("Volume control failed")


# 😂 Joke
def tell_joke():
    speak(random.choice([
        "Why don't skeletons fight? They don't have the guts.",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why did the scarecrow win? Because he was outstanding!"
    ]))


# 🔋 Battery
def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        speak(f"Battery is {battery.percent} percent")
    else:
        speak("Battery info not available")


# 🧠 MAIN
def main():
    speak("Hello! How can I assist you today?")

    while True:
        if keyboard.is_pressed('q'):
            speak("Goodbye!")
            break

        print("\nWaiting for command...")
        command = listen()

        if command:
            print("Processing:", command)

            if "play" in command and "youtube" in command:
                play_youtube_video(command)

            elif "translate" in command or "language" in command:
                voice_translate()

            elif "time" in command:
                speak(datetime.now().strftime("%I:%M %p"))

            elif "date" in command:
                speak(datetime.now().strftime("%A, %B %d, %Y"))

            elif "joke" in command:
                tell_joke()

            elif "battery" in command:
                get_battery_status()

            elif "volume" in command:
                digits = ''.join(filter(str.isdigit, command))
                if digits:
                    set_volume(int(digits))
                else:
                    speak("Tell volume level")

            elif "exit" in command or "quit" in command or "goodbye" in command:
                speak("Goodbye!")
                break

            else:
                search_wikipedia(command)

        time.sleep(1)


if __name__ == "__main__":
    main()