import streamlit as st
from groq import Groq
import os
import time
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
/* Background */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0a0a1a 100%);
    color: #e0e0e0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #120a2e 0%, #0d0d1a 100%);
    border-right: 1px solid #7c3aed44;
}

/* Title */
h1 {
    background: linear-gradient(90deg, #7c3aed, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    text-align: center;
    padding: 1rem 0;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: #1a1a2e !important;
    color: #e0e0e0 !important;
    border: 1px solid #7c3aed !important;
    border-radius: 12px !important;
}

/* User message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #1e1b4b, #312e81) !important;
    border: 1px solid #4f46e5 !important;
    border-radius: 16px !important;
    padding: 12px !important;
    margin: 8px 0 !important;
}

/* Assistant message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #2d1b69, #1e1040) !important;
    border: 1px solid #7c3aed !important;
    border-radius: 16px !important;
    padding: 12px !important;
    margin: 8px 0 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100%;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #6d28d9, #9333ea) !important;
    transform: scale(1.02);
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #c4b5fd !important;
}

/* Selectbox & Slider */
[data-testid="stSidebar"] .stSelectbox > div,
[data-testid="stSidebar"] .stSlider {
    background: #1a1040 !important;
    border-radius: 8px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a1a; }
::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    bot_name = st.text_input("🤖 Bot Name", value="Nova AI")

    model_choice = st.selectbox("🧠 Model", [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ])

    temperature = st.slider("🌡️ Creativity", 0.0, 1.0, 0.7, 0.1)

    system_prompt = st.text_area("📝 Bot Personality",
        value="You are a helpful, smart and friendly AI assistant.",
        height=100
    )

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**💬 Messages:**")
    st.markdown(f"`{len(st.session_state.get('messages', []))}` in history")

# ─── Main Area ────────────────────────────────────────────
st.title(f"✨ {bot_name}")
st.markdown("<p style='text-align:center; color:#a855f7; margin-top:-15px;'>Powered by Groq • Fast AI</p>", unsafe_allow_html=True)
st.markdown("---")

# ─── Session State ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Chat History Display ─────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ─── Input & Response ─────────────────────────────────────
if prompt := st.chat_input(f"Ask {bot_name} anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("✨ Thinking..."):
            time.sleep(0.3)

            response = client.chat.completions.create(
                model=model_choice,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ]
            )

            reply = response.choices[0].message.content

        # Typing animation
        placeholder = st.empty()
        displayed = ""
        for char in reply:
            displayed += char
            placeholder.markdown(displayed + "▌")
            time.sleep(0.008)
        placeholder.markdown(displayed)

    st.session_state.messages.append({"role": "assistant", "content": reply})