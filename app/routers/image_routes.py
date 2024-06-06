# app/routers/image_routes.py

from fastapi import APIRouter
from app.utils.firebase import get_image_urls

router = APIRouter()

@router.get("/images/")
async def list_images():
    urls = get_image_urls()
    return {"image_urls": urls}
