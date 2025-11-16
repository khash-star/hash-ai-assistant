from flask import Flask, request, jsonify, render_template_string
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Жижиг HTML форм (үндсэн хуудас)
HTML_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>HASH AI Assistant</title>
</head>
<body>
  <h1>HASH AI Assistant</h1>
  <form method="post" action="/chat">
    <textarea name="text" rows="5" cols="60">{{ user_text }}</textarea><br>
    <button type="submit">Илгээх</button>
  </form>
  {% if reply %}
    <h3>Хариу:</h3>
    <pre>{{ reply }}</pre>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE, user_text="", reply=None)

# ⬇️ ЭНЭ ХЭСЭГ НЬ ХУУЧИН /chat route-ЫГ ОРЛОХ ШИНЭ ХУВИЛБАР ⬇️
@app.route("/chat", methods=["GET", "POST"])
def chat():
    # 1) text авах (GET эсвэл POST байна)
    if request.method == "GET":
        user_text = (request.args.get("text") or "").trim()
    else:
        if request.is_json:
            data = request.get_json(silent=True) or {}
            user_text = (data.get("text") or "").strip()
        else:
            user_text = (request.form.get("text") or "").strip()

    if not user_text:
        # form-оор ирсэн хоосон бол буцаад хуудсыг нь харуулна
        if request.method == "POST" and not request.is_json:
            return render_template_string(HTML_PAGE, user_text="", reply="Хоосон текст байна.")
        return jsonify({"error": "Хоосон текст ирсэн байна."}), 400

    # 2) OpenAI руу асуулт явуулах
    try:
        completion = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are HASH AI assistant for Buysmart, Shuurkhai, Hash Motors."},
                {"role": "user", "content": user_text},
            ],
        )
        reply_text = completion.choices[0].message.content
    except Exception as e:
        # quota / түлхүүрийн алдаа г.м.
        error_msg = f"OpenAI алдаа: {e}"
        if request.method == "POST" and not request.is_json:
            return render_template_string(HTML_PAGE, user_text=user_text, reply=error_msg), 500
        return jsonify({"error": error_msg}), 500

    # 3) Form-оор ирсэн бол HTML дээр харуулна, JSON бол JSON буцаана
    if request.method == "POST" and not request.is_json:
        return render_template_string(HTML_PAGE, user_text=user_text, reply=reply_text)
    return jsonify({"reply": reply_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
