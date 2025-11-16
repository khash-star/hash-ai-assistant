from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------
# 1) Browser дээр харагдах FORM
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    return """
    <h2>HASH AI Assistant</h2>
    <form method="post" action="/chat">
      <textarea name="text" rows="5" cols="60" placeholder="Юу асуух вэ?"></textarea><br><br>
      <button type="submit">Илгээх</button>
    </form>
    """


# -----------------------------
# 2) POST API endpoint (/chat)
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    # JSON эсвэл FORM аль нь ирсэн ч уншина
    data = request.get_json(silent=True) or {}
    user_text = data.get("text") or request.form.get("text", "")

    if not user_text:
        return jsonify({"reply": "Хоосон текст ирлээ."}), 200

    # OPENAI дуудлага
    reply = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are HASH AI assistant for Buysmart, Shuurkhai, Hash Motors."},
            {"role": "user", "content": user_text},
        ]
    )

    bot_reply = reply.choices[0].message["content"]

    # Хэрвээ POST form-оор ирсэн бол HTML буцаана
    if request.form.get("text"):
        return f"<h2>Хариу:</h2><p>{bot_reply}</p><br><a href='/'>Буцах</a>"

    # JSON response
    return jsonify({"reply": bot_reply}), 200


# -----------------------------
# 3) Server Run
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
