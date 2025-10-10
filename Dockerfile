FROM python:3.10-slim

# Instala aria2
RUN apt-get update && apt-get install -y aria2

# Instala dependências Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia o app
COPY app.py .

# Comando de inicialização
CMD aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all && python app.py
