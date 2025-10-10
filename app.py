def enviar_mensagem_telegram(texto: str) -> str:
    try:
        log = []

        log.append(f"📨 Texto recebido: {texto}")
        log.append(f"🔐 Token presente: {'Sim' if token_telegram else 'Não'}")
        log.append(f"🆔 Chat ID presente: {'Sim' if chat_id else 'Não'}")

        if not texto.strip():
            log.append("⚠️ Mensagem vazia.")
            return "\n".join(log)

        if not token_telegram or not chat_id:
            log.append("❌ Token ou Chat ID ausente.")
            return "\n".join(log)

        url = f"https://api.telegram.org/bot{token_telegram}/sendMessage"
        payload = {
            "chat_id": int(chat_id),
            "text": texto
        }

        response = requests.post(url, data=payload)
        log.append(f"🌐 URL chamada: {url}")
        log.append(f"📦 Payload: {payload}")
        log.append(f"📡 Status HTTP: {response.status_code}")

        if response.ok:
            log.append("✅ Mensagem enviada com sucesso!")
        else:
            log.append(f"❌ Erro do Telegram: {response.text}")

        return "\n".join(log)

    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"
        import requests

token = "8454340898:AAFhVCKBIH4gy8-OmIBKgF6bPbZOdZW9Xus"
chat_id = 7092570800
texto = "oi"

url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {"chat_id": chat_id, "text": texto}

response = requests.post(url, data=payload)
print("Status:", response.status_code)
print("Resposta:", response.text)
