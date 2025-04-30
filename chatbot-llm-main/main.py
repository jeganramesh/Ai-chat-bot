from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import json
import dotenv
import requests
from gtts import gTTS

dotenv.load_dotenv()

app = Flask(__name__)

# ✅ Replace with your actual Gemini API key
GEMINI_API_KEY = "AIzaSyCitsYctNp0B4eSz1xg-j80PrK9NnktvVY"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Ensure the "temp" folder exists for audio generation
os.makedirs("temp", exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


def clean_temp_directory():
    """Clears temporary audio files."""
    for filename in os.listdir("temp"):
        file_path = os.path.join("temp", filename)
        os.remove(file_path)


def get_chat_response(user_input):
    """Sends user input to Gemini API and returns the response."""
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user_input}
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raises an error for HTTP failures

        print("Gemini API Response:", response.json())  # ✅ Debugging

        data = response.json()

        # ✅ Ensure proper response parsing
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0].get("text", "No response received.")
        else:
            return "No response received."
    
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Gemini API: {e}"


def generate_audio_response(response_text):
    """Converts response text to audio and returns the file path."""
    audio_file = f"temp/{uuid.uuid4()}.mp3"
    tts = gTTS(response_text)
    tts.save(audio_file)
    return f"/audio-response/{os.path.basename(audio_file)}"


@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot responses and optional audio generation."""
    data = request.get_json()
    user_input = data.get("message")
    use_audio_response = data.get("audio_response", False)

    chat_response_content = get_chat_response(user_input)

    response_data = {}
    if chat_response_content.startswith("{"):
        try:
            json_response = json.loads(chat_response_content)
            response_data["response_html"] = json_response.get("response_html", chat_response_content)
            response_data["response_text"] = json_response.get("response_text", chat_response_content)
        except json.JSONDecodeError:
            response_data["response_html"] = chat_response_content
            response_data["response_text"] = chat_response_content
    else:
        response_data["response_html"] = chat_response_content
        response_data["response_text"] = chat_response_content

    is_html = "<html>" in response_data["response_html"]

    response = {
        "response_html": response_data["response_html"],
        "response_text": response_data["response_text"],
        "is_html": is_html,
    }

    if use_audio_response:
        response["audio_url"] = generate_audio_response(response_data["response_text"])

    return jsonify(response)


@app.route("/audio-response/<filename>", methods=["GET"])
def audio_response(filename):
    """Sends generated audio files to the user."""
    return send_file(f"temp/{filename}", mimetype="audio/mpeg")


if __name__ == "__main__":
    clean_temp_directory()
    app.run(host="0.0.0.0", port=5041, debug=False)
