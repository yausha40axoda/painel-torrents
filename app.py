import gradio as gr
import os
import requests
import time
import aria2p
import subprocess
import socket

# 🔹 Verifica se a porta 6800 está ocupada
def porta_esta_ocupada(porta):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", porta)) == 0

# 🔹 Inicia aria2c com segredo, se necessário
rpc_secret = os.getenv("RPC_SECRET", "default123")
if not porta_esta_ocupada(6800):
    subprocess.Popen([
        "aria2c",
        "--enable-rpc",
        "--rpc-listen-all=false",
        "--rpc-allow-origin-all",
        f"--rpc-secret={rpc_secret}"
    ])
else:
    print("⚠️ aria2c já está rodando ou porta 6800 ocupada.")

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
    if not texto.strip():
        return "⚠️ Mensagem vazia. Digite algo antes de enviar."
    if not token_telegram or not chat_id:
        return "❌ Tokens do Telegram não configurados."
    url = f"https://api.telegram.org/bot{token_telegram}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    try:
        response = requests.post(url, data=payload)
        return "✅ Mensagem enviada com sucesso!" if response.ok else f"❌ Erro do Telegram: {response.text}"
    except Exception as e:
        return f"❌ Erro ao enviar: {str(e)}"

# 🔹 Função Dropbox (apenas .mkv)
def upload_dropbox(arquivo) -> str:
    if not token_dropbox:
        return "❌ Token do Dropbox não configurado."
    nome = os.path.basename(arquivo.name)
    if not nome.endswith(".mkv"):
        return f"⚠️ Apenas arquivos .mkv são permitidos. Você enviou: {nome}"
    caminho = arquivo.name
    conteudo = arquivo.read()
    tamanho = len(conteudo)
    gr.Info(f"📤 Enviando: {nome} — {tamanho // 1024} KB")

    headers = {
        "Authorization": f"Bearer {token_dropbox}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": f'{{"path": "/{nome}", "mode": "add", "autorename": true}}'
    }

    try:
        response = requests.post("https://content.dropboxapi.com/2/files/upload", headers=headers, data=conteudo)
        if response.ok:
            if os.path.exists(caminho):
                os.remove(caminho)
            return f"✅ Upload concluído e arquivo excluído: {nome}"
        else:
            return f"❌ Erro no upload: {response.text}"
    except Exception as e:
        return f"❌ Erro ao enviar: {str(e)}"

# 🔹 Função Torrent com barra de progresso
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
        progresso = int(download.progress * 100)
        gr.Info(f"📥 Baixando: {download.name} — {progresso}%")
        time.sleep(2)

    enviar_mensagem_telegram(f"✅ Download concluído: {download.name}")

    for nome in os.listdir("downloads"):
        caminho = os.path.join("downloads", nome)
        if os.path.isfile(caminho) and nome.endswith(".mkv"):
            status = upload_dropbox(open(caminho, "rb"))
            enviar_mensagem_telegram(f"📦 {status}")
            resultado.append(status)

    return "\n".join(resultado) if resultado else "⚠️ Nenhum arquivo .mkv encontrado."

# 🔹 Diagnóstico RPC
def testar_rpc() -> str:
    try:
        if not aria2:
            return "❌ Não foi possível conectar ao aria2."
        downloads = aria2.get_downloads()
        return f"✅ Conexão RPC bem-sucedida!\n🔹 Downloads ativos: {len(downloads)}"
    except Exception as e:
        return f"❌ Falha na conexão RPC.\nErro: {str(e)}"

# 🔹 Função para exibir status dos tokens
def status_token(valor):
    return "✔️ Carregado" if valor else "❌ Ausente"

# 🔹 Gerenciador de arquivos
def listar_arquivos():
    pasta = "downloads"
    if not os.path.exists(pasta):
        return "⚠️ Pasta 'downloads' não existe."
    arquivos = [f for f in os.listdir(pasta) if f.endswith(".mkv")]
    if not arquivos:
        return "⚠️ Nenhum arquivo .mkv encontrado."
    return "\n".join(arquivos)

# 🔹 Rclone: salvar config
def salvar_rclone_conf(conf_file):
    os.makedirs("rclone_config", exist_ok=True)
    caminho = os.path.join("rclone_config", "rclone.conf")
    with open(caminho, "wb") as f:
        f.write(conf_file.read())
    return "✅ rclone.conf salvo com sucesso!"

# 🔹 Rclone: enviar arquivo
def enviar_com_rclone(arquivo, remoto):
    nome = os.path.basename(arquivo.name)
    if not nome.endswith(".mkv"):
        return f"⚠️ Apenas arquivos .mkv são permitidos. Você enviou: {nome}"
    caminho = arquivo.name
    try:
        resultado = subprocess.run(
            ["rclone", "--config", "rclone_config/rclone.conf", "copy", caminho, f"{remoto}:/"],
            capture_output=True,
            text=True
        )
        if resultado.returncode == 0:
            os.remove(caminho)
            return f"✅ Enviado via rclone e excluído: {nome}"
        else:
            return f"❌ Erro rclone: {resultado.stderr}"
    except Exception as e:
        return f"❌ Falha ao executar rclone: {str(e)}"

# 🔹 Interface Gradio
remotos_disponiveis = ["dropbox", "gdrive", "onedrive", "mega"]

with gr.Blocks(title="Painel de Torrents") as demo:
    with gr.Tab("🔐 Tokens"):
        gr.Markdown("🔐 Status dos tokens carregados do ambiente:")
        gr.Textbox(value=status_token(token_telegram), label="TELEGRAM_TOKEN", interactive=False)
        gr.Textbox(value=status_token(chat_id), label="CHAT_ID", interactive=False)
        gr.Textbox(value=status_token(token_dropbox), label="DROPBOX_TOKEN", interactive=False)
        gr.Textbox(value=status_token(rpc_secret), label="RPC_SECRET", interactive=False)

    with gr.Tab("📬 Telegram"):
        texto = gr.Textbox(label="Mensagem")
        status_msg = gr.Textbox(label="Status")
        btn_msg = gr.Button(value="Enviar")
        btn_msg.click(fn=enviar_mensagem_telegram, inputs=[texto], outputs=[status_msg])

    with gr.Tab("📁 Dropbox"):
        arquivo = gr.File(label="Escolha um arquivo")
        status_up = gr.Textbox(label="Progresso do Upload", interactive=False)
        btn_up = gr.Button(value="Enviar para Dropbox")
        btn_up.click(fn=upload_dropbox, inputs=[arquivo], outputs=[status_up])

    with gr.Tab("🎬 Torrents"):
        magnet = gr.Textbox(label="Magnet Link")
        status_dl = gr.Textbox(label="Pro
# 🔹 Rclone: salvar config
def salvar_rclone_conf(conf_file):
    os.makedirs("rclone_config", exist_ok=True)
    caminho = os.path.join("rclone_config", "rclone.conf")
    with open(caminho, "wb") as f:
        f.write(conf_file.read())
    return "✅ rclone.conf salvo com sucesso!"

# 🔹 Rclone: enviar arquivo
def enviar_com_rclone(arquivo, remoto):
    nome = os.path.basename(arquivo.name)
    if not nome.endswith(".mkv"):
        return f"⚠️ Apenas arquivos .mkv são permitidos. Você enviou: {nome}"
    caminho = arquivo.name
    try:
        resultado = subprocess.run(
            ["rclone", "--config", "rclone_config/rclone.conf", "copy", caminho, f"{remoto}:/"],
            capture_output=True,
            text=True
        )
        if resultado.returncode == 0:
            os.remove(caminho)
            return f"✅ Enviado via rclone e excluído: {nome}"
        else:
            return f"❌ Erro rclone: {resultado.stderr}"
    except Exception as e:
        return f"❌ Falha ao executar rclone: {str(e)}"

# 🔹 Interface da aba Rclone
remotos_disponiveis = ["dropbox", "gdrive", "onedrive", "mega"]

with gr.Tab("☁️ Rclone"):
    gr.Markdown("Configure e envie arquivos `.mkv` via rclone")

    conf_file = gr.File(label="Upload do rclone.conf")
    status_conf = gr.Textbox(label="Status do Config", interactive=False)
    btn_conf = gr.Button("Salvar Configuração")
    btn_conf.click(fn=salvar_rclone_conf, inputs=[conf_file], outputs=[status_conf])

    remoto = gr.Radio(remotos_disponiveis, label="Escolha o serviço de nuvem")
    arquivo_mkv = gr.File(label="Escolha um arquivo .mkv")
    status_rclone = gr.Textbox(label="Status do Envio", interactive=False)
    btn_rclone = gr.Button("Enviar via Rclone")
    btn_rclone.click(fn=enviar_com_rclone, inputs=[arquivo_mkv, remoto], outputs=[status_rclone])
