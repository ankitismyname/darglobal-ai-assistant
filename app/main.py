"""Web app: Gradio chat UI at /, plus a small JSON API (/health, /api/chat) on the same FastAPI server."""
from __future__ import annotations

import gradio as gr
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from bot import Bot
from config import APP_TITLE, LLM_MODELS, OPENROUTER_API_KEY, PORT

bot = Bot()
meta = bot.meta

EXAMPLES = [
    "Which DarGlobal projects are in Oman?",
    "Tell me about DG1 in Dubai",
    "Which luxury brands has DarGlobal partnered with?",
    "Is DarGlobal listed on a stock exchange?",
    "3 bedroom apartment for rent in Riyadh under 6,000 a month",
    "Villas for sale in North Jeddah under 3 million",
    "What do lands for sale in Dammam typically cost?",
    "What is Wasalt?",
]


def fmt_int(n) -> str:
    return f"{int(n):,}" if n else "0"


HEADER = f"""
# 🏙️ {APP_TITLE}
Ask about **DarGlobal** projects and the company, or search **Wasalt** property listings in Saudi Arabia.
Answers come only from public data scraped from darglobal.co.uk and wasalt.sa, with links to the source pages.
"""

ABOUT = f"""
### Data snapshot
- Scraped **{meta.get('scraped_from')}** to **{meta.get('scraped_to')}**
- DarGlobal: **{fmt_int(meta.get('n_darglobal_pages'))}** pages, incl. **{fmt_int(meta.get('n_darglobal_projects'))}** project pages
- Wasalt: **{fmt_int(meta.get('n_listings'))}** listings in 6 cities + **{fmt_int(meta.get('n_wasalt_pages'))}** area guides
- **{fmt_int(meta.get('n_chunks'))}** searchable text chunks

### How it works
1. Your question is parsed for listing filters (city, type, sale/rent, bedrooms, budget).
2. Hybrid search (embeddings + keywords) finds relevant pages; listings are filtered exactly, then ranked.
3. A free LLM on OpenRouter (`{LLM_MODELS[0]}`, with fallbacks) writes the answer from that context only.

### Notes
- English only for now.
- Listings are a **sample**, and prices change: always check the live page.
- Not financial or investment advice. Demo built for an assessment; not affiliated with DarGlobal or Wasalt.
"""


def to_history(history) -> list[dict]:
    """Gradio 6 message dicts -> plain {role, content:str} (content may be a list of parts)."""
    out = []
    for m in history or []:
        if not isinstance(m, dict):
            continue
        c = m.get("content")
        if isinstance(c, list):
            c = " ".join(p.get("text", "") for p in c if isinstance(p, dict))
        elif isinstance(c, dict):
            c = c.get("text", "")
        if isinstance(c, str) and c.strip():
            out.append({"role": m.get("role"), "content": c})
    return out


def respond(message, history):
    if isinstance(message, dict):
        message = message.get("text", "")
    yield from bot.answer(message, to_history(history))


CSS = """
.gradio-container {max-width: 1200px !important; margin: auto;}
#about {font-size: 0.92em;}
footer {visibility: hidden;}
"""

with gr.Blocks(title=APP_TITLE) as demo:
    gr.Markdown(HEADER)
    with gr.Row(equal_height=False):
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=respond,
                chatbot=gr.Chatbot(
                    height=580,
                    placeholder="Ask about DarGlobal projects or Wasalt listings. Try an example below 👇",
                    render_markdown=True,
                ),
                textbox=gr.Textbox(placeholder="e.g. 2 bedroom flat for rent in Jeddah under 4,000 a month",
                                   submit_btn=True, scale=7),
                examples=EXAMPLES,
                autofocus=True,
                concurrency_limit=8,
            )
        with gr.Column(scale=1, min_width=260, elem_id="about"):
            gr.Markdown(ABOUT)


# ---------- JSON API on the same server ----------
api = FastAPI(title=APP_TITLE, description="Chat API over scraped DarGlobal + Wasalt data")


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@api.get("/health")
def health():
    return {"status": "ok", "listings": meta.get("n_listings"), "chunks": meta.get("n_chunks"),
            "scraped_to": meta.get("scraped_to"), "llm_configured": bool(OPENROUTER_API_KEY), "models": LLM_MODELS}


@api.post("/api/chat")
def chat(req: ChatRequest):
    answer = ""
    for answer in bot.answer(req.message, to_history(req.history)):
        pass
    return {"answer": answer}


app = gr.mount_gradio_app(api, demo, path="/", theme=gr.themes.Soft(primary_hue="amber", neutral_hue="slate"), css=CSS)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
