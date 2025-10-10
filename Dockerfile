FROM python:3.10-slim

RUN apt-get update && apt-get install -y aria2 curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD bash -c "aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all & python app.py"
