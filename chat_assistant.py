import webbrowser
import datetime
import psutil
import screen_brightness_control as sbc
import re

def get_chat_response(user_message):
    user_message = user_message.lower().strip()

    # ---------------- BASIC ----------------
    if any(word in user_message for word in ["hello", "hi", "hey"]):
        return {"response": "Hello! How can I help you? 😊", "redirect": None}

    # Define a list of common ways people ask "How are you?"
    greetings = ["how are you", "how's it going", "how are things", "how do you do", "how r u"]
    # Convert message to lowercase to catch "How are you" or "HOW ARE YOU"
    msg = user_message.lower()
    if any(phrase in msg for phrase in greetings):
        return {"response": "I'm doing great! 🚀 How are you?", "redirect": None}
    
    identity_questions = ["who are you", "what is your name", "how do i address you", "your name"]
    # Use any() to check if any of the phrases are in the message
    if any(question in user_message.lower() for question in identity_questions):
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
    if "brightness" in user_message.lower():
        try:
            msg = user_message.lower()
            current = sbc.get_brightness()[0]
        
        # Check for a number in the message (e.g., "90", "70%")
            match = re.search(r"(\d+)", msg)
        
            if match:
            # Extract the number and clamp it between 0 and 100
               target = max(0, min(100, int(match.group(1))))
               sbc.set_brightness(target)
               return {"response": f"Brightness set to {target}%", "redirect": None}
            
            elif "increase" in msg:
               new = min(100, current + 10)
               sbc.set_brightness(new)
               return {"response": f"Brightness increased to {new}%", "redirect": None}
            
            elif "decrease" in msg:
               new = max(0, current - 10)
               sbc.set_brightness(new)
               return {"response": f"Brightness decreased to {new}%", "redirect": None}
            
            else:
               return {"response": "You can say 'increase brightness', 'decrease', or 'set brightness to 80%'.", "redirect": None}
            
        except Exception:
            return {"response": "Brightness control not supported on this device.", "redirect": None}

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