import gradio as gr
import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

# Noddy's system identity
NODDY_IDENTITY = (
    "You are Noddy, a friendly AI assistant. "
    "Always refer to yourself as Noddy when introducing yourself or answering questions about your name. "
    "Your personality is cheerful, playful, and slightly mischievous like the cartoon Noddy."
)

def chat_with_noddy(message, history):
    formatted_history = [
        {"role": "user" if m[0] == "user" else "model", "parts": [m[1]]}
        for m in history
    ]

    if not formatted_history or formatted_history[0]["parts"][0] != NODDY_IDENTITY:
        formatted_history.insert(0, {"role": "user", "parts": [NODDY_IDENTITY]})

    chat = model.start_chat(history=formatted_history)
    response = chat.send_message(message)
    return response.text

# 🎨 Custom CSS for Noddy’s red-themed chat bubbles
custom_css = """
.chatbot .user {
    background-color: #ffe0e0 !important;
    color: #4a0000 !important;
    border-radius: 16px 16px 0px 16px !important;
    padding: 10px;
}
.chatbot .bot {
    background-color: #ff4d4d !important;
    color: white !important;
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
            avatar_images=("👤", "🎩"),  # 👤 User, 🎩 Noddy (hat icon like Noddy’s hat)
            bubble_full_width=False,
            elem_classes=["chatbot"]
        ),
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
