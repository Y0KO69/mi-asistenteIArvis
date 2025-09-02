import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# ==================================
# CONFIGURACIÓN
# ==================================
app = Flask(__name__)
CORS(app)  # permite llamadas desde el frontend (HTML/JS)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ Debes configurar la variable de entorno OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


# ==================================
# RUTA: Buscar en Google (tema)
# ==================================
@app.route("/buscar", methods=["POST"])
def buscar():
    data = request.get_json()
    tema = data.get("tema")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": SEARCH_ENGINE_ID, "q": tema, "lr": "lang_es"}
    response = requests.get(url, params=params)
    return jsonify(response.json())


# ==================================
# RUTA: Chat con OpenAI (texto + imagen opcional)
# ==================================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    text = data.get("text", "")
    image_base64 = data.get("image_base64", None)
    image_type = data.get("image_type", "image/jpeg")

    messages = [
        {"role": "system", "content": "Eres un profesor en español. Analiza texto e imágenes de ejercicios. Da retroalimentación clara, corrige, sugiere, pero no des la respuesta final."}
    ]

    user_content = []
    if text:
        user_content.append({"type": "text", "text": text})
    if image_base64:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{image_type};base64,{image_base64}"}
        })

    messages.append({"role": "user", "content": user_content})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3
    )

    return jsonify(completion.to_dict())


# ==================================
# MAIN
# ==================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 