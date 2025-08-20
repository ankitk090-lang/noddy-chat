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
    color: #660022 !important;             /* dark red text */
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
    ), server_port=int(os.environ.get("PORT", 7860)))
