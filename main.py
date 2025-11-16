from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# OpenAI client (түлхүүрийг Render дээрх OPENAI_API_KEY-аас уншина)
client = OpenAI()

SYSTEM_PROMPT = """
You are HASH AI Assistant for Buysmart, Shuurkhai, Hash Motors.
Always reply in Mongolian, unless user clearly asks another language.
Keep answers short and practical.
""".strip()


@app.route("/", methods=["GET"])
def index():
    # Жижиг тест HTML форм
    return """
    <h1>HASH AI Assistant</h1>
    <form action="/chat" method="post">
        <textarea name="text" rows="5" cols="60"></textarea><br/>
        <button type="submit">Илгээх</button>
    </form>
    """


@app.route("/chat", methods=["POST"])
def chat():
    """JSON ба HTML form хоёуланг дэмжинэ"""

    user_text = ""

    if request.is_json:
        # ManyChat / webhook гэх мэт JSON POST
        data = request.get_json(silent=True) or {}
        user_text = (data.get("text") or "").strip()
    else:
        # HTML form-оос ирсэн text
        user_text = (request.form.get("text") or "").strip()

    if not user_text:
        # Хоосон асуулт ирвэл
        if request.is_json:
            return jsonify({"error": "Хоосон текст ирлээ."}), 400
        return "<p>Хоосон текст ирлээ.</p><a href='/'>Буцах</a>", 400

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        # Алдааг лог руу хэвлээд, хэрэглэгчид энгийн мессеж үзүүлнэ
        print("OpenAI error:", e, flush=True)
        if request.is_json:
            return jsonify({"error": "OpenAI талд алдаа гарлаа."}), 500
        return "<p>Дотоод алдаа гарлаа. Дахиад оролдоод үзээрэй.</p>", 500

    # Хэрвээ JSON бол JSON-оор буцаана (ManyChat гэх мэтэд таарна)
    if request.is_json:
        return jsonify({"reply": reply})

    # Харин браузерын form бол HTML хуудас буцаана
    return f"""
    <h1>HASH AI Assistant</h1>
    <p><b>Таны асуулт:</b></p>
    <pre>{user_text}</pre>
    <p><b>Хариу:</b></p>
    <pre>{reply}</pre>
    <a href="/">Дахин асуух</a>
    """


if __name__ == "__main__":
    # Render дээр PORT орчинтой явж болно, гэхдээ одоогийн тохиргоо чинь OK
    app.run(host="0.0.0.0", port=10000)
