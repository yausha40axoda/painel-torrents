import gradio as gr
import os
import requests

# 🔹 Carrega variáveis de ambiente
token_telegram = os.getenv("TELEGRAM_TOKEN", "").strip()
chat_id = os.getenv("CHAT_ID", "").strip()

# 🔹 Função segura com retorno garantido
def enviar_mensagem_telegram(texto: str) -> str:
    try:
        if not texto.strip():
            return "⚠️ Mensagem vazia."

        if not token_telegram or not chat_id:
            return "❌ TELEGRAM_TOKEN ou CHAT_ID não configurado."

        try:
            chat_id_int = int(chat_id)
        except ValueError:
            return f"❌ CHAT_ID inválido: '{chat_id}'"

        url = f"https://api.telegram.org/bot{token_telegram}/sendMessage"
        payload = {"chat_id": chat_id_int, "text": texto}
        response = requests.post(url, data=payload)

        if response.ok:
            return "✅ Mensagem enviada com sucesso!"
        else:
            return f"❌ Erro do Telegram: {response.status_code} — {response.text}"

    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"

# 🔹 Interface Gradio
with gr.Blocks(title="Painel Telegram") as demo:
    with gr.Tab("📬 Telegram"):
        texto = gr.Textbox(label="Mensagem")
        status = gr.Textbox(label="Status", lines=8, interactive=False)
        enviar = gr.Button("Enviar")
        enviar.click(fn=enviar_mensagem_telegram, inputs=[texto], outputs=[status])

# 🔹 Lançamento do painel
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
