import streamlit as st
from groq import Groq
import os
import time
from dotenv import load_dotenv
from datetime import datetime
import io
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

embedder = load_embedder()

def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        return uploaded_file.read().decode("utf-8")
    
def chunk_text(text, chunk_size=400, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words),chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks 

def build_vector_store(chunks):
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(
        name = f"nova_rag_{int(time.time())}"
    )
    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        embeddings=embedder.encode(chunks).tolist(),
    )
    return collection

def retrieve_context(query, collection, top_k=3):
    query_emb = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=query_emb, n_results=top_k)
    return "\n\n".join(results["documents"][0])

st.set_page_config(
    page_title="Nova AI",
    page_icon="✦",
    layout="wide",                   
    initial_sidebar_state="collapsed",
)

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

if "messages"  not in st.session_state: st.session_state.messages  = []
if "history"   not in st.session_state: st.session_state.history   = []

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
    st.markdown("### ✦ Knowledge (RAG)")
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt"])

    if uploaded_file:
        if st.session_state.get("rag_file_name") != uploaded_file.name:
            with st.spinner("Indexing document..."):
                text = extract_text(uploaded_file)
                chunks = chunk_text(text)
                st.session_state.rag_collection = build_vector_store(chunks)
                st.session_state.rag_file_name = uploaded_file.name
            st.success(f"Indexed {len(chunks)} chunks from {uploaded_file.name}")
    else:
        st.session_state.pop("rag_collection", None)
        st.session_state.pop("rag_file_name", None)            

    st.markdown("---")
    n = len(st.session_state.messages)
    st.markdown(f"<p>{n} message{'s' if n!=1 else ''}</p>", unsafe_allow_html=True)

st.markdown(f"""
<div class="nova-header">
  <div class="nova-logo">✦ {bot_name}</div>
  <div class="nova-sub">Powered by Groq &nbsp;·&nbsp; Fast Inference</div>
  <div class="nova-divider"></div>
</div>
""", unsafe_allow_html=True)

if "rag_file_name" in st.session_state:
    st.markdown(
        f"<p style='text-align:center;color:var(--accent);font-size:.75rem;'>"
        f"📄 Answering from: {st.session_state.rag_file_name}</p>",
        unsafe_allow_html=True,
    )
    
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

if prompt := st.chat_input("Send a message…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            api_messages = [{"role": "system", "content": system_prompt}]

            if "rag_collection" in st.session_state:
                context = retrieve_context(prompt, st.session_state.rag_collection)
                rag_instruction = (
                    "Use the following document excerpts to answer the user's "
                    "question. If the answer isn't in the excerpts, say so honestly "
                    "instead of guessing.\n\n"
                    f"DOCUMENT EXCERPTS:\n{context}"
                )
                api_messages.append({"role": "system", "content": rag_instruction})

            api_messages.extend(st.session_state.messages)

            response = client.chat.completions.create(
                model=model_choice,
                temperature=temperature,
                messages=api_messages,
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