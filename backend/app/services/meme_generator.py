import os
import json
import re
import io
import google.generativeai as genai

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from fastapi import UploadFile
import tempfile
import shutil
import textwrap

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("A chave de API GEMINI_API_KEY não foi configurada.")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel("gemini-pro-vision")

def extract_subtitle_from_response(response_text: str):
    try:
        match = re.search(r"```json\s*(\{.*\})\s*```", response_text, re.DOTALL)
        if match:
            json_text = match.group(1)
        else:
            raise ValueError("JSON not found in response")
        
        response_json = json.loads(json_text)
        legenda = response_json.get("legenda", "Legenda não encontrada.")
    except json.JSONDecodeError as e:
        legenda = "Legenda não encontrada."
    except ValueError as e:
        legenda = "Legenda não encontrada."
    return {"legenda": legenda}

def generate_subtitle(file: UploadFile) -> dict:
    image_content = file.file.read()
    image = Image.open(io.BytesIO(image_content))

    response = model.generate_content(
        ["Quero criar um meme. Crie uma legenda engraçada para a imagem. Por favor, responda no seguinte formato JSON: 'legenda': 'sua_legenda_aqui.", image],
        stream=True
    )
    response.resolve()
    
    print(response.text)
    
    meme_subtitles = extract_subtitle_from_response(response.text)
    
    print(response.text)

    return meme_subtitles

def apply_subtitles_to_image(file: UploadFile, caption: str):
    try:
        image = Image.open(file.file)
    except UnidentifiedImageError:
        raise ValueError("O arquivo fornecido não é uma imagem válida.")
    
    draw = ImageDraw.Draw(image)
    
    # Substitua pelo caminho correto para a fonte Impact no seu sistema
    font_path = "/path/to/impact.ttf"
    try:
        font = ImageFont.truetype(font_path, size=36)
    except IOError:
        raise ValueError("A fonte 'Impact' não foi encontrada. Verifique o caminho da fonte.")

    max_width = image.width - 20
    char_width, _ = draw.textbbox((0, 0), 'A', font=font)[2:]
    wrapped_caption = textwrap.fill(caption, width=max_width // char_width)

    text_size = draw.textbbox((0, 0), wrapped_caption, font=font)
    text_width, text_height = text_size[2], text_size[3]
    width, height = image.size
    x = (width - text_width) / 2
    y = height - text_height - 10

    outline_range = 2
    for adj in range(-outline_range, outline_range + 1):
        if adj != 0:
            draw.text((x + adj, y), wrapped_caption, font=font, fill="black")
            draw.text((x, y + adj), wrapped_caption, font=font, fill="black")
            draw.text((x + adj, y + adj), wrapped_caption, font=font, fill="black")
            draw.text((x - adj, y - adj), wrapped_caption, font=font, fill="black")

    draw.text((x, y), wrapped_caption, font=font, fill="white")

    return image

def generate_meme_with_subtitles(file: UploadFile) -> str:
    meme_subtitles = generate_subtitle(file)
    subtitles = meme_subtitles.get("legenda", "Sem legenda")
    image_with_subtitles = apply_subtitles_to_image(file, subtitles)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_image_path = os.path.join(temp_dir, "temp_image_with_caption.png")
        image_with_subtitles.save(temp_image_path, format="PNG")
        meme_png = os.path.join(tempfile.gettempdir(), "temp_image_with_caption.png")
        shutil.move(temp_image_path, meme_png)
    
    return meme_png