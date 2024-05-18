import os
import json
import google.generativeai as genai
import re

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("A chave de API GEMINI_API_KEY não foi configurada.")

genai.configure(api_key=gemini_api_key)

generation_config = {
    "temperature": 0.7,  
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 150,  
    "response_mime_type": "text/plain",  
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

def extract_data_from_response(response_text):
    response_text = response_text.strip("`")

    legenda_match = re.search(r"'legenda':\s*'([^']+)'", response_text)
    pixels_match = re.search(r"'pixels':\s*'([^']+)'", response_text)
    fontsize_match = re.search(r"'fontsize':\s*'(\d+)'", response_text)
    
    legenda = legenda_match.group(1) if legenda_match else "Legenda não encontrada."
    pixels = pixels_match.group(1) if pixels_match else ""
    fontsize = fontsize_match.group(1) if fontsize_match else "0"
    
    return {"legenda": legenda, "pixels": pixels, "fontsize": fontsize}

def generate_meme(image_url: str) -> dict:
    prompt = (
        f"Quero criar um meme. Para a imagem em {image_url}, crie uma legenda engraçada e indique a posição ideal para a legenda na imagem e o tamanho recomendado da fonte. Por favor, responda no seguinte formato JSON: {'legenda': 'sua_legenda_aqui', 'pixels': 'posição_xy', 'fontsize': 'tamanho_da_fonte'}."
    )

    response = chat_session.send_message(prompt)
    response_text = response.text.strip()

    print("Response from model:", response_text)

    try:
        meme_data = json.loads(response_text)
    except json.JSONDecodeError:
        
        meme_data = {"legenda": response_text, "pixels": "", "fontsize": ""}
        meme_data = extract_data_from_response(response_text)
        return meme_data