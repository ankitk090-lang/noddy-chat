import os
import gradio as gr
import google.generativeai as genai

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
    # Convert gradio history into Gemini format
    formatted_history = [{"role": "user", "parts": [NODDY_IDENTITY]}]

    for user_msg, bot_msg in history:
        if user_msg:
            formatted_history.append({"role": "user", "parts": [user_msg]})
        if bot_msg:
            formatted_history.append({"role": "model", "parts": [bot_msg]})

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
            elem_classes=["chatbot"],
            avatar_images=(
                "https://cdn-icons-png.flaticon.com/512/847/847969.png",  # user avatar
                "https://cdn-icons-png.flaticon.com/512/616/616408.png",  # Noddy avatar
            ),
        ),
    )

# 🚀 Launch (Render compatible)
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860))
    )
