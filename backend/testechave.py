import os

# Tenta recuperar a chave de API
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print("A chave de API foi configurada corretamente: ", api_key)
else:
    print("A chave de API GEMINI_API_KEY não foi configurada.")
