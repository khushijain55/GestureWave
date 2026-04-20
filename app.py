import subprocess
import os
import signal
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from chat_assistant import get_chat_response
import bcrypt
from pymongo import MongoClient
import cv2

# ------------------- Flask App Configuration -------------------
app = Flask(__name__)
app.secret_key = "YourSecretKey"

print("✅ Flask app is starting...")

# ------------------- MongoDB Connection -------------------
MONGO_URL = "mongodb://localhost:27017"

try:
    client = MongoClient(MONGO_URL)
    db = client['total_records']
    records = db['register']
    print("✅ MongoDB connected successfully")
except Exception as e:
    print("❌ MongoDB connection failed:", str(e))

# ------------------- Load Haar Cascade Safely -------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ------------------- Face Detection Logic -------------------
def detect_face():
    """Accurately detect a face using OpenCV."""
    cap = cv2.VideoCapture(0)  # FIXED CAMERA INDEX
    detected = False

    if not cap.isOpened():
        print("❌ Camera not accessible")
        return False

    while not detected:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read camera frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(80, 80))

        for (x, y, w, h) in faces:
            aspect_ratio = w / float(h)

            if 0.75 < aspect_ratio < 1.3 and w > 80 and h > 80:
                detected = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, "Face Detected!", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return detected

# ------------------- Routes -------------------

@app.route("/", methods=["GET", "POST"])
def face_detection():
    message = ""
    if request.method == "POST":
        if detect_face():
            return redirect(url_for("register"))
        else:
            message = "Face not detected. Please try again."
    return render_template("face_detection.html", message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    if "email" in session:
        return redirect(url_for("dashboard"))

    message = ""
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        password1 = request.form.get("password1", "")
        password2 = request.form.get("password2", "")

        if not name.strip():
            message = "Full name is required."
        elif password1 != password2:
            message = "Passwords must match."
        elif records.find_one({"email": email}):
            message = "Email already exists."
        else:
            hashed = bcrypt.hashpw(password2.encode("utf-8"), bcrypt.gensalt())
            records.insert_one({"name": name, "email": email, "password": hashed})
            session["email"] = email
            session["name"] = name
            return redirect(url_for("dashboard"))

    return render_template("register.html", message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "email" in session:
        return redirect(url_for("dashboard"))

    message = ""
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        email_found = records.find_one({"email": email})

        if email_found and bcrypt.checkpw(password.encode("utf-8"), email_found["password"]):
            session["email"] = email
            session["name"] = email_found.get("name", "User")
            return redirect(url_for("dashboard"))
        else:
            message = "Invalid credentials. Please try again."

    return render_template("login.html", message=message)


@app.route("/dashboard")
def dashboard():
    if "email" in session:
        name = session.get("name", "User")
        return render_template("dashboard.html", name=name)
    return redirect(url_for("login"))


@app.route("/voice_assistant_base", methods=["GET", "POST"])
def voice_assistant_base():
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template("voice_assistant_base.html")


# ------------------- Voice Assistant Process Control -------------------

process = None

@app.route("/voice_assistant", methods=["GET", "POST"])
def voice_assistant():
    global process

    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        script_path = os.path.join(os.getcwd(), "voice_assistant.py")

        if request.form.get("start") == "true":
            if process is None or process.poll() is not None:
                process = subprocess.Popen(["python", script_path])
                flash("✅ Voice Assistant started", "success")
            else:
                flash("⚠️ Voice Assistant already running", "info")

        elif request.form.get("stop") == "true":
            if process and process.poll() is None:
                os.kill(process.pid, signal.SIGTERM)
                process = None
                flash("🛑 Voice Assistant stopped", "warning")
            else:
                flash("⚠️ Voice Assistant not running", "info")

        return redirect(url_for("voice_assistant"))

    return render_template("voice_assistant.html")


# ------------------- Chat Assistant -------------------

@app.route("/chat_assistant")
def chat_assistant():
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template("chat_assistant.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    if not user_message:
        return jsonify({"response": "Please enter a message.", "redirect": None})

    try:
        from chat_assistant import get_chat_response
        reply = get_chat_response(user_message)

        print("User:", user_message)
        print("Bot:", reply)

        return jsonify(reply)

    except Exception as e:
        print("Chat Error:", e)
        return jsonify({
            "response": "Chat assistant is currently unavailable.",
            "redirect": None
        })



# ------------------- Modes -------------------

@app.route("/virtual_mouse")
def virtual_mouse():
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template("virtual_mouse.html")


@app.route("/presentation_mode", methods=["GET", "POST"])
def presentation_mode():
    if "email" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        try:
            subprocess.Popen(["python", "presentation.py"])
            message = "✅ Presentation Mode Activated!"
        except Exception as e:
            message = f"❌ Error: {str(e)}"

    return render_template("presentation_mode.html", message=message)


@app.route("/gaming_mode", methods=["GET", "POST"])
def gaming_mode():
    if "email" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        try:
            subprocess.Popen(["python", "game.py"])

            game_path = r"C:\Users\kajol jewellers\OneDrive\Desktop\Subway Surf.lnk"
            subprocess.Popen([game_path], shell=True)

            message = "✅ Gaming Mode Activated!"
        except Exception as e:
            message = f"❌ Error: {str(e)}"

    return render_template("gaming_mode.html", message=message)


@app.route("/basic_mode", methods=["GET", "POST"])
def basic_mode():
    if "email" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        try:
            subprocess.Popen(["python", "basic.py"])
            message = "✅ Basic Mode Activated!"
        except Exception as e:
            message = f"❌ Error: {str(e)}"

    return render_template("basic_mode.html", message=message)


@app.route("/virtual_keyboard", methods=["GET", "POST"])
def virtual_keyboard():
    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("start") == "true":
        try:
            subprocess.Popen(["python", "virtual_keyboard.py"])
            session["message"] = "✅ Virtual Keyboard Activated!"
        except Exception as e:
            session["message"] = f"❌ Error: {str(e)}"
        return redirect(url_for("virtual_keyboard"))

    message = session.pop("message", "")
    return render_template("virtual_keyboard.html", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ------------------- Start Server -------------------
if __name__ == "__main__":
    print("🚀 Starting Flask server…")
    app.run(debug=True, use_reloader=False)
