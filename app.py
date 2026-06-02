import streamlit as st
from groq import Groq
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="Nova AI",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Inter:wght@300;400;500&display=swap');

:root {
  --bg:      #07060f;
  --surface: #0e0c1a;
  --card:    #12101e;
  --border:  rgba(192,132,252,0.12);
  --accent:  #c084fc;
  --pink:    #f472b6;
  --indigo:  #818cf8;
  --text:    #f0eaff;
  --muted:   #5a4f76;
  --glow:    rgba(192,132,252,0.14);
}

*, *::before, *::after { box-sizing: border-box; }

/* ── KILL ALL WHITE BACKGROUNDS ── */
html, body,
.stApp,
.stApp > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
.main, .main > div,
section[data-testid="stSidebar"] ~ div,
div[class*="appview"],
div[class*="main"] {
  background: var(--bg) !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── BOTTOM INPUT AREA — force dark ── */
[data-testid="stBottom"] {
  background: var(--bg) !important;
  background-color: var(--bg) !important;
  border-top: 1px solid var(--border) !important;
  padding: 1rem 0 1.2rem !important;
  position: relative;
  z-index: 10;
}
[data-testid="stBottomBlockContainer"] {
  background: var(--bg) !important;
  padding-bottom: 0 !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
  background: var(--card) !important;
  border: 1px solid rgba(192,132,252,0.25) !important;
  border-radius: 14px !important;
  transition: border-color 0.25s, box-shadow 0.25s !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: rgba(192,132,252,0.55) !important;
  box-shadow: 0 0 0 3px var(--glow) !important;
}
[data-testid="stChatInput"] textarea {
  background: var(--card) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.92rem !important;
  caret-color: var(--accent) !important;
  border: none !important;
  outline: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
  color: var(--muted) !important;
  font-style: italic !important;
}
[data-testid="stChatInput"] button {
  background: linear-gradient(135deg, var(--accent), var(--pink)) !important;
  border: none !important;
  border-radius: 9px !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"] button:hover {
  transform: scale(1.1) !important;
  box-shadow: 0 4px 18px rgba(192,132,252,0.4) !important;
}
[data-testid="stChatInput"] button svg { fill: white !important; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
.stDeployButton { display: none !important; visibility: hidden !important; }

/* ── MAIN CONTAINER ── */
.block-container {
  max-width: 740px !important;
  padding: 0 1.5rem 5rem !important;
  margin: 0 auto !important;
}

/* ── HEADER ── */
.nova-header {
  text-align: center;
  padding: 3rem 0 1.2rem;
  animation: fadeDown 0.8s ease both;
}
.nova-logo {
  font-family: 'Cormorant Garamond', serif;
  font-size: 3rem;
  font-weight: 300;
  letter-spacing: 0.06em;
  background: linear-gradient(120deg, var(--accent) 0%, var(--pink) 55%, var(--indigo) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}
.nova-sub {
  font-size: 0.68rem;
  letter-spacing: 0.2em;
  color: var(--muted);
  text-transform: uppercase;
  margin-top: 0.4rem;
}
.nova-divider {
  width: 50px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  margin: 1rem auto 0;
}
@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── EMPTY STATE ── */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  animation: fadeDown 1s ease both;
}
.empty-icon {
  font-size: 1.8rem;
  display: block;
  margin-bottom: 0.8rem;
  animation: starPulse 3s ease-in-out infinite;
  color: var(--accent);
}
.empty-text {
  font-family: 'Cormorant Garamond', serif;
  font-style: italic;
  font-size: 1.05rem;
  color: var(--muted);
}
@keyframes starPulse {
  0%,100% { opacity:0.5; transform:scale(1) rotate(0deg); }
  50%     { opacity:1;   transform:scale(1.15) rotate(20deg); }
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 1rem 1.2rem !important;
  margin: 0.45rem 0 !important;
  animation: msgIn 0.32s cubic-bezier(.34,1.4,.64,1) both !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: linear-gradient(135deg, rgba(129,140,248,0.09), rgba(192,132,252,0.05)) !important;
  border-color: rgba(129,140,248,0.2) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
  background: linear-gradient(135deg, rgba(192,132,252,0.06), rgba(244,114,182,0.08)) !important;
  border-color: rgba(244,114,182,0.18) !important;
}
[data-testid="stChatMessage"] p {
  color: var(--text) !important;
  font-size: 0.92rem !important;
  line-height: 1.7 !important;
}
@keyframes msgIn {
  from { opacity:0; transform:translateY(10px) scale(0.97); }
  to   { opacity:1; transform:translateY(0)    scale(1); }
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 265px !important;
  max-width: 265px !important;
  overflow: hidden !important;
}
[data-testid="stSidebarContent"] {
  padding: 1.8rem 1.4rem !important;
  overflow-x: hidden !important;
}
[data-testid="stSidebar"] * {
  writing-mode: horizontal-tb !important;
  overflow-wrap: break-word !important;
}
[data-testid="stSidebar"] h3 {
  font-family: 'Cormorant Garamond', serif !important;
  font-weight: 400 !important;
  font-size: 1.1rem !important;
  color: var(--accent) !important;
  letter-spacing: 0.05em !important;
}
[data-testid="stSidebar"] label {
  font-size: 0.7rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
  display: block !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important;
  color: var(--text) !important;
  font-size: 0.87rem !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important;
  color: var(--text) !important;
}
[data-testid="stSidebar"] hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 1rem 0 !important;
}
[data-testid="stSidebar"] p {
  color: var(--muted) !important;
  font-size: 0.75rem !important;
  text-align: center !important;
}

/* ── SIDEBAR TOGGLE BUTTON — bright & always visible ── */
[data-testid="collapsedControl"] {
  background: linear-gradient(160deg, var(--accent), var(--pink)) !important;
  border-radius: 0 12px 12px 0 !important;
  box-shadow: 4px 0 20px rgba(192,132,252,0.4) !important;
  border: none !important;
  opacity: 1 !important;
  visibility: visible !important;
  z-index: 9999 !important;
  width: 28px !important;
}
[data-testid="collapsedControl"] svg {
  fill: white !important;
  color: white !important;
}

/* ── CLEAR BUTTON ── */
.stButton > button {
  width: 100% !important;
  background: transparent !important;
  color: var(--muted) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important;
  font-size: 0.79rem !important;
  letter-spacing: 0.07em !important;
  padding: 0.5rem !important;
  transition: all 0.25s !important;
}
.stButton > button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  box-shadow: 0 0 14px var(--glow) !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(var(--accent), var(--pink));
  border-radius: 3px;
}

/* ── STAR + ORB LAYERS ── */
#nova-bg {
  position: fixed; inset: 0;
  pointer-events: none; z-index: 0;
}
.orb {
  position: fixed; border-radius: 50%;
  pointer-events: none; z-index: 0; filter: blur(90px);
}
.orb1 {
  width:520px; height:520px; top:-130px; right:-100px;
  background: radial-gradient(circle, rgba(192,132,252,0.09) 0%, transparent 65%);
  animation: drift 13s ease-in-out infinite;
}
.orb2 {
  width:420px; height:420px; bottom:-110px; left:-90px;
  background: radial-gradient(circle, rgba(244,114,182,0.07) 0%, transparent 65%);
  animation: drift 17s ease-in-out infinite reverse;
}
@keyframes drift {
  0%,100% { transform: translate(0,0); }
  50%     { transform: translate(-25px, 35px); }
}
</style>

<!-- BACKGROUND LAYERS -->
<div class="orb orb1"></div>
<div class="orb orb2"></div>
<canvas id="nova-bg"></canvas>

<script>
// Wait for DOM then run star animation
(function boot() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    const c = document.getElementById('nova-bg');
    if (!c) { setTimeout(init, 200); return; }
    const ctx = c.getContext('2d');

    function resize() {
      c.width  = window.innerWidth;
      c.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // 140 twinkling stars
    const stars = Array.from({length: 140}, () => ({
      x:     Math.random(),
      y:     Math.random(),
      r:     Math.random() * 1.3 + 0.2,
      base:  Math.random() * 0.55 + 0.15,
      speed: Math.random() * 0.012 + 0.004,
      phase: Math.random() * Math.PI * 2,
    }));

    // 40 coloured dust particles
    const COLS = ['192,132,252','244,114,182','129,140,248'];
    const dust = Array.from({length: 40}, () => ({
      x:   Math.random() * window.innerWidth,
      y:   Math.random() * window.innerHeight,
      r:   Math.random() * 1.6 + 0.3,
      dx:  (Math.random() - 0.5) * 0.28,
      dy:  (Math.random() - 0.5) * 0.28,
      a:   Math.random() * 0.4 + 0.08,
      col: COLS[Math.floor(Math.random() * 3)],
    }));

    // Shooting star state
    let shoot = null;
    let frame = 0;

    function spawnShoot() {
      const sx = Math.random() * c.width  * 0.5 + 50;
      const sy = Math.random() * c.height * 0.35 + 30;
      shoot = { x: sx, y: sy, len: 0, maxLen: 160,
                angle: Math.PI / 5, alpha: 1 };
    }

    function draw() {
      ctx.clearRect(0, 0, c.width, c.height);
      frame++;

      // Twinkling stars
      stars.forEach(s => {
        const t = Math.sin(frame * s.speed + s.phase) * 0.42 + 0.58;
        ctx.beginPath();
        ctx.arc(s.x * c.width, s.y * c.height, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${s.base * t})`;
        ctx.fill();
      });

      // Dust
      dust.forEach(p => {
        p.x += p.dx; p.y += p.dy;
        if (p.x < 0 || p.x > c.width)  p.dx *= -1;
        if (p.y < 0 || p.y > c.height) p.dy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.col},${p.a})`;
        ctx.fill();
      });

      // Shooting star
      if (frame % 240 === 0) spawnShoot();
      if (shoot) {
        shoot.len += 8;
        shoot.alpha = 1 - shoot.len / shoot.maxLen;
        const ex = shoot.x + Math.cos(shoot.angle) * shoot.len;
        const ey = shoot.y + Math.sin(shoot.angle) * shoot.len;
        const g  = ctx.createLinearGradient(shoot.x, shoot.y, ex, ey);
        g.addColorStop(0,   `rgba(255,255,255,0)`);
        g.addColorStop(0.3, `rgba(192,132,252,${shoot.alpha * 0.8})`);
        g.addColorStop(1,   `rgba(255,255,255,${shoot.alpha})`);
        ctx.beginPath();
        ctx.moveTo(shoot.x, shoot.y);
        ctx.lineTo(ex, ey);
        ctx.strokeStyle = g;
        ctx.lineWidth   = 1.5;
        ctx.stroke();
        if (shoot.len >= shoot.maxLen) shoot = null;
      }

      requestAnimationFrame(draw);
    }
    draw();
  }
})();
</script>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ✦ Settings")
    st.markdown("---")
    bot_name      = st.text_input("Bot Name", value="Nova AI")
    model_choice  = st.selectbox("Model", [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ])
    system_prompt = st.text_area(
        "Bot Personality",
        value="You are Nova, a warm, witty and intelligent AI assistant. Be concise, helpful and precise.",
        height=110,
    )
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    count = len(st.session_state.get("messages", []))
    st.markdown(f"<p>{count} messages</p>", unsafe_allow_html=True)

st.markdown("""
<div class="nova-header">
  <div class="nova-logo">✦ Nova AI</div>
  <div class="nova-sub">Powered by Groq &nbsp;·&nbsp; Fast Inference</div>
  <div class="nova-divider"></div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
      <span class="empty-icon">✦</span>
      <div class="empty-text">How can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Send a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            response = client.chat.completions.create(
                model=model_choice,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages,
                ],
            )
            reply = response.choices[0].message.content

        placeholder = st.empty()
        displayed   = ""
        for char in reply:
            displayed += char
            placeholder.markdown(displayed + "▌")
            time.sleep(0.007)
        placeholder.markdown(displayed)

    st.session_state.messages.append({"role": "assistant", "content": reply})