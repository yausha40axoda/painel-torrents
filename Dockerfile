FROM debian:bullseye-slim

# Instala Python e aria2
RUN apt-get update && \
    apt-get install -y python3 python3-pip aria2 && \
    apt-get clean

# Instala dependências Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copia o app
COPY app.py .

# Comando de inicialização
CMD bash -c "aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all & python3 app.py"
