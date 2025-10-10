import gradio as gr

def baixar_e_gerenciar_automatico(magnet):
    # Aqui você pode colocar sua lógica real de download
    # Por enquanto, vamos simular uma resposta
    return f"Recebido magnet link: {magnet}\nDownload iniciado..."

gr.Interface(
    fn=baixar_e_gerenciar_automatico,
    inputs=gr.Textbox(label="🔗 Magnet Link"),
    outputs=gr.Textbox(label="📦 Status do Download"),
    title="Painel de Torrents",
    description="Insira o link magnet para baixar arquivos automaticamente."
).launch()
