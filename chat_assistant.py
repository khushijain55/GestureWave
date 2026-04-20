import webbrowser
import datetime
import psutil
import screen_brightness_control as sbc

def get_chat_response(user_message):
    user_message = user_message.lower().strip()

    # ---------------- BASIC ----------------
    if any(word in user_message for word in ["hello", "hi", "hey"]):
        return {"response": "Hello! How can I help you? 😊", "redirect": None}

    if "how are you" in user_message:
        return {"response": "I'm doing great! 🚀 How are you?", "redirect": None}
    
    if "who are you" in user_message:
        return {"response": "I'm a chat bot. You can call me Waver.", "redirect": None}
    
    if "who built you" in user_message:
        return {"response": "I was built by a group of students : Khushi Jain, Tanmay Shete, Nihar Bhirwadkar and Dhruv Dodia.", "redirect": None}

    # ---------------- TIME ----------------
    if "time" in user_message:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return {"response": f"The current time is {now}.", "redirect": None}

    # ---------------- BATTERY ----------------
    if any(word in user_message for word in ["battery", "charge", "power"]):
        battery = psutil.sensors_battery()
        if battery:
            return {"response": f"Battery is at {battery.percent}%", "redirect": None}
        return {"response": "Battery info not available.", "redirect": None}

    # ---------------- BRIGHTNESS ----------------
    if "brightness" in user_message:
        try:
            current = sbc.get_brightness()[0]
            if "increase" in user_message:
                new = min(100, current + 10)
                sbc.set_brightness(new)
                return {"response": f"Brightness increased to {new}%", "redirect": None}
            elif "decrease" in user_message:
                new = max(0, current - 10)
                sbc.set_brightness(new)
                return {"response": f"Brightness decreased to {new}%", "redirect": None}
            else:
                return {"response": "Say increase or decrease brightness.", "redirect": None}
        except:
            return {"response": "Brightness control not supported.", "redirect": None}

    # ---------------- GOOGLE SEARCH ----------------
    if "search" in user_message or "google" in user_message:
        query = user_message.replace("search", "").replace("google", "").strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return {"response": f"Searching Google for {query}...", "redirect": None}
        return {"response": "What do you want to search?", "redirect": None}

    # ---------------- WIKIPEDIA STYLE ----------------
    if any(word in user_message for word in ["who is", "what is", "tell me about"]):
        topic = user_message.replace("who is", "").replace("what is", "").replace("tell me about", "").strip()
        if topic:
            webbrowser.open(f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}")
            return {"response": f"Here is information about {topic}.", "redirect": None}
        return {"response": "Please tell me the topic.", "redirect": None}

    # ---------------- NAVIGATION ----------------
    if "virtual mouse" in user_message:
        return {"response": "Opening Virtual Mouse...", "redirect": "/virtual_mouse"}

    if "virtual keyboard" in user_message:
        return {"response": "Opening Virtual Keyboard...", "redirect": "/virtual_keyboard"}

    if "voice assistant" in user_message:
        return {"response": "Opening Voice Assistant...", "redirect": "/voice_assistant"}

    # ---------------- DEFAULT ----------------
    return {"response": "Get lost.", "redirect": None}