import firebase_admin
from firebase_admin import credentials, storage
from fastapi import UploadFile
import uuid
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
cred_path = os.path.join(base_dir, 'credentials', 'firebase-adminsdk.json')

if not os.path.exists(cred_path):
    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {"storageBucket": "meme-generator-redes-neurais.appspot.com"})

bucket = storage.bucket()

async def upload_image(file: UploadFile, content_type: str = "application/octet-stream") -> str:
    blob = bucket.blob(f"images/{uuid.uuid4()}.png")
    blob.upload_from_file(file.file, content_type=content_type)
    blob.make_public() 
    return blob.public_url

def get_image_urls():
    bucket = storage.bucket()  
    blobs = bucket.list_blobs(prefix="images/") 
    urls = [blob.public_url for blob in blobs if blob.name.endswith(".png")]
    return urls