from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

# Flask 應用程式
app = Flask(__name__)

# 初始化 OpenAI 客戶端（新版）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/analyze', methods=["POST"])
def analyze():
    data = request.get_json()
    messages = data.get("messages", [])

    # 將 A/B 對話轉為文字格式
    chat_log = "\n".join([f"{m['sender']}: {m['text']}" for m in messages])

    # 呼叫 GPT 分析對話
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "你是一位心理分析師，根據雙方對話，請分別分析以下人格類型：Big Five、依附關係類型、薩提爾對話模式與 MBTI。請簡短分析每位使用者的特徵。"
            },
            {
                "role": "user",
                "content": f"以下是 A 與 B 的對話：\n{chat_log}"
            }
        ],
        temperature=0.7
    )

    result = response.choices[0].message.content
    return jsonify({"analysis": result})

if __name__ == '__main__':
    print("✅ Flask server is starting... Please open your browser and go to http://127.0.0.1:5000")
    app.run(debug=True)
