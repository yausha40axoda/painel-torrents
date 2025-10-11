import gradio as gr
import os
import requests

# 🔹 Carrega variáveis de ambiente
token_telegram = os.getenv("TELEGRAM_TOKEN", "")
chat_id = os.getenv("CHAT_ID", "")

# 🔹 Função de envio com log detalhado
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

# 🔹 Interface Gradio com aba Telegram
with gr.Blocks(title="Painel DropColab") as demo:
    with gr.Tab("📬 Telegram"):
        texto = gr.Textbox(label="Mensagem")
        status_msg = gr.Textbox(label="Log de Status", lines=10, interactive=False)
        btn_msg = gr.Button(value="Enviar")
        btn_msg.click(fn=enviar_mensagem_telegram, inputs=[texto], outputs=[status_msg])

# 🔹 Lançamento do painel
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
