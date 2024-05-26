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
    
    # Caminho para a fonte dentro do diretório do projeto
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "impact.ttf")
    try:
        font_size = 70  # Aumentar o tamanho da fonte
        font = ImageFont.truetype(font_path, size=font_size)
    except IOError:
        raise ValueError("A fonte 'Impact' não foi encontrada. Verifique o caminho da fonte.")
    
    width, height = image.size
    max_width = width - 20
    
    # Ajustar quebra de linha da legenda
    caption_lines = textwrap.fill(caption, width=40).split('\n')
    mid_index = len(caption_lines) // 2
    top_caption = '\n'.join(caption_lines[:mid_index])
    bottom_caption = '\n'.join(caption_lines[mid_index:])
    
    # Diminuir a margem para o topo e a parte inferior
    margin_top = 5
    margin_bottom = 5
    
    # Desenhar legenda no topo
    text_size = draw.textbbox((0, 0), top_caption, font=font)
    text_width, text_height = text_size[2], text_size[3]
    x_top = (width - text_width) / 2
    y_top = margin_top  # Margem do topo
    
    # Desenhar contorno do texto no topo
    outline_range = 2
    for adj in range(-outline_range, outline_range + 1):
        if adj != 0:
            draw.text((x_top + adj, y_top), top_caption, font=font, fill="black")
            draw.text((x_top, y_top + adj), top_caption, font=font, fill="black")
            draw.text((x_top + adj, y_top + adj), top_caption, font=font, fill="black")
            draw.text((x_top - adj, y_top - adj), top_caption, font=font, fill="black")

    draw.text((x_top, y_top), top_caption, font=font, fill="white")

    # Desenhar legenda na parte inferior
    text_size = draw.textbbox((0, 0), bottom_caption, font=font)
    text_width, text_height = text_size[2], text_size[3]
    x_bottom = (width - text_width) / 2
    y_bottom = height - text_height - margin_bottom  # Margem inferior
    
    # Desenhar contorno do texto na parte inferior
    for adj in range(-outline_range, outline_range + 1):
        if adj != 0:
            draw.text((x_bottom + adj, y_bottom), bottom_caption, font=font, fill="black")
            draw.text((x_bottom, y_bottom + adj), bottom_caption, font=font, fill="black")
            draw.text((x_bottom + adj, y_bottom + adj), bottom_caption, font=font, fill="black")
            draw.text((x_bottom - adj, y_bottom - adj), bottom_caption, font=font, fill="black")

    draw.text((x_bottom, y_bottom), bottom_caption, font=font, fill="white")

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