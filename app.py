from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    messages = data.get("messages", [])
    
    prompt = "請你擔任一位個性分析師。根據以下對話紀錄，請分析雙方的性格特質，並分別用 Big Five、MBTI、依附類型、薩提爾對話模式簡要描述 A 與 B。\n\n"
    for msg in messages:
        prompt += f"{msg['sender']}: {msg['text']}\n"
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    result = response.choices[0].message.content.strip()
    return jsonify({"analysis": result})

# === WebSocket handling ===

@socketio.on("send_message")
def handle_message(data):
    sender = data.get("sender")
    text = data.get("text")
    timestamp = data.get("timestamp") or datetime.now().strftime("%H:%M")
    emit("receive_message", {"sender": sender, "text": text, "timestamp": timestamp}, broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)
