import gradio as gr
import google.generativeai as genai
import os
from datetime import datetime, timezone

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Noddy's system identity
NODDY_IDENTITY = (
    "You are Noddy, a friendly AI assistant. "
    "Always refer to yourself as Noddy when introducing yourself or answering questions about your name. "
    "Your personality is cheerful, playful, and slightly mischievous like the cartoon Noddy."
)

# ===== Usage tracking (resets daily UTC) =====
USAGE = {
    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    "requests": 0,
    "in_tokens": 0,
    "out_tokens": 0,
}
# If you want to hard-stop after N requests/day, set this (Gemini free ~50/day)
REQUEST_LIMIT = int(os.getenv("DAILY_REQUEST_LIMIT", "50"))  # change if you like; or set very high to disable

def _maybe_reset_usage():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if USAGE["date"] != today:
        USAGE["date"] = today
        USAGE["requests"] = 0
        USAGE["in_tokens"] = 0
        USAGE["out_tokens"] = 0

def chat_with_noddy(message, history):
    _maybe_reset_usage()

    if USAGE["requests"] >= REQUEST_LIMIT:
        return (
            "⚠️ Daily request limit reached for Noddy.\n"
            "Please try again tomorrow (UTC reset)."
        )

    # Prepare chat history for Gemini
    formatted_history = [
        {"role": "user" if m[0] == "user" else "model", "parts": [m[1]]}
        for m in history
    ]
    if not formatted_history or formatted_history[0]["parts"][0] != NODDY_IDENTITY:
        formatted_history.insert(0, {"role": "user", "parts": [NODDY_IDENTITY]})

    chat = model.start_chat(history=formatted_history)
    response = chat.send_message(message)

    # Accurate token counts from Gemini
    usage = getattr(response, "usage_metadata", None)
    in_tok = getattr(usage, "prompt_token_count", 0) if usage else 0
    out_tok = getattr(usage, "candidates_token_count", 0) if usage else 0

    # Update daily usage
    USAGE["requests"] += 1
    USAGE["in_tokens"] += in_tok
    USAGE["out_tokens"] += out_tok

    usage_footer = (
        f"\n\n---\n"
        f"📅 {USAGE['date']} (UTC)\n"
        f"🧮 Request #{USAGE['requests']} | "
        f"📥 Input tokens: {in_tok} | 📤 Output tokens: {out_tok}\n"
        f"📊 Totals today → In: {USAGE['in_tokens']} | Out: {USAGE['out_tokens']}\n"
        f"🔒 Daily request limit: {REQUEST_LIMIT}"
    )

    return (response.text or "").strip() + usage_footer

# 🎨 Custom CSS for Noddy’s softer chat bubbles (unchanged)
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
    )

# Launch on Render's PORT (default 7860 for local)
demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
