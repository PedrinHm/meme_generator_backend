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

    return credentials.Certificate(cred_dict)

# Inicializa o Firebase
firebase_app = initialize_app(load_firebase_credentials(), {"storageBucket": "meme-generator-redes-neurais.appspot.com"})

# Obtém o bucket associado ao Firebase app inicializado
bucket = storage.bucket()

try:
    blobs = list(bucket.list_blobs())  # Certifica-se de que 'blobs' é uma lista
    if not blobs:
        print("Nenhum arquivo encontrado no bucket.")
except Exception as e:
    print(f"Erro ao acessar o bucket: {e}")
    blobs = []  # Assegura que blobs é uma lista vazia em caso de erro

# Pasta local para salvar os arquivos
local_folder = r'C:\Users\Computador\Documents\Faculdade\Redes_Neurais\meme_generator_backend\images'

# Certificar de que a pasta local existe
if not os.path.exists(local_folder):
    os.makedirs(local_folder)

# Baixar cada arquivo, se houver
if blobs:
    for blob in blobs:
        file_path = os.path.join(local_folder, blob.name)
        blob.download_to_filename(file_path)
        print(f'Arquivo {blob.name} baixado com sucesso!')
else:
    print("Nenhum arquivo para baixar.")