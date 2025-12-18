import os, requests
from ..config import OPENAI_API_KEY, OPENAI_BASE_URL, PRO_MAX_TOKENS, NORMAL_MAX_TOKENS

def call_ai(messages, mode="normal"):
    max_t = PRO_MAX_TOKENS if mode == "pro" else NORMAL_MAX_TOKENS
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {"model": "gpt-4o", "messages": messages, "max_tokens": max_t}
    r = requests.post(f"{OPENAI_BASE_URL}/chat/completions", json=payload, headers=headers)
    r.raise_for_status()
    d = r.json()
    return {"content": d["choices"][0]["message"]["content"], "tokens_used": d["usage"]["total_tokens"], "model": d["model"]}
