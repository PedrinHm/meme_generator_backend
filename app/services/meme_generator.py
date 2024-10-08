import os
import json
import re
import io
import google.generativeai as genai

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError, ExifTags
from fastapi import UploadFile
import tempfile
import shutil
import textwrap

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("A chave de API GEMINI_API_KEY não foi configurada.")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel("gemini-1.5-pro-002")

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
        ["Você é o Memeiro Supremo, um criador de memes que domina a arte de fazer qualquer pessoa rir, independentemente da idade ou interesse. Sua missão é criar memes que conectem diferentes públicos, misturando cultura pop, temas cotidianos e tendências da internet de forma inteligente e acessível. Com um senso de humor afiado e versátil, você sabe adaptar o tom para cada plataforma, seja uma piada boba ou um meme cheio de ironia e referências nerds. Sempre atento ao que está em alta, você cria conteúdos que são engraçados, atemporais e que fazem as pessoas se sentirem parte de algo maior. Faça um meme para a imagem. Por favor, responda no seguinte formato JSON: 'legenda': 'sua_legenda_aqui.", image],
        stream=True
    )
    response.resolve()
    
    print(response.text)
    
    meme_subtitles = extract_subtitle_from_response(response.text)
    
    print(response.text)

    return meme_subtitles

def correct_image_orientation(img):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        
        exif = dict(img._getexif().items())

        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass

    return img

def apply_subtitles_to_image(file, caption: str):
    try:
        image = Image.open(file.file)
        image = correct_image_orientation(image)
    except UnidentifiedImageError:
        raise ValueError("O arquivo fornecido não é uma imagem válida.")

    width, height = image.size
    font_size = width // 20
    max_width = width - 40

    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'BebasNeue-Regular.ttf')
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"O arquivo da fonte não foi encontrado no caminho: {font_path}")

    try:
        font = ImageFont.truetype(font_path, size=font_size)
        print("Fonte carregada com sucesso.")
    except IOError as e:
        raise IOError(f"Erro ao carregar a fonte: {e}")
        
    chars_per_line = max_width // (font_size // 2)
    caption_lines = textwrap.fill(caption, width=chars_per_line).split('\n')

    draw = ImageDraw.Draw(image)

    mid_point = len(caption_lines) // 2
    top_lines = caption_lines[:mid_point]
    bottom_lines = caption_lines[mid_point:]

    y_offset_top = 10
    for line in top_lines:
        line_width = draw.textlength(line, font=font)
        x = (width - line_width) / 2
        draw.text((x, y_offset_top), line, font=font, fill='white', stroke_width=2, stroke_fill='black')
        y_offset_top += font_size

    y_offset_bottom = height - (len(bottom_lines) * font_size) - 10
    for line in bottom_lines:
        line_width = draw.textlength(line, font=font)
        x = (width - line_width) / 2
        draw.text((x, y_offset_bottom), line, font=font, fill='white', stroke_width=2, stroke_fill='black')
        y_offset_bottom += font_size

    return image

def generate_meme_with_subtitles(file: UploadFile) -> str:
    max_attempts = 3 
    attempt = 0
    meme_subtitles = None

    while attempt < max_attempts:
        meme_subtitles = generate_subtitle(file)
        if meme_subtitles.get("legenda") != "Legenda não encontrada.":
            break
        attempt += 1

    if meme_subtitles.get("legenda") == "Legenda não encontrada.":
        return "Não foi possível gerar uma legenda válida após várias tentativas."

    subtitles = meme_subtitles.get("legenda", "Sem legenda")
    image_with_subtitles = apply_subtitles_to_image(file, subtitles)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_image_path = os.path.join(temp_dir, "temp_image_with_caption.png")
        image_with_subtitles.save(temp_image_path, format="PNG")
        meme_png = os.path.join(tempfile.gettempdir(), "temp_image_with_caption.png")
        shutil.move(temp_image_path, meme_png)

    return meme_png
