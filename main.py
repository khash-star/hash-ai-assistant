from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os

app = Flask(__name__)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

HTML_FORM = """
<!doctype html>
<html>
  <head><meta charset="utf-8"><title>HASH AI Assistant</title></head>
  <body>
    <h1>HASH AI Assistant</h1>
    <form action="/chat" method="post">
      <textarea name="text" rows="6" cols="60">{{ user_text }}</textarea><br>
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
def index():
    return render_template_string(HTML_FORM, user_text="", reply="")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    # 1) text авч авах
    if request.method == "POST":
        user_text = (request.form.get("text") or "").strip()
    else:
        user_text = (request.args.get("text") or "").strip()

    if not user_text:
        # Хоосон бол шууд HTML / JSON буцаагаад дуусгая
        if request.method == "POST" and request.is_json:
            return jsonify({"error": "Хоосон текст ирлээ."}), 400
        return render_template_string(HTML_FORM, user_text="", reply="Хоосон текст ирлээ.")

    # 2) OpenAI-руу хүсэлт
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are HASH AI assistant for Buysmart, Shuurkhai, Hash Motors."
            },
            {"role": "user", "content": user_text},
        ],
    )

    reply_text = completion.choices[0].message.content

    # 3) Хэрвээ JSON POST бол JSON, бусад үед HTML буцаая
    if request.method == "POST" and request.is_json:
        return jsonify({"reply": reply_text})

    return render_template_string(HTML_FORM, user_text=user_text, reply=reply_text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
