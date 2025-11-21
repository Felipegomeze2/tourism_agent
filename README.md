# 🌴 Tourism Voice Agent — Asistente Turístico de Colombia  
Proyecto Final — Inteligencia Artificial  
Autor: Felipe Gómez Espinal y Diego Hernandez

---

## 🎤 ¿Qué es este proyecto?
Un **agente de voz en tiempo real** que actúa como un **asistente turístico experto en destinos de Colombia**, capaz de:

- Entender voz del usuario (STT – Whisper)
- Contestar con voz natural (TTS – OpenAI / ElevenLabs)
- Mantener una conversación contextual
- Recomendar destinos reales de Colombia
- Mostrar tarjetas con precios, actividades y clima
- Procesar texto y audio con un mismo agente
- Responder en menos de 2 segundos

🎧 Modo voz interactivo  
⌨️ Chat tradicional por texto  

---

## 🚀 Funcionalidades principales
- Reconocimiento de voz (Whisper / LiveKit STT)
- Síntesis de voz (OpenAI TTS o ElevenLabs)
- Agente conversacional (gpt-4o-mini)
- Base de datos turística (Polars)
- Coincidencias exactas + Fuzzy Matching
- Recomendaciones contextuales en tiempo real
- Tarjetas visuales de destinos
- Interrupción de voz del agente (como Alexa/Siri)
- Sesiones aisladas por usuario

---

## 🏗️ Arquitectura del sistema

Browser (HTML/JS)
       |
       v
Flask Backend
 - /api/chat
 - /api/voice/chat
 - /api/greet
       |
       v
Tourism Assistant (LiveKit Agent)
       |
       v
OpenAI GPT-4o / Whisper / TTS
       |
       v
TourismDatabase (polars, fuzzy search)

---

## 📦 Requisitos

Python 3.10+

Instalar dependencias:

pip install -r requirements.txt


---

## 🔐 Variables de entorno (.env)

Crear un archivo llamado **.env** con:

SECRET_KEY=tourism-secret-key

OPENAI_API_KEY="TU_API_KEY_AQUI"

TOURISM_DATA_PATH=data/tourism_data.csv


---

## ▶️ Cómo ejecutar

1) Activar el entorno virtual:

venv\Scripts\activate

2) Ejecutar el servidor Flask:

python voice_tourism_app.py


3) Abrir en el navegador:

http://127.0.0.1:5000


---

## 📁 Estructura del proyecto

project/

│

├── voice_tourism_app.py

├── tourism_assistant.py

├── tourism_database.py

├── requirements.txt

├── .env

├── data/

│ └── tourism_data.csv

├── templates/

│ └── voice_index.html

└── static/

├── style.css

└── script.js



---

## 🧠 ¿Cómo funciona el asistente?

El asistente se comporta como un **experto turístico colombiano**:

- Responde máximo en 3 oraciones  
- Recomienda destinos reales  
- Usa precios, clima y actividades  
- Se adapta a la intención del usuario  
- Mantiene coherencia en la conversación  

---

## 🎯 Ejemplo de interacción

**Usuario:** “Quiero viajar a un lugar barato con playa.”

**Asistente:**  
“Una buena opción es Santa Marta, clima cálido, playas amplias y acceso al Parque Tayrona.  
El precio ronda los $1’100.000.  
Si quieres algo más tranquilo puedes considerar San Andrés.”

---
