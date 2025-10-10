import gradio as gr
import os
import requests

# 🔐 Carrega tokens das variáveis de ambiente
token_telegram = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("CHAT_ID")
token_dropbox = os.getenv("DROPBOX_TOKEN")

# 📤 Envia mensagem para Telegram
def enviar_mensagem_telegram(texto):
    if not token_telegram or not chat_id:
        return "❌ Tokens do Telegram não configurados."
    url = f"https://api.telegram.org/bot{token_telegram}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    response = requests.post(url, data=payload)
    return "✅ Mensagem enviada!" if response.ok else f"❌ Erro: {response.text}"

# 📁 Upload para Dropbox
def upload_dropbox(arquivo):
    if not token_dropbox:
        return "❌ Token do Dropbox não configurado."
    nome = os.path.basename(arquivo.name)
    conteudo = arquivo.read()
    headers = {
        "Authorization": f"Bearer {token_dropbox}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": f'{{"path": "/{nome}", "mode": "add", "autorename": true}}'
    }
    response = requests.post("https://content.dropboxapi.com/2/files/upload", headers=headers, data=conteudo)
    return "✅ Upload concluído!" if response.ok else f"❌ Erro: {response.text}"

# 🎛️ Interface Gradio
with gr.Blocks(title="Painel de Integração") as demo:
    gr.Markdown("## 📬 Enviar mensagem para Telegram")
    texto = gr.Textbox(label="Mensagem")
    status_msg = gr.Textbox(label="Status")
    btn_msg = gr.Button("Enviar")
    btn_msg.click(fn=enviar_mensagem_telegram, inputs=texto, outputs=status_msg)

    gr.Markdown("## 📁 Upload de arquivo para Dropbox")
    arquivo = gr.File(label="Escolha um arquivo")
    status_up = gr.Textbox(label="Status")
    btn_up = gr.Button("Enviar para Dropbox")
    btn_up.click(fn=upload_dropbox, inputs=arquivo, outputs=status_up)

# 🔌 Configuração para Render
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
