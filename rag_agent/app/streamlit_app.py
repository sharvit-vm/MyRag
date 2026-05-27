import streamlit as st
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()


def clean_answer(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


st.set_page_config(
    page_title="RAG Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
[data-testid="stAppViewContainer"] > .main {
    background: #0d0d14;
}
[data-testid="stAppViewContainer"] {
    background: #0d0d14;
}
section[data-testid="stSidebar"] {
    background: #111118 !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    min-width: 280px !important;
    max-width: 280px !important;
}

/* ── Hide chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }

/* ── Sidebar text ── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #a0a0b0 !important;
    font-size: 13px !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
}
[data-testid="stMetricLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.35) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #e2e0da !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.04) !important;
    color: #c8c6c0 !important;
    padding: 8px 16px !important;
    transition: all 0.18s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.18) !important;
    border-color: rgba(99,102,241,0.45) !important;
    color: #fff !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] label { color: #888 !important; }

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    margin: 0 0 12px 0 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(99,102,241,0.55) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}
textarea[data-testid="stChatInputTextArea"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 15px !important;
    color: #e2e0da !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 2px 0 !important;
    gap: 12px !important;
}
[data-testid="stChatMessageContent"] p {
    font-family: 'Syne', sans-serif !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
    color: #d4d2cc !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    margin-top: 6px !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: rgba(255,255,255,0.25) !important;
    margin-top: 4px !important;
}

/* ── HR ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 16px 0 !important; }

/* ── Alert boxes ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)


# ── System loader ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_system():
    from vectordb.chroma_store import get_vectorstore
    from agent.rag_agent import get_rag_chain
    chain, parser = get_rag_chain()
    vectordb = get_vectorstore()
    return chain, parser, vectordb


def get_doc_count(vectordb):
    try:
        return vectordb._collection.count()
    except:
        return 0


def run_ingestion(file_path: str):
    from ingestion.pipeline import ingest
    return ingest(file_path)


# ── Session state ──────────────────────────────────────────────────────────────
for key, default in {
    "messages": [],
    "cache_hits": 0,
    "cache_misses": 0,
    "total_queries": 0,
    "query_cache": {},
    "ingested_files": set(),
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo + title
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:20px 4px 24px 4px;">
        <div style="
            flex-shrink:0;
            width:40px;height:40px;
            background:linear-gradient(135deg,#6366f1,#a855f7);
            border-radius:12px;
            display:flex;align-items:center;justify-content:center;
            font-size:20px;color:white;
        ">&#9672;</div>
        <div>
            <div style="font-size:20px;font-weight:800;color:#e2e0da;
                        font-family:'Syne',sans-serif;letter-spacing:-0.02em;line-height:1.2;">
                RAG Agent
            </div>
            <div style="font-size:10px;color:rgba(255,255,255,0.28);
                        font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;">
                DOCUMENT INTELLIGENCE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # System status
    st.markdown('<p style="font-size:11px;font-family:JetBrains Mono,monospace;letter-spacing:0.1em;color:rgba(255,255,255,0.3);text-transform:uppercase;margin-bottom:12px;margin-top:0;">System Status</p>', unsafe_allow_html=True)

    with st.spinner("Loading system..."):
        try:
            chain, parser, vectordb = load_system()
            doc_count = get_doc_count(vectordb)
            system_ready = True
        except Exception as e:
            system_ready = False
            st.error(f"System error: {e}")

    if system_ready:
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:8px;">
            <div style="display:flex;align-items:center;justify-content:space-between;
                        background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.18);
                        border-radius:9px;padding:10px 14px;">
                <span style="font-size:13px;color:rgba(255,255,255,0.5);font-family:'Syne',sans-serif;">LLM</span>
                <span style="font-size:12px;color:#4ade80;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;gap:6px;">
                    <span style="width:7px;height:7px;background:#4ade80;border-radius:50%;display:inline-block;"></span>llama3
                </span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;
                        background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.18);
                        border-radius:9px;padding:10px 14px;">
                <span style="font-size:13px;color:rgba(255,255,255,0.5);font-family:'Syne',sans-serif;">Vector DB</span>
                <span style="font-size:12px;color:#4ade80;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;gap:6px;">
                    <span style="width:7px;height:7px;background:#4ade80;border-radius:50%;display:inline-block;"></span>{doc_count} chunks
                </span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;
                        background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.18);
                        border-radius:9px;padding:10px 14px;">
                <span style="font-size:13px;color:rgba(255,255,255,0.5);font-family:'Syne',sans-serif;">Embeddings</span>
                <span style="font-size:12px;color:#818cf8;font-family:'JetBrains Mono',monospace;">MiniLM-L6</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Cache stats
    st.markdown('<p style="font-size:11px;font-family:JetBrains Mono,monospace;letter-spacing:0.1em;color:rgba(255,255,255,0.3);text-transform:uppercase;margin-bottom:12px;margin-top:0;">Cache Stats</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Hits", st.session_state.cache_hits)
    with col2:
        st.metric("Misses", st.session_state.cache_misses)

    total = st.session_state.cache_hits + st.session_state.cache_misses
    hit_rate = int((st.session_state.cache_hits / total) * 100) if total > 0 else 0

    st.markdown(f"""
    <div style="margin-top:10px;background:rgba(255,255,255,0.03);
                border:1px solid rgba(255,255,255,0.07);border-radius:10px;
                padding:14px;text-align:center;">
        <div style="font-size:10px;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;
                    color:rgba(255,255,255,0.28);text-transform:uppercase;margin-bottom:6px;">
            Hit Rate
        </div>
        <div style="font-size:30px;font-weight:800;font-family:'Syne',sans-serif;
                    background:linear-gradient(135deg,#6366f1,#a855f7);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            {hit_rate}%
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Ingest
    st.markdown('<p style="font-size:11px;font-family:JetBrains Mono,monospace;letter-spacing:0.1em;color:rgba(255,255,255,0.3);text-transform:uppercase;margin-bottom:12px;margin-top:0;">Ingest Document</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop a PDF or DOCX",
        type=["pdf", "docx"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        already_done = uploaded_file.name in st.session_state.ingested_files
        if already_done:
            st.success(f"✓ Already ingested this session")
        if st.button("⟳  Ingest Document", use_container_width=True, disabled=already_done):
            save_path = f"data/docs/{uploaded_file.name}"
            os.makedirs("data/docs", exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            with st.spinner("Ingesting..."):
                try:
                    result = run_ingestion(save_path)
                    if result and result.get("status") == "skipped":
                        st.warning("Already in database — skipped.")
                        st.session_state.ingested_files.add(uploaded_file.name)
                    else:
                        chunks = result.get("chunks", "?") if result else "?"
                        st.success(f"Done — {chunks} chunks added.")
                        st.session_state.ingested_files.add(uploaded_file.name)
                        st.cache_resource.clear()
                        st.rerun()
                except Exception as e:
                    st.error(f"Ingestion failed: {e}")

    st.divider()

    if st.button("✕  Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.query_cache = {}
        st.session_state.cache_hits = 0
        st.session_state.cache_misses = 0
        st.session_state.total_queries = 0
        st.rerun()


# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:36px 0 28px 0;">
    <p style="font-size:12px;font-family:'JetBrains Mono',monospace;letter-spacing:0.15em;
              color:rgba(255,255,255,0.22);text-transform:uppercase;margin:0 0 12px 0;">
        Document Intelligence System
    </p>
    <h1 style="font-size:44px;font-weight:800;color:#e2e0da;letter-spacing:-0.03em;
               font-family:'Syne',sans-serif;line-height:1.1;margin:0;">
        Ask your
        <span style="background:linear-gradient(135deg,#6366f1,#a855f7);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            documents
        </span>
        anything.
    </h1>
</div>
""", unsafe_allow_html=True)

# Empty state
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:80px 20px 60px 20px;">
        <div style="font-size:52px;opacity:0.12;margin-bottom:16px;">&#9672;</div>
        <p style="font-size:16px;color:rgba(255,255,255,0.2);
                  font-family:'Syne',sans-serif;margin:0;">
            No questions yet — start a conversation below.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:

    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])

    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

            meta_parts = []
            if msg.get("cached"):
                meta_parts.append("⚡ cached")
            if msg.get("elapsed"):
                meta_parts.append(msg["elapsed"])
            if meta_parts:
                st.caption(" · ".join(meta_parts))

            if msg.get("sources"):
                unique_sources = list(set(
                    os.path.basename(s["source"]) for s in msg["sources"]
                ))
                with st.expander(f"📄 Sources ({len(unique_sources)})"):
                    for src in unique_sources:
                        st.markdown(f"- `{src}`")


# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything about your documents..."):
    if not system_ready:
        st.error("System not ready. Check the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.total_queries += 1

        is_cached = prompt in st.session_state.query_cache

        if is_cached:
            st.session_state.cache_hits += 1
            cached = st.session_state.query_cache[prompt]
            st.session_state.messages.append({
                "role": "assistant",
                "content": cached["answer"],
                "sources": cached["sources"],
                "cached": True,
                "elapsed": "< 1ms",
            })
        else:
            st.session_state.cache_misses += 1
            with st.spinner("Thinking..."):
                start = time.time()
                try:
                    result = chain.invoke(prompt)
                    elapsed = time.time() - start

                    if isinstance(result, dict):
                        answer = clean_answer(result.get("answer", str(result)))
                        sources = result.get("sources", [])
                    else:
                        answer = clean_answer(result.answer)
                        sources = [
                            {"content": s.content, "source": s.source}
                            for s in result.sources
                        ]

                    st.session_state.query_cache[prompt] = {
                        "answer": answer,
                        "sources": sources,
                    }
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "cached": False,
                        "elapsed": f"{elapsed:.1f}s",
                    })

                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Something went wrong: {str(e)}",
                        "sources": [],
                        "cached": False,
                        "elapsed": "",
                    })

        st.rerun()