from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os

app = Flask(__name__)

# OpenAI client (шинэ SDK)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Small HTML page for browser testing
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
  {% if error %}
    <h3>Алдаа:</h3>
    <pre>{{ error }}</pre>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE, user_text="", reply=None, error=None)

# Support both JSON (webhooks) and HTML form usage
@app.route("/chat", methods=["GET", "POST"])
def chat():
    # 1) Get text (from GET args or POST json/form)
    if request.method == "GET":
        user_text = (request.args.get("text") or "").strip()
    else:
        if request.is_json:
            data = request.get_json(silent=True) or {}
            user_text = (data.get("text") or "").strip()
        else:
            user_text = (request.form.get("text") or "").strip()

    # 2) Validate
    if not user_text:
        msg = "Хоосон текст ирсэн байна."
        if request.method == "POST" and not request.is_json:
            return render_template_string(HTML_PAGE, user_text="", reply=None, error=msg), 400
        return jsonify({"error": msg}), 400

    # 3) Call OpenAI Chat Completion (шинэ SDK)
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # чамд нээлттэй модел байхад л болно
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are HASH AI Assistant for Buysmart, Shuurkhai, "
                        "Hash Motors. Always reply in Mongolian, unless the "
                        "user clearly asks for another language. "
                        "Keep answers short and practical."
                    ),
                },
                {"role": "user", "content": user_text},
            ],
            max_tokens=512,
        )
        reply_text = completion.choices[0].message.content
    except Exception as e:
        print("OpenAI error:", e, flush=True)
        error_msg = f"OpenAI алдаа: {e}"
        if request.method == "POST" and not request.is_json:
            return render_template_string(
                HTML_PAGE, user_text=user_text, reply=None, error=error_msg
            ), 500
        return jsonify({"error": error_msg}), 500

    # 4) Return HTML for form submissions, JSON for API clients
    if request.method == "POST" and not request.is_json:
        return render_template_string(
            HTML_PAGE, user_text=user_text, reply=reply_text, error=None
        )
    return jsonify({"reply": reply_text})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
