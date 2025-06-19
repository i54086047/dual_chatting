from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import openai
import os
from dotenv import load_dotenv

# === 載入 API 金鑰 ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === 建立 Flask app 與 SocketIO ===
app = Flask(__name__)
socketio = SocketIO(app)

# === 路由：首頁 ===
@app.route('/')
def index():
    return render_template('index.html')

# === 路由：分析對話 ===
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"analysis": "⚠️ 尚未輸入對話內容。"})

    # 格式轉換為 GPT 對話格式
    chat_history = "\n".join(f"{msg['sender']}: {msg['text']}" for msg in messages)

    prompt = f"""
你是一位心理分析師。根據以下對話紀錄，請分析 A 與 B 的性格特質，以及他們之間的互動風格，最後請給予一句有趣的總結或比喻。

對話紀錄：
{chat_history}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        analysis = response['choices'][0]['message']['content'].strip()
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"analysis": f"❌ 發生錯誤：{str(e)}"})

# === SocketIO: 接收訊息並廣播 ===
@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

# === 主程式入口點 ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)

