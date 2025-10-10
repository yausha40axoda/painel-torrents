import gradio as gr
import os
import requests
import time
import aria2p
import subprocess

# 🔹 Inicia aria2c com segredo
rpc_secret = os.getenv("RPC_SECRET", "default123")
subprocess.Popen([
    "aria2c",
    "--enable-rpc",
    "--rpc-listen-all=false",
    "--rpc-allow-origin-all",
    f"--rpc-secret={rpc_secret}"
])

# 🔹 Tokens via ambiente
token_telegram = os.getenv("TELEGRAM_TOKEN", "")
chat_id = os.getenv("CHAT_ID", "")
token_dropbox = os.getenv("DROPBOX_TOKEN", "")

# 🔹 Conexão com aria2
try:
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=rpc_secret
        )
    )
    print("✅ Conectado ao aria2 com sucesso.")
except Exception as e:
    print(f"❌ Erro ao conectar ao aria2: {e}")
    aria2 = None

# 🔹 Função Telegram
def enviar_mensagem_telegram(texto: str) -> str:
    if not token_telegram or not chat_id:
        return "❌ Tokens do Telegram não configurados."
    url = f"https://api.telegram.org/bot{token_telegram}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    response = requests.post(url, data=payload)
    return "✅ Mensagem enviada!" if response.ok else f"❌ Erro: {response.text}"

# 🔹 Função Dropbox
def upload_dropbox(arquivo) -> str:
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

# 🔹 Função Torrent
def baixar_e_gerenciar_automatico(magnet: str) -> str:
    if not aria2:
        return "⚠️ aria2 não está disponível. Verifique se está rodando."
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
            with open(caminho, "rb") as f:
                upload_dropbox(f)
            enviar_mensagem_telegram(f"📦 Arquivo enviado: {nome}")
            resultado.append(f"{nome} enviado")

    return "\n".join(resultado) if resultado else "⚠️ Nenhum arquivo .mkv encontrado."

# 🔹 Interface Gradio
with gr.Blocks(title="Painel de Torrents") as demo:
    with gr.Tab("🔐 Tokens"):
        gr.Markdown("Tokens carregados automaticamente do ambiente.")

    with gr.Tab("📬 Telegram"):
        texto = gr.Textbox(label="Mensagem")
        status_msg = gr.Textbox(label="Status")
        btn_msg = gr.Button(value="Enviar")
        btn_msg.click(fn=enviar_mensagem_telegram, inputs=[texto], outputs=[status_msg])

    with gr.Tab("📁 Dropbox"):
        arquivo = gr.File(label="Escolha um arquivo")
        status_up = gr.Textbox(label="Status")
        btn_up = gr.Button(value="Enviar para Dropbox")
        btn_up.click(fn=upload_dropbox, inputs=[arquivo], outputs=[status_up])

    with gr.Tab("🎬 Torrents"):
        magnet = gr.Textbox(label="Magnet Link")
        status_dl = gr.Textbox(label="Status do Download")
        btn_dl = gr.Button(value="Buscar e Enviar")
        btn_dl.click(fn=baixar_e_gerenciar_automatico, inputs=[magnet], outputs=[status_dl])

# 🔹 Lançamento do painel com share=True
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port, share=True)
