import gradio as gr
import os
import requests
import traceback

# Carrega variáveis de ambiente (sempre strip)
token_telegram = os.getenv("TELEGRAM_TOKEN", "").strip()
chat_id = os.getenv("CHAT_ID", "").strip()

def _append_log(text: str):
    print(text, flush=True)
    try:
        with open("telegram_debug.log", "a", encoding="utf-8") as f:
            f.write(text + "\n" + ("-"*60) + "\n")
    except Exception:
        pass

def enviar_mensagem_telegram(texto: str) -> str:
    try:
        logs = []
        logs.append(f"INPUT: {repr(texto)}")
        logs.append(f"TOKEN_PRESENT: {bool(token_telegram)}")
        logs.append(f"CHAT_ID_RAW: {repr(chat_id)}")

        if not texto or not texto.strip():
            logs.append("RESULT: Mensagem vazia")
            resultado = "\n".join(logs)
            _append_log(resultado)
            return resultado

        if not token_telegram or not chat_id:
            logs.append("RESULT: Variáveis de ambiente ausentes")
            resultado = "\n".join(logs)
            _append_log(resultado)
            return resultado

        try:
            chat_id_int = int(chat_id)
            logs.append(f"CHAT_ID_INT: {chat_id_int}")
        except Exception as e:
            logs.append(f"CHAT_ID_PARSE_ERROR: {e}")
            resultado = "\n".join(logs)
            _append_log(resultado)
            return resultado

        url = f"https://api.telegram.org/bot{token_telegram}/sendMessage"
        payload = {"chat_id": chat_id_int, "text": texto}
        logs.append(f"CALL_URL: {url}")
        logs.append(f"PAYLOAD: {payload}")

        try:
            response = requests.post(url, data=payload, timeout=15)
            logs.append(f"HTTP_STATUS: {response.status_code}")
            logs.append(f"HTTP_TEXT: {response.text}")
            if response.ok:
                logs.append("RESULT: Enviado com sucesso")
            else:
                logs.append("RESULT: Erro ao enviar")
        except Exception as e:
            logs.append(f"REQUEST_EXCEPTION: {repr(e)}")

        resultado = "\n".join(logs)
        _append_log(resultado)
        return resultado

    except Exception as e:
        tb = traceback.format_exc()
        resultado = f"EXCEPTION: {str(e)}\n{tb}"
        _append_log(resultado)
        return resultado

with gr.Blocks(title="Debug Telegram") as demo:
    texto = gr.Textbox(label="Mensagem")
    status = gr.Textbox(label="Status", lines=14, interactive=False)
    enviar = gr.Button("Enviar")
    enviar.click(fn=enviar_mensagem_telegram, inputs=[texto], outputs=[status])

port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
