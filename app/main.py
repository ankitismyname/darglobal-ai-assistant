"""Web app: Gradio chat UI at /, plus a small JSON API (/health, /api/chat) on the same FastAPI server."""
from __future__ import annotations

import pathlib

import gradio as gr
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

import ui
from bot import Bot
from config import APP_TITLE, LLM_MODELS, OPENROUTER_API_KEY, PORT

bot = Bot()
meta = bot.meta

EXAMPLES = [
    "Which DarGlobal projects are in Oman?",
    "Which luxury brands has DarGlobal partnered with?",
    "Is DarGlobal listed on a stock exchange?",
    "3 bedroom apartment for rent in Riyadh under 6,000 a month",
    "Villas for sale in North Jeddah under 3 million",
    "What do lands for sale in Dammam typically cost?",
]
# number of countries with DarGlobal projects (one synthetic "DarGlobal projects in <country>" page each)
COUNTRIES = len({c["title"] for c in bot.index.chunks if c["title"].startswith("DarGlobal projects in ")}) or 6
AVATAR = str(pathlib.Path(__file__).with_name("static") / "assistant.svg")


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


with gr.Blocks(title=APP_TITLE) as demo:
    gr.HTML(ui.hero(meta, COUNTRIES), padding=False)
    with gr.Tabs(elem_classes="dg-tabs"):
        with gr.Tab("Assistant"):
            with gr.Row(equal_height=False):
                with gr.Column(scale=3, min_width=320):
                    gr.ChatInterface(
                        fn=respond,
                        chatbot=gr.Chatbot(
                            elem_id="dg-chat",
                            height=600,
                            placeholder=ui.PLACEHOLDER,
                            avatar_images=(None, AVATAR),
                            render_markdown=True,
                            show_label=False,
                        ),
                        textbox=gr.Textbox(placeholder="e.g. 2 bedroom flat for rent in Jeddah under 4,000 a month",
                                           submit_btn=True, scale=7, show_label=False),
                        examples=EXAMPLES,
                        autofocus=True,
                        concurrency_limit=8,
                    )
                with gr.Column(scale=1, min_width=270):
                    gr.HTML(ui.side_panel(meta, COUNTRIES), padding=False)
        with gr.Tab("How it works"):
            gr.HTML(ui.how_it_works(meta, LLM_MODELS), padding=False)
        with gr.Tab("Data"):
            gr.HTML(ui.data_page(meta, COUNTRIES), padding=False)
    gr.HTML(ui.FOOTER, padding=False)


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


app = gr.mount_gradio_app(api, demo, path="/", theme=ui.make_theme(), css=ui.CSS, head=ui.FONTS_HEAD,
                         favicon_path=AVATAR)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
