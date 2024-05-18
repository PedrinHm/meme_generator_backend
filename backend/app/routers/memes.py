from fastapi import APIRouter, File, UploadFile
from app.services.meme_generator import generate_meme
from app.utils.firebase import upload_image

router = APIRouter()

@router.post("/generate-meme/")
async def create_meme(file: UploadFile = File(...)):
    image_url = await upload_image(file)
    meme_data = generate_meme(image_url)
    return {"image_url": image_url, "meme_data": meme_data}
