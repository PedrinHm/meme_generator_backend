import os
import json
import google.generativeai as genai
import re

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("A chave de API GEMINI_API_KEY não foi configurada.")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel(
    model_name="gemini-1.0-pro-vision-latest",
)

chat_session = model.start_chat(history=[])

def extract_data_from_response(response_text):
    response_text = response_text.strip("`")

    legenda_match = re.search(r"'legenda':\s*'([^']+)'", response_text)
    
    legenda = legenda_match.group(1) if legenda_match else "Legenda não encontrada."
    
    return {"legenda": legenda}

def generate_meme(image_url: str) -> dict:
    prompt = (
        f"Quero criar um meme. Para a imagem em {image_url}, crie uma legenda engraçada. Por favor, responda no seguinte formato JSON: {{'legenda': 'sua_legenda_aqui'}}."
    )

    response = chat_session.send_message(prompt)
    response_text = response.text.strip()

    print("Response from model:", response_text)

    try:
        meme_data = json.loads(response_text)
    except json.JSONDecodeError:
        meme_data = extract_data_from_response(response_text)
    
    return meme_data