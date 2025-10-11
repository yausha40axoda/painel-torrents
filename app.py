import gradio as gr
import os
import requests
import traceback

token_telegram = os.getenv("TELEGRAM_TOKEN", "").strip()
chat_id = os.getenv("CHAT_ID", "").strip()

def enviar_mensagem_telegram(texto: str) -> str:
    try:
        log_lines = []
        log_lines.append(f"INPUT: {repr(texto)}")
        log_lines.append(f"TOKEN_PRESENT: {bool(token_telegram)}")
        log_lines.append(f"CHAT_ID_RAW: {repr(chat_id)}")

        if not texto or not texto.strip():
            log_lines.append("RESULT: Mensagem vazia")
            mensagem = "\n".join(log_lines)
            _append_log(mensagem)
            return mensagem

        if not token_telegram or not chat_id:
            log_lines.append("RESULT: Variáveis de ambiente ausentes")
            mensagem = "\n".join(log_lines)
            _append_log(mensagem)
            return mensagem

        try:
            chat_id_int = int(chat_id)
        except Exception as e:
            log_lines.append(f"CHAT_ID_PARSE_ERROR: {e}")
            mensagem = "\n".join(log_lines)
            _append_log(mensagem)
            return mensagem

        url = f"https://api.telegram.org/bot{token_telegram}/sendMessage"
        payload = {"chat_id": chat_id_int, "text": texto}
        log_lines.append(f"CALL_URL: {url}")
        log_lines.append(f"PAYLOAD: {payload}")

        response = requests.post(url, data=payload, timeout=15)
        log_lines.append(f"HTTP_STATUS: {response.status_code}")
        log_lines.append(f"HTTP_TEXT: {response.text}")

        if response.ok:
            log_lines.append("RESULT: Enviado com sucesso")
        else:
            log_lines.append("RESULT: Erro ao enviar")

        mensagem = "\n".join(log_lines)
        _append_log(mensagem)
        return mensagem

    except Exception as e:
        tb = traceback.format_exc()
        mensagem = f"EXCEPTION: {str(e)}\n{tb}"
        _append_log(mensagem)
        return mensagem

def _append_log(text: str):
    print(text, flush=True)
    try:
        with open("telegram_debug.log", "a", encoding="utf-8") as f:
            f.write(text + "\n" + ("-"*60) + "\n")
    except Exception:
        pass

with gr.Blocks(title="Debug Telegram") as demo:
    texto = gr.Textbox(label="Mensagem")
    status = gr.Textbox(label="Status", lines=12, interactive=False)
    enviar = gr.Button("Enviar")
    enviar.click(fn=enviar_mensagem_telegram, inputs=[texto], outputs=[status])

port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
