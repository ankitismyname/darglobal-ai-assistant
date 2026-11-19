"""Look and feel of the web app: theme, CSS and the static HTML panels (hero, flow diagram, data page).

Visual language follows darglobal.co.uk: deep navy and bronze on warm white, a high-contrast serif for headings,
uppercase letter-spaced labels. No logos or copy are taken from the site, and the page says it is an independent demo.
"""
from __future__ import annotations

import html

import gradio as gr

GITHUB_URL = "https://github.com/ankitismyname/darglobal-ai-assistant"

FONTS_HEAD = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500'
    '&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">'
)

BRONZE = gr.themes.Color(c50="#f7f4ee", c100="#efe9de", c200="#e0d9cf", c300="#cdbb98", c400="#ac936d",
                         c500="#887148", c600="#6b5e43", c700="#574b35", c800="#3f3627", c900="#2a241a",
                         c950="#1a160f", name="bronze")
NAVY = gr.themes.Color(c50="#f4f6f8", c100="#e8eef2", c200="#d7e3eb", c300="#adc0ce", c400="#7d93a5",
                       c500="#536a7d", c600="#364d60", c700="#223849", c800="#142b3c", c900="#081c2a",
                       c950="#05121b", name="navy")


def make_theme() -> gr.themes.Base:
    return gr.themes.Base(
        primary_hue=BRONZE, secondary_hue=BRONZE, neutral_hue=NAVY,
        font=[gr.themes.GoogleFont("Manrope"), "ui-sans-serif", "system-ui", "sans-serif"],
        radius_size=gr.themes.sizes.radius_sm,
    ).set(
        body_background_fill="#f6f4f0", body_background_fill_dark="#06121b",
        body_text_color="#13202b", body_text_color_dark="#e8e3da",
        body_text_color_subdued="#5f6b74", body_text_color_subdued_dark="#9aa8b3",
        background_fill_primary="#ffffff", background_fill_primary_dark="#0c1d29",
        background_fill_secondary="#f8f6f2", background_fill_secondary_dark="#102434",
        block_background_fill="#ffffff", block_background_fill_dark="#0c1d29",
        block_border_color="#e4ddd1", block_border_color_dark="#1f3546",
        border_color_primary="#e4ddd1", border_color_primary_dark="#1f3546",
        color_accent="#6b5e43", color_accent_soft="#f1ece3", color_accent_soft_dark="#16303f",
        border_color_accent="#ac936d", border_color_accent_dark="#ac936d",
        border_color_accent_subdued="#e0d9cf", border_color_accent_subdued_dark="#2a4152",
        link_text_color="#6b5e43", link_text_color_dark="#d2bc94",
        link_text_color_hover="#081c2a", link_text_color_hover_dark="#efe2c8",
        link_text_color_visited="#6b5e43", link_text_color_visited_dark="#d2bc94",
        link_text_color_active="#6b5e43", link_text_color_active_dark="#d2bc94",
        button_primary_background_fill="#081c2a", button_primary_background_fill_dark="#ac936d",
        button_primary_background_fill_hover="#6b5e43", button_primary_background_fill_hover_dark="#cdbb98",
        button_primary_text_color="#ffffff", button_primary_text_color_dark="#081c2a",
        button_primary_border_color="#081c2a", button_primary_border_color_dark="#ac936d",
        button_secondary_background_fill="#ffffff", button_secondary_background_fill_dark="#0c1d29",
        button_secondary_background_fill_hover="#f1ece3", button_secondary_background_fill_hover_dark="#16303f",
        button_secondary_border_color="#e0d9cf", button_secondary_border_color_dark="#2a4152",
        button_secondary_text_color="#081c2a", button_secondary_text_color_dark="#e8e3da",
        input_background_fill="#ffffff", input_background_fill_dark="#0c1d29",
        input_border_color="#e0d9cf", input_border_color_dark="#2a4152",
        input_border_color_focus="#ac936d", input_border_color_focus_dark="#ac936d",
        shadow_drop="0 1px 2px rgba(8,28,42,.06)", shadow_drop_lg="0 6px 24px rgba(8,28,42,.08)",
        chatbot_text_size="15px",
    )


CSS = """
:root {
  --dg-navy: #081c2a; --dg-bronze: #6b5e43; --dg-gold: #ac936d; --dg-sand: #e0d9cf;
  --dg-card: #ffffff; --dg-line: #e4ddd1; --dg-ink: #13202b; --dg-muted: #5f6b74;
  --dg-accent: #6b5e43; --dg-soft: #f4f0e9; --dg-strong: #081c2a; --dg-strong-ink: #ffffff;
  --dg-serif: "Cormorant Garamond", "Playfair Display", Georgia, serif;
}
.dark {
  --dg-card: #0c1d29; --dg-line: #1f3546; --dg-ink: #e8e3da; --dg-muted: #9aa8b3;
  --dg-accent: #d2bc94; --dg-soft: #112838; --dg-strong: #ac936d; --dg-strong-ink: #081c2a;
}
.gradio-container { max-width: 1240px !important; margin: 0 auto !important; }
footer { display: none !important; }

/* ---------- hero ---------- */
.dg-hero { position: relative; overflow: hidden; border-radius: 6px; color: #f4efe6;
  background: radial-gradient(120% 160% at 90% 0%, #18405a 0%, #0a2333 45%, #061520 100%);
  padding: 38px 44px 30px; }
.dg-hero::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 2px;
  background: linear-gradient(90deg, transparent, #ac936d 30%, #ac936d 70%, transparent); opacity: .8; }
.dg-hero .dg-eyebrow { font-size: 11.5px; font-weight: 600; letter-spacing: .24em; text-transform: uppercase;
  color: #ac936d; }
.dg-hero h1.dg-title { font-family: var(--dg-serif); font-weight: 500; font-size: clamp(34px, 4.6vw, 54px);
  line-height: 1.03; margin: 14px 0 12px; color: #ffffff; letter-spacing: .005em; }
.dg-hero h1.dg-title em { font-style: italic; color: #cdbb98; font-weight: 500; }
.dg-hero p.dg-sub { max-width: 620px; margin: 0; color: #c3ced6; font-size: 15.5px; line-height: 1.6; }
.dg-stats { position: relative; z-index: 1; display: flex; flex-wrap: wrap; gap: 14px 38px; margin-top: 26px;
  padding-top: 18px; border-top: 1px solid rgba(172,147,109,.32); }
.dg-stats div { display: flex; flex-direction: column; }
.dg-stats b { font-family: var(--dg-serif); font-size: 32px; font-weight: 500; line-height: 1; color: #fff; }
.dg-stats span { margin-top: 6px; font-size: 11px; font-weight: 600; letter-spacing: .16em; text-transform: uppercase;
  color: #93a6b4; }
.dg-skyline { position: absolute; right: 28px; bottom: 2px; width: 340px; max-width: 34%; opacity: .5;
  pointer-events: none; }
@media (max-width: 1080px) { .dg-skyline { display: none; } }
@media (max-width: 760px) {
  .dg-hero { padding: 26px 20px 22px; }
  .dg-skyline { display: none; }
  .dg-stats { gap: 14px 24px; }
  .dg-stats b { font-size: 26px; }
}

/* ---------- tabs ---------- */
.dg-tabs button[role="tab"] { font-size: 12px !important; font-weight: 700 !important; letter-spacing: .16em;
  text-transform: uppercase; }

/* ---------- chat ---------- */
#dg-chat .placeholder-content, #dg-chat .placeholder { width: 100%; }
/* the "Sources" footer that the bot appends to every answer: a quieter, separated block */
#dg-chat .bot .prose > p:has(> strong:only-child):has(+ ul:last-child) { margin: 14px 0 6px; padding-top: 10px;
  border-top: 1px solid var(--dg-line); font-size: 11px; letter-spacing: .18em; text-transform: uppercase;
  color: var(--dg-accent); }
#dg-chat .bot .prose > ul:last-child { font-size: 13px; }
#dg-chat .bot .prose > ul:last-child li { margin: 2px 0; }
.dg-ph { text-align: center; padding: 10px 12px 4px; }
.dg-ph .dg-ph-k { font-size: 11px; font-weight: 700; letter-spacing: .22em; text-transform: uppercase;
  color: var(--dg-accent); }
.dg-ph h2 { font-family: var(--dg-serif); font-weight: 500; font-size: 34px; margin: 8px 0 6px; color: var(--dg-ink); }
.dg-ph p { margin: 0; color: var(--dg-muted); font-size: 14.5px; }

/* ---------- side cards ---------- */
.dg-side { display: flex; flex-direction: column; gap: 14px; }
.dg-card { background: var(--dg-card); border: 1px solid var(--dg-line); border-radius: 6px; padding: 18px 18px 16px;
  color: var(--dg-ink); }
.dg-k { font-size: 11px; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; color: var(--dg-accent);
  margin-bottom: 12px; }
.dg-src + .dg-src { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--dg-line); }
.dg-src h4 { font-family: var(--dg-serif); font-size: 22px; font-weight: 600; margin: 0 0 4px; color: var(--dg-ink); }
.dg-src p, .dg-card li { font-size: 13.5px; line-height: 1.55; color: var(--dg-muted); margin: 0; }
.dg-card ul { margin: 0; padding-left: 18px; }
.dg-card li + li { margin-top: 6px; }
.dg-card i { color: var(--dg-ink); }
.dg-note { background: var(--dg-soft); font-size: 12.5px; line-height: 1.55; color: var(--dg-muted); }

/* ---------- how it works ---------- */
.dg-page { color: var(--dg-ink); padding: 8px 4px 4px; }
.dg-page h2 { font-family: var(--dg-serif); font-weight: 500; font-size: 32px; margin: 4px 0 4px; color: var(--dg-ink); }
.dg-page h3 { font-family: var(--dg-serif); font-weight: 600; font-size: 22px; margin: 0 0 6px; color: var(--dg-ink); }
.dg-lead { color: var(--dg-muted); font-size: 15px; margin: 0 0 22px; max-width: 760px; line-height: 1.6; }
.dg-section + .dg-section { margin-top: 44px; }

.dg-flow { max-width: 900px; margin: 0 auto; }
.dg-row { display: grid; grid-template-columns: minmax(0, 1fr) 250px; gap: 0 18px; align-items: center; }
.dg-row.solo { grid-template-columns: minmax(0, 1fr) 250px; }
.dg-node { position: relative; display: flex; gap: 14px; align-items: flex-start; background: var(--dg-card);
  border: 1px solid var(--dg-line); border-radius: 6px; padding: 14px 16px; box-shadow: 0 1px 2px rgba(8,28,42,.05); }
.dg-node b { display: block; font-size: 15px; color: var(--dg-ink); }
.dg-node small { display: block; margin-top: 3px; font-size: 13px; line-height: 1.5; color: var(--dg-muted); }
.dg-node code, .dg-pipe code { font-size: 12px; background: var(--dg-soft); padding: 1px 5px; border-radius: 3px;
  color: var(--dg-ink); }
.dg-num { flex: none; width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center;
  font-size: 12.5px; font-weight: 700; color: var(--dg-accent); border: 1.5px solid var(--dg-gold); }
.dg-node.io { background: var(--dg-soft); border-style: dashed; border-color: var(--dg-gold); }
.dg-node.io .dg-num { border: none; font-size: 17px; }
.dg-node.llm { background: var(--dg-strong); border-color: var(--dg-strong); }
.dg-node.llm b, .dg-node.llm small { color: var(--dg-strong-ink); }
.dg-node.llm small { opacity: .82; }
.dg-node.llm .dg-num { color: var(--dg-strong-ink); border-color: var(--dg-strong-ink); }
.dg-node.llm code { background: rgba(255,255,255,.14); color: var(--dg-strong-ink); }
.dark .dg-node.llm code { background: rgba(8,28,42,.15); }
.dg-tagout { display: inline-block; margin-top: 8px; font-size: 12px; font-weight: 600; color: var(--dg-accent); }

.dg-aside { position: relative; font-size: 12.5px; line-height: 1.5; color: var(--dg-muted); padding: 10px 12px;
  border-left: 2px solid var(--dg-gold); background: var(--dg-soft); border-radius: 0 4px 4px 0; }
.dg-aside b { color: var(--dg-ink); display: block; font-size: 12.5px; }
.dg-aside::before { content: ""; position: absolute; left: -20px; top: 50%; width: 18px; border-top: 1.5px dashed var(--dg-gold); }

.dg-arrow { position: relative; height: 26px; width: calc(100% - 268px); }
.dg-arrow::before { content: ""; position: absolute; left: 50%; top: 2px; bottom: 7px; border-left: 1.5px solid var(--dg-gold); }
.dg-arrow::after { content: ""; position: absolute; left: calc(50% - 4.5px); bottom: 1px; border: 5px solid transparent;
  border-top: 6px solid var(--dg-gold); border-bottom: 0; }
.dg-fork { width: calc(100% - 268px); }
.dg-fork svg { display: block; width: 100%; height: 26px; overflow: visible; }
.dg-fork svg path { fill: none; stroke: var(--dg-gold); stroke-width: 1.5; vector-effect: non-scaling-stroke; }
.dg-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; width: calc(100% - 268px); }
.dg-pair .dg-node { flex-direction: column; gap: 8px; }
.dg-pair .dg-head { display: flex; gap: 12px; align-items: center; }

.dg-pipe { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; counter-reset: s; }
.dg-pipe > div { position: relative; background: var(--dg-card); border: 1px solid var(--dg-line); border-radius: 6px;
  padding: 14px 14px 12px; }
.dg-pipe > div:not(:last-child)::after { content: "›"; position: absolute; right: -11px; top: 50%; transform: translateY(-55%);
  font-size: 22px; color: var(--dg-gold); }
.dg-pipe .dg-k { margin-bottom: 6px; }
.dg-pipe b { display: block; font-size: 14.5px; margin-bottom: 4px; color: var(--dg-ink); }
.dg-pipe small { display: block; font-size: 12.5px; line-height: 1.5; color: var(--dg-muted); }

.dg-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.dg-grid .dg-card b { display: block; font-size: 14.5px; margin-bottom: 4px; }
.dg-grid .dg-card p { margin: 0; font-size: 13px; line-height: 1.55; color: var(--dg-muted); }

table.dg-table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
table.dg-table th { text-align: left; font-size: 11px; letter-spacing: .16em; text-transform: uppercase;
  color: var(--dg-accent); font-weight: 700; padding: 8px 10px; border-bottom: 1px solid var(--dg-gold); }
table.dg-table td { padding: 9px 10px; border-bottom: 1px solid var(--dg-line); color: var(--dg-ink); vertical-align: top; }
table.dg-table td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; font-weight: 600; }

.dg-foot { text-align: center; font-size: 12px; color: var(--dg-muted); padding: 14px 8px 4px; line-height: 1.7; }
.dg-foot a { color: var(--dg-accent); }

@media (max-width: 760px) {
  .dg-row, .dg-row.solo { grid-template-columns: 1fr; gap: 8px; }
  .dg-aside::before { display: none; }
  .dg-arrow, .dg-fork, .dg-pair { width: 100%; }
  .dg-fork svg { display: none; }
  .dg-fork { height: 16px; }
  .dg-pair, .dg-pipe, .dg-grid { grid-template-columns: 1fr; }
  .dg-pipe > div:not(:last-child)::after { content: none; }
}
"""

SKYLINE = """
<svg class="dg-skyline" viewBox="0 0 380 150" aria-hidden="true" fill="none" stroke="#ac936d" stroke-width="1.2">
  <path d="M0 149h380"/>
  <path d="M20 149V96h26v53M28 104h10M28 114h10M28 124h10"/>
  <path d="M58 149V60l18-12 18 12v89M70 70h12M70 82h12M70 94h12M70 106h12"/>
  <path d="M106 149V30h8V14h4v16h8v119M112 46h8M112 60h8M112 74h8M112 88h8"/>
  <path d="M140 149V78c18-4 30-20 34-48 4 28 16 44 34 48v71"/>
  <path d="M222 149V52h34v97M230 62h18M230 74h18M230 86h18M230 98h18M230 110h18"/>
  <path d="M268 149V88l22-14 22 14v61"/>
  <path d="M322 149V66h10V50h10v16h10v83M330 80h14M330 94h14M330 108h14"/>
  <path d="M362 149v-38h14v38"/>
</svg>
"""


def esc(x) -> str:
    return html.escape(str(x))


def n(x) -> str:
    return f"{int(x):,}" if x else "0"


def hero(meta: dict, countries: int) -> str:
    cities = len(meta.get("listings_by_city", {})) or 6
    return f"""
<div class="dg-hero">
  {SKYLINE}
  <div class="dg-eyebrow">AI property assistant &nbsp;·&nbsp; independent demo</div>
  <h1 class="dg-title">DarGlobal <em>&amp;</em> Wasalt<br>Property Assistant</h1>
  <p class="dg-sub">Ask about DarGlobal's projects and the company, or search Wasalt property listings across
  Saudi Arabia. Answers come only from the two public websites, and each one links to its source pages.</p>
  <div class="dg-stats">
    <div><b>{n(meta.get('n_darglobal_projects'))}</b><span>DarGlobal projects</span></div>
    <div><b>{countries}</b><span>Countries</span></div>
    <div><b>{n(meta.get('n_listings'))}</b><span>Wasalt listings</span></div>
    <div><b>{cities}</b><span>Saudi cities</span></div>
  </div>
</div>
"""


PLACEHOLDER = """
<div class="dg-ph">
  <div class="dg-ph-k">Ask anything</div>
  <h2>How can I help?</h2>
  <p>Pick an example below, or type your own question about DarGlobal or Wasalt.</p>
</div>
"""


def side_panel(meta: dict, countries: int) -> str:
    cities = ", ".join(meta.get("listings_by_city", {})) or "Riyadh, Jeddah, Dammam, Al Khobar, Makkah, Madinah"
    articles =meta.get("n_darglobal_pages", 0) - meta.get("n_darglobal_projects", 0)
    purpose = meta.get("listings_by_purpose", {})
    return f"""
<div class="dg-side">
  <div class="dg-card">
    <div class="dg-k">What I know</div>
    <div class="dg-src">
      <h4>DarGlobal</h4>
      <p>{n(meta.get('n_darglobal_projects'))} projects in {countries} countries, plus {n(articles)} company pages,
      FAQs, press releases and articles.</p>
    </div>
    <div class="dg-src">
      <h4>Wasalt</h4>
      <p>{n(meta.get('n_listings'))} listings ({n(purpose.get('rent'))} for rent, {n(purpose.get('sale'))} for sale)
      in {esc(cities)}, plus Wasalt's area guides.</p>
    </div>
  </div>
  <div class="dg-card">
    <div class="dg-k">Tips</div>
    <ul>
      <li>Describe what you want in plain words: <i>"2 bed furnished flat in Jeddah under 5,000 a month"</i>.</li>
      <li>Ask a follow-up: <i>"what about Dammam?"</i> or <i>"cheapest first"</i>.</li>
      <li>Numbers like [1] or [L2] point to the sources listed under each answer.</li>
    </ul>
  </div>
  <div class="dg-card dg-note">
    Data snapshot from {esc(meta.get('scraped_to'))}. Wasalt listings are a sample and prices change, so check the
    live page. English only for now. Not financial advice.
  </div>
</div>
"""


def how_it_works(meta: dict, models: list[str]) -> str:
    main_model = esc(models[0]) if models else "a free model"
    fallbacks = " → ".join(f"<code>{esc(m)}</code>" for m in models[1:]) or "none"
    fork = ('<div class="dg-fork"><svg viewBox="0 0 100 26" preserveAspectRatio="none">'
            '<path d="M50 0V12M25 12H75M25 12V26M75 12V26"/></svg></div>')
    merge = ('<div class="dg-fork"><svg viewBox="0 0 100 26" preserveAspectRatio="none">'
             '<path d="M25 0V12M75 0V12M25 12H75M50 12V26"/></svg></div>')
    arrow = '<div class="dg-arrow"></div>'
    return f"""
<div class="dg-page">
 <div class="dg-section">
  <h2>How a question becomes an answer</h2>
  <p class="dg-lead">Every message goes through the same five steps. Only step 4 uses the AI model, once per
  message. Everything else is ordinary code, so it is fast and gives the same result every time.</p>
  <div class="dg-flow">
    <div class="dg-row">
      <div class="dg-node io"><div class="dg-num">💬</div><div><b>Your question</b>
        <small>e.g. "3 bedroom apartment for rent in Riyadh under 6,000 a month"</small></div></div>
      <div></div>
    </div>
    {arrow}
    <div class="dg-row">
      <div class="dg-node"><div class="dg-num">1</div><div><b>Understand the question</b>
        <small>Rules, not AI. Reads city, district, property type, sale or rent, bedrooms, budget and size.
        Decides whether it is a listing search or a question about the companies, and carries filters into
        follow-ups like "what about Jeddah?".</small></div></div>
      <div class="dg-aside"><b>Shortcut</b>Greetings and non-English messages get an instant reply with no AI call.</div>
    </div>
    {fork}
    <div class="dg-pair">
      <div class="dg-node"><div class="dg-head"><div class="dg-num">2a</div><b>Search the pages</b></div>
        <small>{n(meta.get('n_chunks'))} passages from DarGlobal and Wasalt pages. Two searches run together:
        by meaning (<code>bge-small</code> embeddings) and by exact words (BM25). Their rankings are merged,
        and curated pages such as projects and the FAQ count more than blog posts.</small>
        <span class="dg-tagout">→ passages tagged [1] [2] …</span></div>
      <div class="dg-node"><div class="dg-head"><div class="dg-num">2b</div><b>Search the listings</b></div>
        <small>{n(meta.get('n_listings'))} Wasalt listings. Exact filters first; if nothing matches, one filter is
        relaxed at a time and the answer says which. Matches are ranked by meaning, spread across districts,
        and summarised as price statistics (median and typical range).</small>
        <span class="dg-tagout">→ listings tagged [L1] [L2] …</span></div>
    </div>
    {merge}
    <div class="dg-row">
      <div class="dg-node"><div class="dg-num">3</div><div><b>Build the prompt</b>
        <small>Strict rules (answer only from the context, cite the tags, no investment advice, no contact
        details), the tagged passages and listings, and the last two exchanges of the chat.</small></div></div>
      <div></div>
    </div>
    {arrow}
    <div class="dg-row">
      <div class="dg-node llm"><div class="dg-num">4</div><div><b>Write the answer: free AI model on OpenRouter</b>
        <small><code>{main_model}</code>, falling back to {fallbacks} if it is busy. The answer streams in
        as it is written.</small></div></div>
      <div class="dg-aside"><b>Safety net</b>If the free model is rate-limited or down, the bot still answers
        with the listings and passages it found, with links.</div>
    </div>
    {arrow}
    <div class="dg-row">
      <div class="dg-node"><div class="dg-num">5</div><div><b>Add the sources</b>
        <small>The code turns each tag the model cited into the real page link. The model never writes URLs, so
        it cannot invent one.</small></div></div>
      <div></div>
    </div>
    {arrow}
    <div class="dg-row">
      <div class="dg-node io"><div class="dg-num">✓</div><div><b>Answer with sources</b>
        <small>In the chat, or as JSON from <code>POST /api/chat</code>.</small></div></div>
      <div></div>
    </div>
  </div>
 </div>

 <div class="dg-section">
  <h2>Before any question: building the knowledge base</h2>
  <p class="dg-lead">Done once, before deployment. The search index is built inside the Docker image, so the app
  starts in seconds and never scrapes while you chat.</p>
  <div class="dg-pipe">
    <div><div class="dg-k">Step 1</div><b>Scrape</b><small>Public pages only. robots.txt and Wasalt's llms.txt
      rules followed, about 1 request per second, no phone numbers or owner details stored.</small></div>
    <div><div class="dg-k">Step 2</div><b>Clean and structure</b><small>Text read from the sites' page data, not
      the layout. Projects get fields like location and unit types; listings get price, size, beds and district.</small></div>
    <div><div class="dg-k">Step 3</div><b>Index</b><small>Pages split into passages, duplicates removed, and
      everything embedded with <code>bge-small</code> (runs on CPU, no GPU needed).</small></div>
    <div><div class="dg-k">Step 4</div><b>Package</b><small>App, data and index go into one Docker image that
      runs anywhere: <code>docker run -p 7860:7860</code>.</small></div>
  </div>
 </div>

 <div class="dg-section">
  <h2>The two sources</h2>
  <p class="dg-lead">In their own words, from the scraped pages.</p>
  <div class="dg-grid">
    <div class="dg-card"><div class="dg-k">darglobal.co.uk</div><h3>DarGlobal</h3>
      <p>A London-listed luxury real estate developer, investor and asset manager. Its projects span the UAE,
      Oman, Saudi Arabia, Qatar, Spain and the UK, many with brand partners such as Aston Martin and
      Lamborghini.</p></div>
    <div class="dg-card"><div class="dg-k">wasalt.sa</div><h3>Wasalt</h3>
      <p>A real estate platform in Saudi Arabia offering residential and commercial properties for sale and rent,
      in Arabic and English. The bot covers listings in six major cities.</p></div>
  </div>
 </div>
</div>
"""


def data_page(meta: dict, countries: int) -> str:
    sec = meta.get("chunks_by_section", {})
    by_city = meta.get("listings_by_city", {})
    by_type = meta.get("listings_by_type", {})
    purpose = meta.get("listings_by_purpose", {})
    city_rows = "".join(f"<tr><td>{esc(c)}</td><td class='n'>{n(v)}</td></tr>" for c, v in by_city.items())
    type_rows = "".join(f"<tr><td>{esc(t)}</td><td class='n'>{n(v)}</td></tr>"
                        for t, v in list(by_type.items())[:7])
    return f"""
<div class="dg-page">
 <div class="dg-section">
  <h2>What the bot knows</h2>
  <p class="dg-lead">A snapshot of public pages scraped on {esc(meta.get('scraped_to'))}. Nothing else is used: if
  the answer is not in these pages, the bot says so.</p>
  <div class="dg-grid">
    <div class="dg-card"><div class="dg-k">DarGlobal · darglobal.co.uk</div>
      <table class="dg-table">
        <tr><th>Content</th><th style="text-align:right">Count</th></tr>
        <tr><td>Project pages ({countries} countries)</td><td class="n">{n(meta.get('n_darglobal_projects'))}</td></tr>
        <tr><td>All pages scraped</td><td class="n">{n(meta.get('n_darglobal_pages'))}</td></tr>
        <tr><td>Passages from blog articles</td><td class="n">{n(sec.get('DarGlobal/blog'))}</td></tr>
        <tr><td>Passages from press releases</td><td class="n">{n(sec.get('DarGlobal/press'))}</td></tr>
        <tr><td>Passages from company pages and FAQs</td><td class="n">{n(sec.get('DarGlobal/page'))}</td></tr>
      </table></div>
    <div class="dg-card"><div class="dg-k">Wasalt · wasalt.sa</div>
      <table class="dg-table">
        <tr><th>Listings by city</th><th style="text-align:right">Count</th></tr>
        {city_rows}
        <tr><td><b>Total</b> ({n(purpose.get('rent'))} rent · {n(purpose.get('sale'))} sale)</td>
            <td class="n">{n(meta.get('n_listings'))}</td></tr>
      </table></div>
    <div class="dg-card"><div class="dg-k">Wasalt listings by type</div>
      <table class="dg-table">
        <tr><th>Type</th><th style="text-align:right">Count</th></tr>
        {type_rows}
      </table></div>
    <div class="dg-card"><div class="dg-k">How it was collected</div>
      <p>DarGlobal: every page in the site's sitemap except forms, legal pages, careers and campaign pages.</p>
      <p style="margin-top:8px">Wasalt: public category pages for 6 cities (city, region and a sample of district
      pages, for sale and rent). Wasalt's /search pages are never requested, and no phone numbers, WhatsApp links,
      owner or agent details are stored.</p>
      <p style="margin-top:8px">Listings are a sample, so price statistics describe the sample, not the whole market.</p>
    </div>
  </div>
 </div>
</div>
"""


FOOTER = f"""
<div class="dg-foot">
  Independent demo built for a technical assessment. Not affiliated with or endorsed by DarGlobal or Wasalt.
  Not financial advice.<br>
  <a href="{GITHUB_URL}" target="_blank" rel="noopener">Source code on GitHub</a> ·
  <a href="/health" target="_blank" rel="noopener">API health</a>
</div>
"""
