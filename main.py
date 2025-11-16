from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        user_text = (request.args.get("text") or "").strip()
    else:
        if request.is_json:
            data = request.get_json(silent=True) or {}
            user_text = (data.get("text") or "").strip()
        else:
            user_text = (request.form.get("text") or "").strip()

    if not user_text:
        if request.method == "POST" and not request.is_json:
            return render_template_string(HTML_PAGE, user_text="", reply="Хоосон текст байна."), 400
        return jsonify({"error": "Хоосон текст ирсэн байна."}), 400

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are HASH AI Assistant for Buysmart, Shuurkhai, Hash Motors. Always reply in Mongolian."
                },
                {"role": "user", "content": user_text},
            ],
        )

        reply_text = completion.choices[0].message["content"]

    except Exception as e:
        error_msg = f"OpenAI алдаа: {e}"
        print(error_msg, flush=True)

        if request.method == "POST" and not request.is_json:
            return render_template_string(HTML_PAGE, user_text=user_text, reply=error_msg), 500
        return jsonify({"error": error_msg}), 500

    if request.method == "POST" and not request.is_json:
        return render_template_string(HTML_PAGE, user_text=user_text, reply=reply_text)

    return jsonify({"reply": reply_text})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
