import firebase_admin
from firebase_admin import credentials, storage, initialize_app
from fastapi import UploadFile
import uuid
import os
import json

def load_firebase_credentials():
    # Assegura que todas as variáveis necessárias estão definidas
    cred_keys = [
        "type", "project_id", "private_key_id", "private_key",
        "client_email", "client_id", "auth_uri", "token_uri",
        "auth_provider_x509_cert_url", "client_x509_cert_url"
    ]
    
    cred_dict = {}
    for key in cred_keys:
        value = os.getenv(f"FIREBASE_{key.upper()}")
        if not value:
            raise ValueError(f"Variável de ambiente FIREBASE_{key.upper()} não está definida.")
        if key == 'private_key':
            value = value.replace('\\n', '\n')
        cred_dict[key] = value

    print("Credenciais Carregadas:", cred_dict)  # Imprime para verificar os valores
    return credentials.Certificate(cred_dict)

# Inicializa o Firebase
firebase_app = initialize_app(load_firebase_credentials(), {"storageBucket": "meme-generator-redes-neurais.appspot.com"})

# Obtém o bucket associado ao Firebase app inicializado
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
