from fastapi import APIRouter, File, UploadFile
from app.services.meme_generator import generate_meme_with_caption
from app.utils.firebase import upload_image

router = APIRouter()

@router.post("/generate-meme/")
async def create_meme(file: UploadFile = File(...)):
    local_image_path = generate_meme_with_caption(file)
    
    with open(local_image_path, 'rb') as img_file:
        upload_file = UploadFile(img_file, filename="temp_image_with_caption.png")
        captioned_image_url = await upload_image(upload_file, content_type="image/png")
    
    return {"captioned_image_url": captioned_image_url}
