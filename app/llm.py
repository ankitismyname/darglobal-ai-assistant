"""Minimal streaming client for OpenRouter's OpenAI-compatible chat API, with model fallback."""
from __future__ import annotations

import json
from collections.abc import Iterator

import requests

from config import LLM_MAX_TOKENS, LLM_MODELS, LLM_TIMEOUT, OPENROUTER_API_KEY, OPENROUTER_URL


class LLMError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def stream_chat(messages: list[dict], temperature: float = 0.2) -> Iterator[str]:
    """Yield answer text pieces. OpenRouter tries LLM_MODELS in order if one is down or rate limited."""
    if not OPENROUTER_API_KEY:
        raise LLMError("OPENROUTER_API_KEY is not set", status=401)
    payload = {
        "models": LLM_MODELS,  # native fallback routing
        "messages": messages,
        "temperature": temperature,
        "max_tokens": LLM_MAX_TOKENS,
        "stream": True,
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "DarGlobal & Wasalt Property Assistant (demo)",
    }
    try:
        resp = requests.post(OPENROUTER_URL, json=payload, headers=headers, stream=True, timeout=LLM_TIMEOUT)
    except requests.RequestException as e:
        raise LLMError(f"network error: {e}") from e
    if resp.status_code != 200:
        try:
            detail = resp.json().get("error", {}).get("message", resp.text[:200])
        except ValueError:
            detail = resp.text[:200]
        raise LLMError(f"OpenRouter HTTP {resp.status_code}: {detail}", status=resp.status_code)

    got_text = False
    resp.encoding = "utf-8"
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue  # OpenRouter sends ": OPENROUTER PROCESSING" keep-alive comments
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            chunk = json.loads(data)
        except json.JSONDecodeError:
            continue
        if "error" in chunk:  # errors after streaming has started arrive in-band
            raise LLMError(chunk["error"].get("message", "stream error"), status=chunk["error"].get("code"))
        for choice in chunk.get("choices") or []:
            piece = (choice.get("delta") or {}).get("content")
            if piece:
                got_text = True
                yield piece
    if not got_text:
        raise LLMError("empty response from model")
