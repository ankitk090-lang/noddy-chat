import os
import re
from datetime import datetime, timezone

import gradio as gr
import google.generativeai as genai

# =========================
# Gemini setup
# =========================
NODDY_IDENTITY = (
    "You are Noddy, a friendly AI assistant. "
    "Always refer to yourself as Noddy when introducing yourself or answering questions about your name. "
    "Your personality is cheerful, playful, and slightly mischievous like the cartoon Noddy."
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=NODDY_IDENTITY,  # ✅ identity set once, not in history every turn
)

# =========================
# Usage tracking (resets daily UTC)
# =========================
USAGE = {
    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    "requests": 0,
    "in_tokens": 0,
    "out_tokens": 0,
}
REQUEST_LIMIT = int(os.getenv("DAILY_REQUEST_LIMIT", "50"))  # Gemini free ≈ 50 req/day

USAGE_SPLIT = "\n---\n"  # marker for stripping usage footer

def _maybe_reset_usage():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if USAGE["date"] != today:
        USAGE["date"] = today
        USAGE["requests"] = 0
        USAGE["in_tokens"] = 0
        USAGE["out_tokens"] = 0

def _strip_usage_footer(text: str) -> str:
    # Remove anything we appended after our marker to avoid re-sending it
    return text.split(USAGE_SPLIT, 1)[0].strip()

def _to_gemini_history(history):
    """
    Convert Gradio Chatbot(type='messages') history -> Gemini format
    history is a list of dicts: {'role': 'user'|'assistant', 'content': '...'}
    """
    gem_hist = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        content = _strip_usage_footer(m.get("content", ""))
        if content:
            gem_hist.append({"role": role, "parts": [content]})
    return gem_hist

def chat_with_noddy(message, history):
    _maybe_reset_usage()

    if USAGE["requests"] >= REQUEST_LIMIT:
        return (
            "⚠️ Daily request limit reached for Noddy.\n"
            "Please try again tomorrow (UTC reset)."
        )

    # Build clean history (no previous usage footers)
    formatted_history = _to_gemini_history(history)

    # Chat with Gemini
    chat = model.start_chat(history=formatted_history)
    response = chat.send_message(str(message))

    # Accurate token usage for THIS turn
    usage = getattr(response, "usage_metadata", None)
    in_tok = int(getattr(usage, "prompt_token_count", 0) or 0)
    out_tok = int(getattr(usage, "candidates_token_count", 0) or 0)

    # Update daily counters
    USAGE["requests"] += 1
    USAGE["in_tokens"] += in_tok
    USAGE["out_tokens"] += out_tok

    # Append a small footer (will be stripped on next turn)
    usage_footer = (
        f"{USAGE_SPLIT}"
        f"📅 {USAGE['date']} (UTC)\n"
        f"🧮 Request #{USAGE['requests']} | 📥 Input tokens: {in_tok} | 📤 Output tokens: {out_tok}\n"
        f"📊 Totals today → In: {USAGE['in_tokens']} | Out: {USAGE['out_tokens']}\n"
        f"🔒 Daily request limit: {REQUEST_LIMIT}"
    )

    return ((response.text or "").strip() + usage_footer)

# =========================
# UI (light grey user, light pink Noddy, black text)
# =========================
custom_css = """
.chatbot .user {
    background-color: #e6e6e6 !important;
    color: #000000 !important;
    border-radius: 16px 16px 0px 16px !important;
    padding: 10px;
}

.chatbot .bot {
    background-color: #ffd6e7 !important;
    color: #000000 !important;
    border-radius: 16px 16px 16px 0px !important;
    padding: 10px;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as app:
    gr.ChatInterface(
        fn=chat_with_noddy,
        title="🤖 Noddy",
        description="Say hello to Noddy, your cheerful AI friend!",
        chatbot=gr.Chatbot(
            type="messages",  # ✅ use messages format to avoid deprecation & double handling
            avatar_images=(
                "https://cdn-icons-png.flaticon.com/512/847/847969.png",   # user
                "https://cdn-icons-png.flaticon.com/512/616/616408.png",   # Noddy
            ),
            elem_classes=["chatbot"]
        ),
    )

# Render: bind to assigned PORT
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
