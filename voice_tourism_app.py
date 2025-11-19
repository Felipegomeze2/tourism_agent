#!/usr/bin/env python3
"""
Optimized Voice Tourism App - Colombia Travel Agent
"""

from flask import Flask, render_template, request, jsonify, session
import uuid
import logging
import os
import tempfile
import asyncio
import base64
import time
from dotenv import load_dotenv

from tourism_assistant import TourismAssistant
from tourism_database import get_tourism_db

from openai import OpenAI

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tourism-secret-key")

# Global objects
assistants = {}
conversation_history = {}
tourism_db = get_tourism_db()

# ---- Helpers ----

def get_assistant():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    sid = session["session_id"]

    if sid not in assistants:
        assistants[sid] = TourismAssistant()
        conversation_history[sid] = []

    return assistants[sid], conversation_history[sid]

def add_msg(session_id, role, text):
    conversation_history[session_id].append({
        "role": role,
        "content": text,
        "timestamp": time.time()
    })

    if len(conversation_history[session_id]) > 20:
        conversation_history[session_id] = conversation_history[session_id][-20:]

def build_prompt(user_msg, history, destinos, desc=""):
    recent = ""
    for m in history[-4:]:
        tag = "Usuario" if m["role"] == "user" else "Asistente"
        recent += f"{tag}: {m['content']}\n"

    destinos_txt = "DESTINOS RECOMENDADOS:\n"
    for d in destinos[:6]:
        destinos_txt += f"- {d['name']} ({d['department']}), aprox ${d['price']}, clima {d['climate']}\n"

    return f"""
CONTEXTO RECIENTE:
{recent}

{destinos_txt}

USUARIO: {user_msg}

RESPUESTA (máx 3 oraciones, concisa, turística, menciona clima/actividades/precio):
"""

async def ask_gpt(prompt):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente turístico colombiano: breve, útil, cálido y directo."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"GPT error: {e}")
        return "Puedo darte recomendaciones turísticas. ¿Qué destino de Colombia te interesa?"

# ---- Routes ----

@app.route("/")
def index():
    return render_template("voice_index.html")

@app.route("/api/greet", methods=["POST"])
def greet():
    assistant, history = get_assistant()
    sid = session["session_id"]

    destinos = tourism_db.featured_destinations(6)

    greeting = (
        f"¡Hola! Soy tu asistente turístico de Colombia. "
        f"Tengo {len(tourism_db.df)} destinos para recomendarte. "
        f"Por ejemplo, {destinos[0]['name']} cuesta aprox ${destinos[0]['price']}. "
        "¿Qué tipo de destino buscas?"
    )

    add_msg(sid, "assistant", greeting)

    return jsonify({
        "success": True,
        "message": greeting,
        "mentioned_products": destinos
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()

    assistant, history = get_assistant()
    sid = session["session_id"]

    add_msg(sid, "user", user_msg)

    destinos, desc = tourism_db.search(user_msg, max_results=8)

    prompt = build_prompt(user_msg, history, destinos, desc)
    reply = asyncio.run(ask_gpt(prompt))

    add_msg(sid, "assistant", reply)

    return jsonify({
        "success": True,
        "response": reply,
        "mentioned_products": destinos[:6]
    })

@app.route("/api/voice/chat", methods=["POST"])
def voice_chat():
    sid = request.form.get("session_id")
    voice = request.form.get("voice", "alloy")
    audio = request.files.get("audio")

    if not audio:
        return jsonify({"error": "No audio"}), 400

    # Save temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        audio.save(tmp.name)
        path = tmp.name

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with open(path, "rb") as f:
            trans = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        user_msg = trans.text

        add_msg(sid, "user", user_msg)

        destinos, desc = tourism_db.search(user_msg, 8)
        prompt = build_prompt(user_msg, conversation_history[sid], destinos, desc)
        reply = asyncio.run(ask_gpt(prompt))
        add_msg(sid, "assistant", reply)

        # TTS
        audio_out = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=reply,
            speed=1.1
        )

        b64 = base64.b64encode(audio_out.content).decode()

        return jsonify({
            "success": True,
            "user_message": user_msg,
            "response_text": reply,
            "audio_data": b64,
            "mentioned_products": destinos[:6]
        })

    finally:
        os.unlink(path)

# ---- Start ----

if __name__ == "__main__":
    logger.info("🌎 Turismo Colombia - Voice Agent")
    app.run(debug=True, host="0.0.0.0", port=5000)
