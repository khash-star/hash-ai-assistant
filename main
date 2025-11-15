from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "HASH AI Assistant is running"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_text = data.get("text", "")

    if not user_text:
        return jsonify({"reply": "Хоосон текст ирлээ."})

    reply = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are HASH AI assistant for Buysmart, Shuurkhai, Hash Motors."},
            {"role": "user", "content": user_text}
        ]
    )

    return jsonify({"reply": reply.choices[0].message["content"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
