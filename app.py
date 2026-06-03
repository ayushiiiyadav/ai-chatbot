import streamlit as st
from groq import Groq
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="Nova AI",
    page_icon="✦",
    layout="wide",                    # KEY FIX — wide kills the side gutter columns
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  STYLES + CANVAS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=DM+Sans:wght@300;400;500&display=swap');

:root{
    --bg:#07060f;
    --card:#12101e;
    --accent:#c084fc;
    --pink:#f472b6;
    --text:#f0eaff;
    --muted:#6b6385;

    --chat-width:760px;
}

/* Base */
html,
body,
.stApp{
    background:var(--bg)!important;
    color:var(--text)!important;
}

/* Hide Streamlit chrome */
#MainMenu,
footer,
header,
[data-testid="stToolbar"]{
    display:none!important;
}

/* Main content */
.block-container{
    display:flex!important;
    flex-direction:column!important;

    width:min(var(--chat-width),95vw)!important;
    margin:auto!important;

    padding-top:1rem!important;
    padding-bottom:7rem!important;
}

/* Assistant messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) span,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) li{
    color:#F5F0FF !important; /* Bright lavender-white */
}

/* User messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) span,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) li{
    color:#E0E7FF !important; /* Soft indigo */
}

/* Bottom area */
[data-testid="stBottom"]{
    display:flex!important;

    justify-content:center!important;

    background:var(--bg)!important;

    border-top:1px solid rgba(192,132,252,.12)!important;
}

/* Critical fix */
[data-testid="stChatInputContainer"]{
    width:min(var(--chat-width),95vw)!important;

    margin:auto!important;
}

/* Chat input */
[data-testid="stChatInput"]{
    background:#ffffff!important;
    border:1px solid rgba(0,0,0,.15)!important;
}

[data-testid="stChatInput"] textarea{
    color:#000000!important;
}

/* Header */
.nova-header{
    text-align:center;
    margin:3rem 0;
}

.nova-logo{
    font-size:3rem;
    font-weight:300;
    letter-spacing:.05em;
}

.nova-sub{
    color:var(--muted);
    font-size:.7rem;
    letter-spacing:.2em;
}
</script>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages"  not in st.session_state: st.session_state.messages  = []
if "history"   not in st.session_state: st.session_state.history   = []

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ✦ Settings")
    st.markdown("---")

    bot_name = st.text_input("Bot Name", value="Nova AI")

    model_choice = st.selectbox("Model", [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ])

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)

    system_prompt = st.text_area(
        "Personality",
        value="You are Nova, a warm, witty and intelligent AI assistant. Be concise, helpful and precise.",
        height=100,
    )

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Save"):
            if st.session_state.messages:
                title = next(
                    (m["content"][:38] for m in st.session_state.messages if m["role"]=="user"),
                    "Conversation"
                )
                st.session_state.history.append({
                    "title": title,
                    "messages": list(st.session_state.messages),
                    "ts": datetime.now().strftime("%H:%M"),
                })
                st.toast("Chat saved ✦")
    with c2:
        if st.button("🗑 Clear"):
            st.session_state.messages = []
            st.rerun()

    if st.session_state.history:
        st.markdown("---")
        st.markdown("### ✦ History")
        for i, item in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - 1 - i
            label = item["title"] + ("…" if len(item["title"]) == 38 else "")
            if st.button(f"↩ {label}", key=f"h{idx}"):
                st.session_state.messages = list(item["messages"])
                st.rerun()

    st.markdown("---")
    n = len(st.session_state.messages)
    st.markdown(f"<p>{n} message{'s' if n!=1 else ''}</p>", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="nova-header">
  <div class="nova-logo">✦ {bot_name}</div>
  <div class="nova-sub">Powered by Groq &nbsp;·&nbsp; Fast Inference</div>
  <div class="nova-divider"></div>
</div>
""", unsafe_allow_html=True)

# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
      <span class="empty-icon">✦</span>
      <div class="empty-text">How can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)

# ── MESSAGES ──────────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── INPUT ─────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Send a message…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            response = client.chat.completions.create(
                model=model_choice,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages,
                ],
            )
            reply = response.choices[0].message.content

        placeholder = st.empty()
        displayed = ""
        for char in reply:
            displayed += char
            placeholder.markdown(displayed + "▌")
            time.sleep(0.007)
        placeholder.markdown(displayed)

    st.session_state.messages.append({"role": "assistant", "content": reply})