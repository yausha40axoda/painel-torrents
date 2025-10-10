import gradio as gr
import os
import requests
import time
import aria2p

# 🔐 Tokens via variáveis de ambiente
token_dropbox = os.getenv("DROPBOX_TOKEN")
token_telegram = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("CHAT_ID")

# 🔗 Conecta ao aria2 RPC
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""  # Se usar secret, defina aqui e no start command
    )
)

# 📤 Envia mensagem para Telegram
def enviar_mensagem_telegram(texto):
    url = f"https://api.telegram.org/bot{token_telegram}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    requests.post(url, data=payload)

# 📤 Envia arquivo para Telegram
def enviar_arquivo_telegram(caminho):
    nome = os.path.basename(caminho)
    url = f"https://api.telegram.org/bot{token_telegram}/sendDocument"
    with open(caminho, "rb") as f:
        files = {"document": (nome, f)}
        data = {"chat_id": chat_id}
        requests.post(url, data=data, files=files)

# 📁 Upload para Dropbox
def upload_dropbox(caminho):
    nome = os.path.basename(caminho)
    with open(caminho, "rb") as f:
        conteudo = f.read()
    headers = {
        "Authorization": f"Bearer {token_dropbox}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": f'{{"path": "/{nome}", "mode": "add", "autorename": true}}'
    }
    requests.post("https://content.dropboxapi.com/2/files/upload", headers=headers, data=conteudo)

# 📥 Função principal: baixar torrent e enviar
def baixar_e_gerenciar_automatico(magnet):
    os.makedirs("downloads", exist_ok=True)
    resultado = []

    try:
        downloads = aria2.add(uri=magnet, options={"dir": "downloads"})
    except Exception as e:
        return f"❌ Erro ao iniciar download: {str(e)}"

    if not downloads:
        return "❌ Nenhum download iniciado."

    download = downloads[0]
    enviar_mensagem_telegram(f"🎬 Iniciando download: {download.name}")

    while not download.is_complete:
        download.update()
        time.sleep(5)

    enviar_mensagem_telegram(f"✅ Download concluído: {download.name}")

    for nome in os.listdir("downloads"):
        caminho = os.path.join("downloads", nome)
        if os.path.isfile(caminho) and nome.endswith(".mkv"):
            upload_dropbox(caminho)
            enviar_arquivo_telegram(caminho)
            tamanho = os.path.getsize(caminho) / (1024 * 1024)
            resultado.append(f"📦 {nome} enviado ({tamanho:.2f} MB)")

    return "\n".join(resultado) if resultado else "⚠️ Nenhum arquivo .mkv encontrado."

# 🎛️ Interface Gradio
demo = gr.Interface(
    fn=baixar_e_gerenciar_automatico,
    inputs=gr.Textbox(label="🔗 Magnet Link"),
    outputs=gr.Textbox(label="📦 Status do Download"),
    title="Painel de Torrents",
    description="Insira o link magnet para baixar, enviar para Dropbox e Telegram automaticamente."
)

# 🔌 Configuração para Render
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
