FROM python:3.10-slim

# Instala aria2 e dependências básicas
RUN apt-get update && apt-get install -y aria2 curl

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o app
COPY app.py .

# Comando de inicialização
CMD bash -c "aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all & python app.py"
