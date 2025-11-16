from flask import Flask, request, jsonify, render_template_string
import openai
import os

app = Flask(__name__)

# Read API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

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
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE, user_text="", reply=None)

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
        if request.method == "POST" and not request.is_json:
            return render_template_string(HTML_PAGE, user_text="", reply="Хоосон текст байна."), 400
        return jsonify({"error": "Хоосон текст ирсэн байна."}), 400

    # 3) Call OpenAI Chat Completion (using openai package)
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # choose a model you have access to
            messages=[
                {
                    "role": "system",
                    "content": "You are HASH AI Assistant for Buysmart, Shuurkhai, Hash Motors. Always reply in Mongolian, unless the user clearly asks for another language. Keep answers short and practical."
                },
                {"role": "user", "content": user_text},
            ],
            max_tokens=512,
        )
        # openai.ChatCompletion.create returns a dict-like response
        reply_text = completion["choices"][0]["message"]["content"]
    except Exception as e:
        # Log error and show a friendly message
        print("OpenAI error:", e, flush=True)
        error_msg = f"OpenAI алдаа: {e}"
        if request.method == "POST" and not request.is_json:
            return render_template_string(HTML_PAGE, user_text=user_text, reply=error_msg), 500
        return jsonify({"error": error_msg}), 500

    # 4) Return HTML for form submissions, JSON for API clients
    if request.method == "POST" and not request.is_json:
        return render_template_string(HTML_PAGE, user_text=user_text, reply=reply_text)
    return jsonify({"reply": reply_text})

if __name__ == "__main__":
    # Use PORT env var if present (useful on platforms like Render)
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
