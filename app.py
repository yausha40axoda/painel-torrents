import gradio as gr
import os
import requests

# 🔹 Carrega tokens do ambiente
token_telegram = os.getenv("TELEGRAM_TOKEN", "")
chat_id = os.getenv("CHAT_ID", "")

# 🔹 Função de envio para Telegram
def enviar_mensagem_telegram(texto: str) -> str:
    if not texto.strip():
        return "⚠️ Mensagem vazia. Digite algo antes de enviar."
    if not token_telegram or not chat_id:
        return "❌ Tokens do Telegram não configurados."

    url = f"https://api.telegram.org/bot{token_telegram}/sendMessage"
    payload = {
        "chat_id": int(chat_id),
        "text": texto
    }

    try:
        response = requests.post(url, data=payload)
        if response.ok:
            return "✅ Mensagem enviada com sucesso!"
        else:
            return f"❌ Erro do Telegram: {response.status_code} — {response.text}"
    except Exception as e:
        return f"❌ Erro ao enviar: {str(e)}"

# 🔹 Interface Gradio com aba Telegram
with gr.Blocks(title="Teste Telegram") as demo:
    with gr.Tab("📬 Telegram"):
        texto = gr.Textbox(label="Mensagem")
        status_msg = gr.Textbox(label="Status", interactive=False)
        btn_msg = gr.Button(value="Enviar")
        btn_msg.click(fn=enviar_mensagem_telegram, inputs=[texto], outputs=[status_msg])

# 🔹 Lançamento do painel
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port, share=True)
