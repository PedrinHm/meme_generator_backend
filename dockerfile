# Usar uma imagem base Python oficial, versão 3.9-slim
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo requirements.txt para o diretório atual no container
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o diretório backend para o diretório de trabalho no container
COPY ./backend .

# Informar que o container está escutando na porta 8000
EXPOSE 8000

# Comando para executar a aplicação usando uvicorn
# Ajuste o caminho do módulo FastAPI de acordo com a localização e nome do arquivo
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
