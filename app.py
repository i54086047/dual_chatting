from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import os
import json

from openai import OpenAI  # ✅ 新版 SDK

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

client = OpenAI(api_key=OPENAI_API_KEY)  # ✅ 新版 SDK 使用 client 物件

# ===== 儲存聊天紀錄用（部署後可換成資料庫）=====
CHAT_LOG_FILE = "chat_log.json"

def save_chat(messages):
    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False)

def load_chat():
    if os.path.exists(CHAT_LOG_FILE):
        with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ===== 路由區 =====
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/load_chat")
def load_chat_route():
    messages = load_chat()
    return jsonify({"messages": messages})

@app.route("/analyze", methods=["POST"])
def analyze():
    messages = request.json.get("messages", [])

    # 轉換為 GPT 所需格式
    chat_log = [{"role": "user", "content": f"{msg['sender']}: {msg['text']}"} for msg in messages]
    prompt = [
        {"role": "system", "content": "你是一位聊天分析師，擅長根據對話紀錄分析兩位使用者的性格特質與相處風格，請用有趣且生動的語氣說明他們是什麼樣的組合角色。"},
        *chat_log
    ]

    # ✅ 使用新版 SDK 呼叫 chat
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0.7
    )

    summary = response.choices[0].message.content.strip()
    return jsonify({"analysis": summary})

# ===== SocketIO 區 =====
@socketio.on("send_message")
def handle_send_message(data):
    sender = data["sender"]
    text = data["text"]
    timestamp = datetime.now().strftime("%H:%M:%S")
    message = {"sender": sender, "text": text, "timestamp": timestamp}

    # 廣播訊息
    emit("receive_message", message, broadcast=True)

    # 儲存聊天紀錄
    chat = load_chat()
    chat.append(message)
    save_chat(chat)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)
