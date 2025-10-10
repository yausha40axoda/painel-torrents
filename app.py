!pip install gradio aria2p requests

import gradio as gr
import os
import requests
import time
import aria2p

# 🔐 Variáveis globais (simuladas para Colab)
token_telegram = ""
chat_id = ""
token_dropbox = ""

# 🔗 Conecta ao aria2 RPC (simulado para Colab — não roda aria2c aqui)
try:
    aria2 = aria2p.API(aria2p.Client(host="http://localhost", port=6800, secret=""))
except:
    aria2 = None

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

# 📥 Baixar torrent e enviar
def baixar_e_gerenciar_automatico(magnet):
    if not aria2:
        return "⚠️ aria2 não está disponível no Colab. Teste local ou no Render."
    os.makedirs("downloads", exist_ok=True)
    resultado = []

    try:
        downloads = aria2.add(uri=magnet, options={"dir": "downloads"})
    except Exception as e:
        return f"❌ Erro ao iniciar download: {str(e)}"

    download = downloads[0]
    enviar_mensagem_telegram(f"🎬 Iniciando download: {download.name}")

    while not download.is_complete:
        download.update()
        time.sleep(5)

    enviar_mensagem_telegram(f"✅ Download concluído: {download.name}")

    for nome in os.listdir("downloads"):
        caminho = os.path.join("downloads", nome)
        if os.path.isfile(caminho) and nome.endswith(".mkv"):
            upload_dropbox(open(caminho, "rb"))
            enviar_mensagem_telegram(f"📦 Arquivo enviado: {nome}")
            resultado.append(f"{nome} enviado")

    return "\n".join(resultado) if resultado else "⚠️ Nenhum arquivo .mkv encontrado."

# 🎛️ Interface com abas
with gr.Blocks(title="Painel Completo") as demo:
    with gr.Tab("🔐 Tokens"):
        gr.Markdown("### Salve seus tokens aqui")
        token_telegram_input = gr.Textbox(label="Token do Telegram")
        chat_id_input = gr.Textbox(label="Chat ID do Telegram")
        token_dropbox_input = gr.Textbox(label="Token do Dropbox")
        status_tokens = gr.Textbox(label="Status")
        btn_salvar = gr.Button("Salvar Tokens")

        def salvar_tokens(tg, cid, dbx):
            global token_telegram, chat_id, token_dropbox
            token_telegram = tg
            chat_id = cid
            token_dropbox = dbx
            return "✅ Tokens salvos com sucesso!"

        btn_salvar.click(salvar_tokens, [token_telegram_input, chat_id_input, token_dropbox_input], status_tokens)

    with gr.Tab("📬 Telegram"):
        texto = gr.Textbox(label="Mensagem")
        status_msg = gr.Textbox(label="Status")
        btn_msg = gr.Button("Enviar")
        btn_msg.click(enviar_mensagem_telegram, texto, status_msg)

    with gr.Tab("📁 Dropbox"):
        arquivo = gr.File(label="Escolha um arquivo")
        status_up = gr.Textbox(label="Status")
        btn_up = gr.Button("Enviar para Dropbox")
        btn_up.click(upload_dropbox, arquivo, status_up)

    with gr.Tab("🎬 Torrents"):
        magnet = gr.Textbox(label="Magnet Link")
        status_dl = gr.Textbox(label="Status do Download")
        btn_dl = gr.Button("Baixar e Enviar")
        btn_dl.click(baixar_e_gerenciar_automatico, magnet, status_dl)

demo.launch(share=True)
