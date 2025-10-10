import gradio as gr
import os

def saudacao(nome):
    return f"Olá, {nome}!"

# Captura a porta do ambiente Render
port = int(os.environ.get("PORT", 7860))

gr.Interface(
    fn=saudacao,
    inputs=gr.Textbox(label="Digite seu nome"),
    outputs=gr.Textbox(label="Mensagem de boas-vindas"),
    title="Painel Simples",
    description="Digite seu nome e receba uma saudação personalizada."
).launch(server_name="0.0.0.0", server_port=port)
