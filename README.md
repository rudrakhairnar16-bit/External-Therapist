# 🧠 The Eternal Therapist

> An AI therapy companion that **never forgets** — built with Cognee Cloud persistent memory and Groq's Llama 3 70B.

[![Hackathon](https://img.shields.io/badge/Hackathon-Hangover%20Part%20AI-6C63FF)](https://hangoverpartai.com)
[![Track](https://img.shields.io/badge/Track-Best%20Use%20of%20Cognee%20Cloud-00D4AA)](https://cognee.ai)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://external-therapist.streamlit.app)

---

## 🔗 Links

| | |
|---|---|
| 🌐 **Live App** | [external-therapist.streamlit.app](https://external-therapist.streamlit.app) |
| 📖 **Blog Post** | [contextos-second-brain-for-developer.hashnode.dev](https://contextos-second-brain-for-developer.hashnode.dev/the-eternal-therapist-building-an-ai-that-actually-remembers) |
| 🎥 **Demo Video** | [youtu.be/wGF6Dl9Q2zc](https://youtu.be/wGF6Dl9Q2zc) |
| 💻 **GitHub Repo** | [github.com/rudrakhairnar16-bit/External-Therapist](https://github.com/rudrakhairnar16-bit/External-Therapist) |
| 🔗 **LinkedIn** | [linkedin.com/in/rudra-khaire-2657a5381](https://www.linkedin.com/in/rudra-khaire-2657a5381) |

---

## 🏆 The Problem

AI therapy bots exist — but they all **forget** you between sessions. Real therapy works because your therapist builds a continuous, evolving understanding of who you are. Every insight from last week informs today's conversation.

The Eternal Therapist solves this with **Cognee Cloud's persistent memory layer**. Every chat, journal entry, and mood log is stored in a hybrid graph-vector database. When you come back, your therapist remembers everything.

## ✨ Features

- **Persistent Memory** — `remember()` ingests every session; `recall()` retrieves relevant context across visits
- **Intelligent Responses** — Llama 3 70B via Groq, informed by your full history
- **Mood Tracking** — Automatic mood extraction from conversation
- **Topic Detection** — Identifies themes (work, anxiety, relationships, etc.)
- **Privacy Controls** — `forget()` to delete specific or all memories
- **Knowledge Graph** — Visualize your memory connections over time
- **Journaling** — Free-form journal entries with mood sliders

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Frontend                  │
│  (Chat UI / Memory Graph / Journal / About tab)     │
└──────────┬──────────────────────────────────────────┘
           │  direct module calls (standalone mode)
           ▼
┌─────────────────────────────────────────────────────┐
│                 Core Business Logic                  │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ TherapyLLM │──│ EternalMemory│──│  Cognee Cloud │ │
│  │ (Groq API) │  │  (SQLite)    │  │  (Graph DB)   │ │
│  └────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Cognee Cloud APIs Used

| API | Purpose |
|-----|---------|
| `remember()` | Ingest session transcripts, journal entries, mood logs |
| `recall()` | Retrieve relevant context across sessions before responding |
| `improve()` | Enrich knowledge graph connections over time |
| `forget()` | Privacy-first deletion of specific memories |

## 🚀 Quick Start (Local)

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com) (free tier available)
- A [Cognee Cloud API key](https://cognee.ai)

### Setup

```bash
# Clone the repo
git clone https://github.com/rudrakhairnar16-bit/External-Therapist.git
cd External-Therapist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env and add your API keys:
#   GROQ_API_KEY=gsk_your_key_here
#   COGNEE_API_KEY=your_cognee_key_here
```

### Run (Full Stack — FastAPI Backend + Streamlit Frontend)

**Terminal 1 — Backend:**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser.

### Run (Standalone — Streamlit Only, No Backend Needed)

```bash
streamlit run streamlit_app.py
```

The app works without the FastAPI backend by calling core modules directly.

## ☁️ Deploy to Streamlit Cloud

The app is designed to deploy directly on [Streamlit Community Cloud](https://streamlit.io/cloud).

### One-Click Deploy

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"Deploy an app"**
4. Select your repo, branch, and set **Main file path** to `streamlit_app.py`
5. Under **Advanced settings → Secrets**, add:

```toml
GROQ_API_KEY = "gsk_your_key_here"
COGNEE_API_KEY = "your_cognee_key_here"
```

6. Click **Deploy**

### Configure Domain (Optional)

1. Go to **Settings → Custom domain**
2. Enter your preferred subdomain (e.g., `eternal-therapist`)
3. Your app will be at `https://eternal-therapist.streamlit.app`

### Streamlit Cloud Notes

- The app runs in **standalone mode** — no separate backend server needed
- Memory is stored in a local SQLite file (ephemeral on Streamlit Cloud — resets on redeploy)
- For persistent storage, connect to Cognee Cloud or use an external database

## 🗂️ Project Structure

```
External-Therapist/
├── app/
│   ├── core/
│   │   ├── config.py          # Environment configuration
│   │   ├── llm.py             # Groq LLM integration with memory
│   │   └── memory.py          # EternalMemory (Cognee Cloud / SQLite)
│   ├── api/
│   │   ├── chat.py            # Chat endpoint
│   │   ├── sessions.py        # Session history endpoint
│   │   ├── journal.py         # Journal and insights endpoints
│   │   └── privacy.py         # Forget endpoints
│   ├── models/
│   │   ├── memory.py          # Pydantic models for memory
│   │   ├── session.py         # Pydantic models for chat
│   │   └── user.py            # Pydantic models for users
│   └── main.py                # FastAPI app entry
├── tests/
│   └── test_memory.py         # Unit tests
├── demo/
│   └── demo_script.md         # 90-second hackathon demo script
├── .streamlit/
│   └── config.toml            # Streamlit Cloud configuration
├── .env.template              # Environment template
├── .gitignore
├── requirements.txt
├── streamlit_app.py           # Main Streamlit app (standalone)
└── README.md
```

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 🔧 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | — | Groq API key for Llama 3 70B |
| `COGNEE_API_KEY` | No | — | Cognee Cloud API key |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Groq model name |
| `DATABASE_URL` | No | `sqlite:///./external_therapist.db` | Database URL |

## 📹 Hackathon Demo

See `demo/demo_script.md` for the 90-second video script.

### Demo Flow

1. **Opening** — Show the app, explain the problem (AI therapists forget)
2. **Chat** — Have a conversation, show the therapist referencing past context
3. **Memory** — Open the sidebar, show stored memories and insights
4. **Graph** — Show the knowledge graph visualization
5. **Privacy** — Demonstrate the forget/delete functionality
6. **Close** — Recap: Cognee Cloud APIs used (remember / recall / improve / forget)

## 🛠️ Tech Stack

- **Memory:** Cognee Cloud (graph-vector hybrid store)
- **LLM:** Llama 3 70B via Groq
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Database:** SQLite (local) / Cognee Cloud (production)

## 📄 License

MIT
