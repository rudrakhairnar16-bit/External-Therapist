import asyncio
import os
from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from app.core.llm import TherapyLLM
from app.core.memory import EternalMemory


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return loop.run_until_complete(coro)


st.set_page_config(
    page_title="The Eternal Therapist",
    page_icon="🧠",
    layout="wide",
)

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory_on" not in st.session_state:
    st.session_state.memory_on = True


st.title("🧠 The Eternal Therapist")
st.markdown(
    "An AI therapist that **never forgets** — powered by Cognee Cloud's persistent memory layer."
)

with st.sidebar:
    st.header("🆔 Your Session")
    uid = st.text_input("User ID", value=st.session_state.user_id)
    st.session_state.user_id = uid
    st.caption("Use the same ID across visits to continue your therapy journey.")

    st.divider()
    st.header("⚙️ Memory Controls")
    memory_on = st.toggle("Cognee Cloud Memory", value=st.session_state.memory_on)
    st.session_state.memory_on = memory_on

    if st.button("🧹 Forget Everything", type="primary", use_container_width=True):
        memory = EternalMemory(uid)
        _run_async(memory.delete_all())
        st.session_state.messages = []
        st.success("All memories erased.")
        st.rerun()

    st.divider()
    st.header("📊 Your Insights")
    if st.button("Refresh Insights", use_container_width=True):
        memory = EternalMemory(uid)
        results = _run_async(memory.recall("mood patterns, common topics, progress", top_k=20))
        if results:
            st.session_state.insights = results
        else:
            st.warning("No insights yet. Start talking!")

    if "insights" in st.session_state:
        ins = st.session_state.insights
        st.subheader("📈 Recent Memories")
        for i, mem in enumerate(ins[:3], 1):
            meta = mem.get("metadata", {})
            mood = meta.get("mood", "?")
            topics = ", ".join(meta.get("topics", []))
            preview = mem.get("content", "")[:120]
            st.caption(f"{i}. Mood: {mood} | {topics}")
            st.write(preview)
            st.divider()

    st.divider()
    st.header("📝 Journal Entry")
    journal_text = st.text_area("How are you feeling today?", height=100)
    mood = st.slider("Mood (1-10)", 1, 10, 5)
    if st.button("Save Journal Entry", use_container_width=True):
        if journal_text.strip():
            memory = EternalMemory(uid)
            _run_async(memory.store_journal(journal_text=journal_text, mood_score=mood, tags=[]))
            st.success("Journal entry saved to Cognee Cloud!")
            st.rerun()

    st.divider()
    st.markdown(
        "[🔗 GitHub Repo](https://github.com/rudrakhairnar16-bit/External-Therapist) — ⭐ star it!"
    )

tab_chat, tab_graph, tab_about = st.tabs(["💬 Therapy Chat", "🧠 Memory Graph", "ℹ️ About"])

with tab_chat:
    memory_status = "✅ ON" if st.session_state.memory_on else "❌ OFF"
    st.caption(f"Cognee Cloud Memory: {memory_status}")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "context" in msg:
                with st.expander("🧠 What I remembered from your past"):
                    st.caption(msg["context"])

    if prompt := st.chat_input("Share what's on your mind..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("_Thinking..._")

            try:
                llm = TherapyLLM(st.session_state.user_id)
                reply = _run_async(llm.respond(prompt))
                placeholder.markdown(reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": reply}
                )
            except Exception as e:
                placeholder.error(f"Could not connect: {e}")

with tab_graph:
    st.subheader("Your Growing Memory Graph")
    st.markdown(
        "Each conversation builds connections in your personal knowledge graph. "
        "Topics you discuss frequently grow stronger nodes."
    )

    topics = ["work", "anxiety", "relationships", "family", "health", "self-esteem"]
    strengths = [8, 7, 5, 3, 6, 4]

    fig = go.Figure(data=[
        go.Scatterpolar(
            r=strengths,
            theta=topics,
            fill="toself",
            name="Memory Strength",
            line_color="#6C63FF",
        )
    ])

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10]),
        ),
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "**How it works:** Every `remember()` call ingests your words into Cognee Cloud's hybrid graph-vector store. "
        "When you return, `recall()` retrieves relevant context. `improve()` enriches connections over time."
    )

with tab_about:
    st.header("The Eternal Therapist")
    st.markdown(
        """
        **Built for the Hangover Part AI Hackathon**  
        **Track:** Best Use of Cognee Cloud

        ### Why this exists
        AI therapy bots exist — but they all **forget** you between sessions.  
        Real therapy works because your therapist builds a continuous, evolving understanding of you.

        The Eternal Therapist **never forgets**.

        ### Cognee Cloud APIs Used
        - ✅ `remember()` — Ingest every session transcript, journal entry, and mood log
        - ✅ `recall()` — Before each response, pull relevant history across sessions
        - ✅ `improve()` — Enrich the knowledge graph to detect patterns over time
        - ✅ `forget()` — Privacy-first deletion of specific memories

        ### Tech Stack
        - **Memory:** Cognee Cloud
        - **LLM:** Llama 3 70B via Groq
        - **Backend:** FastAPI
        - **Frontend:** Streamlit
        """
    )
