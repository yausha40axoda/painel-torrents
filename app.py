import os

port = int(os.environ.get("PORT", 7860))

gr.Interface(
    fn=baixar_e_gerenciar_automatico,
    inputs=gr.Textbox(label="🔗 Magnet Link"),
    outputs=gr.Textbox(label="📦 Status do Download"),
    title="Painel de Torrents",
    description="Insira o link magnet para baixar, enviar para Dropbox e Telegram automaticamente."
).launch(server_name="0.0.0.0", server_port=port)
