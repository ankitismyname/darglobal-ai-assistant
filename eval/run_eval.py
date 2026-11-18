"""Run the evaluation questions against the bot and write eval/results.md.

  python eval/run_eval.py                       # in-process (needs OPENROUTER_API_KEY in the environment)
  python eval/run_eval.py --url https://...     # against a deployed instance's /api/chat

Checks per question: an answer came back, it contains at least one expected keyword, it has a Sources section
(except guardrail replies), and whether the LLM fallback path was used. Also records latency.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))


def ask_local(bot, q: str, history: list[dict]) -> str:
    ans = ""
    for ans in bot.answer(q, history):
        pass
    return ans


def ask_remote(url: str, q: str, history: list[dict]) -> str:
    import requests

    r = requests.post(url.rstrip("/") + "/api/chat", json={"message": q, "history": history}, timeout=120)
    r.raise_for_status()
    return r.json()["answer"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="deployed base URL; default runs the bot in-process")
    ap.add_argument("--only", help="comma-separated question ids")
    ap.add_argument("--pause", type=float, default=4.0, help="seconds between questions (free-model rate limits)")
    args = ap.parse_args()

    questions = json.loads((ROOT / "eval" / "questions.json").read_text())
    if args.only:
        keep = set(args.only.split(","))
        questions = [x for x in questions if x["id"] in keep]
    bot = None
    if not args.url:
        from bot import Bot

        bot = Bot()

    rows = []
    for i, item in enumerate(questions):
        history = []
        for h in item.get("history", []):
            prev = ask_local(bot, h, []) if bot else ask_remote(args.url, h, [])
            history += [{"role": "user", "content": h}, {"role": "assistant", "content": prev}]
        t0 = time.time()
        try:
            ans = ask_local(bot, item["q"], history) if bot else ask_remote(args.url, item["q"], history)
        except Exception as e:  # noqa: BLE001
            ans = f"ERROR: {e}"
        dt = time.time() - t0
        low = ans.lower()
        keyword = any(k.lower() in low for k in item["any"])
        sources = "**sources**" in low or item["kind"] == "guardrail"
        fallback = "unavailable right now" in low
        ok = keyword and sources and not ans.startswith("ERROR")
        rows.append({**item, "answer": ans, "ok": ok, "keyword": keyword, "sources": sources,
                     "fallback": fallback, "seconds": round(dt, 1)})
        print(f"{'PASS' if ok else 'FAIL'} {item['id']:16s} {dt:5.1f}s fallback={fallback} | {ans[:110]!r}", flush=True)
        if i < len(questions) - 1:
            time.sleep(args.pause)

    passed = sum(r["ok"] for r in rows)
    lat = sorted(r["seconds"] for r in rows if not r["fallback"])
    lines = [
        "# Evaluation results",
        "",
        f"Target: {args.url or 'in-process'} · run at {time.strftime('%Y-%m-%d %H:%M')} · "
        f"**{passed}/{len(rows)} passed** · median latency {lat[len(lat) // 2] if lat else 'n/a'}s · "
        f"LLM fallback used {sum(r['fallback'] for r in rows)} times",
        "",
        "| # | id | type | question | keyword | sources | latency | result |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for n, r in enumerate(rows, 1):
        lines.append(f"| {n} | {r['id']} | {r['kind']} | {r['q']} | {'✅' if r['keyword'] else '❌'} | "
                     f"{'✅' if r['sources'] else '❌'} | {r['seconds']}s | {'PASS' if r['ok'] else 'FAIL'} |")
    lines += ["", "## Answers", ""]
    for r in rows:
        lines += [f"### {r['id']}: {r['q']}", "", r["answer"], ""]
    (ROOT / "eval" / "results.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{passed}/{len(rows)} passed -> eval/results.md")


if __name__ == "__main__":
    main()
