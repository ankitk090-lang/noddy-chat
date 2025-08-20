import gradio as gr
import os
from xai import Client
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),  # Explicitly set Grok key
    base_url="https://api.x.ai/v1"
)

client = Client(api_key=os.environ.get("GROK_API_KEY"))

# Noddy's system identity
NODDY_IDENTITY = (
    "You are Noddy, a friendly AI assistant. "
    "Always refer to yourself as Noddy when introducing yourself or answering questions about your name. "
    "Your personality is cheerful, playful, and slightly mischievous like the cartoon Noddy."
)

def chat_with_noddy(message, history):
    # Convert Gradio history to OpenAI-compatible format
    messages = [{"role": "system", "content": NODDY_IDENTITY}]
    for speaker, text in history:
        if speaker == "user":
            messages.append({"role": "user", "content": text})
        else:
            messages.append({"role": "assistant", "content": text})
    messages.append({"role": "user", "content": message})

    # Send request to Grok
    response = client.chat.completions.create(
        model="grok-beta",  # Grok model
        messages=[
            {"role": "user", "content": message}
    )

    return response.choices[0].message.content

# 🎨 Custom CSS for Noddy’s softer chat bubbles
custom_css = """
.chatbot .user {
    background-color: #e6e6e6 !important;  /* light grey */
    color: #000000 !important;             /* black text */
    border-radius: 16px 16px 0px 16px !important;
    padding: 10px;
}

.chatbot .bot {
    background-color: #ffd6e7 !important;  /* soft light pink */
    color: #000000 !important;             /* black text */
    border-radius: 16px 16px 16px 0px !important;
    padding: 10px;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.ChatInterface(
        fn=chat_with_noddy,
        title="🤖 Noddy",
        description="Say hello to Noddy, your cheerful AI friend!",
        chatbot=gr.Chatbot(
            avatar_images=(
                "https://cdn-icons-png.flaticon.com/512/847/847969.png",   # user grey avatar
                "https://cdn-icons-png.flaticon.com/512/616/616408.png",   # Noddy pink avatar
            ),
            elem_classes=["chatbot"]
        ),
    )
app = demo
# Launch on Render
#demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
