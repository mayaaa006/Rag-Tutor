# NotePilot 📚

An AI-powered document chat app. Upload PDFs or Word documents, ask questions, and get grounded answers pulled only from your files — with support for multiple documents, multiple chat threads, custom response styles, and Google sign-in.

Built with Streamlit, LangChain, Groq, and Hugging Face — no cloud database, no heavy backend, runs entirely from a single Python project.

---

## Features

- **Upload PDFs and Word docs** (up to 6 at a time) and chat with their contents
- **Grounded answers only** — the model is instructed to answer strictly from your documents, and says "I don't know" if the answer isn't in there
- **Multiple chat threads** — create, rename, delete, and switch between separate conversations, each sharing the same uploaded documents
- **Custom response style** — pick a preset (concise, detailed notes, simple language, expanded context) or add your own free-text instructions
- **Copy-to-clipboard** button on every AI response
- **Google Sign-In** — the app is gated behind OAuth login; no one reaches the chat without signing in
- **Persistent history per user** — your chats are saved to disk and reload automatically the next time you log in, even after closing the app
- **Custom landing page** — a styled marketing-style landing screen (`index.html`) shown before login

---

## Tech Stack

| Piece                    | Tool                                                                       |
| ------------------------ | -------------------------------------------------------------------------- |
| App framework / UI       | [Streamlit](https://streamlit.io)                                          |
| RAG orchestration        | [LangChain](https://www.langchain.com/)                                    |
| PDF parsing              | `pypdf` (via `PyPDFLoader`)                                                |
| Word doc parsing         | `docx2txt` (via `Docx2txtLoader`)                                          |
| Text chunking            | LangChain's `RecursiveCharacterTextSplitter`                               |
| Embeddings               | Hugging Face Inference API (`sentence-transformers/all-MiniLM-L6-v2`)      |
| Vector store             | [FAISS](https://github.com/facebookresearch/faiss) (local, in-memory)      |
| Chat / answer generation | [Groq](https://groq.com/) (`llama-3.3-70b-versatile`)                      |
| Auth                     | Streamlit native auth (`st.login()` / `st.user`), Google OAuth via Authlib |
| Persistence              | Local JSON files, one per user (keyed by email)                            |

---

## Project Structure

```
rag-tutor/
├── app.py                  # Main entry point — login gate, chat UI, wiring
├── ui.py                   # Sidebar rendering: uploader, chat list, settings, styling
├── document_handler.py     # PDF/DOCX loading, chunking, embedding, FAISS store
├── llm_handler.py          # Builds the prompt and calls the Groq chat model
├── storage.py              # Load/save per-user chat history as JSON
├── index.html              # Custom landing page shown before login
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed — see below)
├── .streamlit/
│   └── secrets.toml        # Google OAuth config (not committed — see below)
├── user_data/               # Per-user saved chat history (auto-created, not committed)
└── files/                   # Uploaded documents saved here at runtime
```

---

## Setup — Running This Yourself

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/mayaaa006/Rag-Tutor.git
cd rag-tutor
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# or: source venv/bin/activate  # Mac/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your API keys

You'll need three things:

**Groq API key** (for chat answers — free)

1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Sign in, create a key

**Hugging Face token** (for embeddings — free)

1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a new token, type "Read"

**Google OAuth credentials** (for sign-in)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → create/select a project
2. APIs & Services → Credentials → Create Credentials → OAuth Client ID
3. Application type: **Web application**
4. Under **Authorized redirect URIs**, add: `http://localhost:8501/oauth2callback`
5. Copy the generated **Client ID** and **Client Secret**

### 4. Create your `.env` file

In the project root, create `.env`:

```
GROQ_API_KEY=your_groq_key_here
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
```

### 5. Create your `.streamlit/secrets.toml` file

```bash
mkdir .streamlit
```

Create `.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "any-long-random-string-you-make-up"
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

> ⚠️ Both `.env` and `.streamlit/secrets.toml` contain secrets and are already excluded via `.gitignore`. Never commit them.

### 6. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser. You'll land on the custom landing page — click **Init Login** to sign in with Google, and you'll be dropped into the app.

---

## How to Use It

1. **Sign in** with your Google account on the landing page
2. **Upload documents** from the sidebar (PDF or DOCX, up to 6 at once)
3. Wait for the "document(s) processed and ready!" message
4. **Pick a response style** (concise, detailed notes, simple language, or expanded) and optionally add custom instructions
5. **Ask questions** in the chat box — answers are grounded only in your uploaded documents
6. Use **➕ New chat** to start a separate conversation thread; switch between threads anytime from the sidebar
7. Use the **⋮** menu next to a chat to rename or delete it
8. Click **📋** under any answer to copy it
9. Your chat history is saved automatically and will still be there next time you log in

---

## Known Limitations

- **Local file storage only** — uploaded documents and vector stores live only in-memory per session; chat history is saved to local JSON files, which won't survive a redeploy on most cloud hosting platforms without switching to a real database
- **No streaming responses** — answers appear all at once after the model finishes generating, not progressively
- **Documents are shared across chat threads** — all chats within one login use the same uploaded document set; there's no per-chat document isolation
- **Rebuilding on file changes re-embeds everything** — adding/removing a document re-processes all currently uploaded files, not just the changed one
- **Free-tier API limits apply** — both Groq and Hugging Face's free tiers have rate limits; heavy testing/usage may occasionally hit them

---

## Roadmap (Not Yet Built)

- Docker containerization
- Cloud deployment
- Per-chat document isolation (optional)
- Streaming responses
