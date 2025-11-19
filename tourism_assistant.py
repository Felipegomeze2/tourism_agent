#!/usr/bin/env python3
"""
Tourism Voice Assistant for Colombia
"""

import os
from livekit.agents import Agent
from livekit.plugins import openai, elevenlabs, silero

class TourismAssistant(Agent):
    def __init__(self):
        api = os.getenv("OPENAI_API_KEY")

        llm = openai.LLM(model="gpt-4o", api_key=api)
        stt = openai.STT()

        try:
            tts = elevenlabs.TTS()
        except:
            tts = openai.TTS()

        vad = silero.VAD.load()

        super().__init__(
            instructions="""
Eres un asistente turístico experto en destinos de Colombia.

PERSONALIDAD:
- Amigable, cálido, con tono colombiano
- Respondes corto y conciso (máx 3 oraciones)
- Recomiendas destinos reales de Colombia
- Incluye precio estimado, clima y actividades principales
- Sugiere alternativas si el usuario no está seguro
- Explica la mejor época del año para viajar
- Mantén el tono turístico, útil y directo

SIEMPRE responde en español natural.
            """,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad
        )
