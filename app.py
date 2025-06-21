from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import openai
import os
import datetime

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
openai.api_key = os.getenv("OPENAI_API_KEY")

# 全域聊天記錄，會每天中午清空
chat_messages = []

def is_today():
    return datetime.datetime.now().date()

last_reset_date = is_today()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    messages = request.json.get("messages", [])
    conversation = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in messages])

    prompt = f"""你是一位幽默但專業的心理學分析師。請根據以下對話紀錄，分析對話雙方的個性特質、溝通風格，並推測他們的互動關係與相處模式：

{conversation}

請用中文回答，語氣輕鬆但專業，不要只講重點，請用有趣的方式總結。"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一位擅長從對話分析人格與互動風格的心理學專家"},
                {"role": "user", "content": prompt}
            ]
        )
        analysis = response.choices[0].message.content.strip()
    except Exception as e:
        analysis = f"分析失敗：{str(e)}"

    return jsonify({"analysis": analysis})

@socketio.on("send_message")
def handle_send_message(data):
    global last_reset_date
    if is_today() != last_reset_date:
        chat_messages.clear()
        last_reset_date = is_today()

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    data["timestamp"] = timestamp
    chat_messages.append(data)
    emit("receive_message", data, broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
