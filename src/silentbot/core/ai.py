import os
import time
import requests
import google.generativeai as genai
from ..config import OPENAI_API_KEY, OPENAI_BASE_URL, GEMINI_API_KEY, PRO_MAX_TOKENS, NORMAL_MAX_TOKENS, DEFAULT_MODEL

def call_ai(messages, mode="normal", retries=3):
    """
    Universal AI Caller: Supports OpenAI and Gemini (Google).
    Auto-detects available keys and switches providers.
    """
    max_tokens = PRO_MAX_TOKENS if mode == "pro" else NORMAL_MAX_TOKENS
    
    last_error = None
    for attempt in range(retries):
        # PRIORITY 1: GEMINI
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                
                # Convert OpenAI-style messages to Gemini history
                system_instruction = next((m["content"] for m in messages if m["role"] == "system"), "You are a helpful AI.")
                chat_history = []
                
                for m in messages:
                    if m["role"] == "user":
                        chat_history.append({"role": "user", "parts": [m["content"]]})
                    elif m["role"] == "assistant":
                        chat_history.append({"role": "model", "parts": [m["content"]]})
                
                model_name = "gemini-1.5-flash"
                if mode == "pro":
                    model_name = "gemini-1.5-pro"

                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction
                )

                last_msg = messages[-1]["content"] if messages[-1]["role"] == "user" else "Hello"
                
                if len(chat_history) > 1:
                    chat = model.start_chat(history=chat_history[:-1])
                    response = chat.send_message(last_msg, generation_config={"max_output_tokens": max_tokens})
                else:
                    response = model.generate_content(last_msg, generation_config={"max_output_tokens": max_tokens})

                return {
                    "content": response.text,
                    "tokens_used": 0,
                    "model": model_name
                }
            except Exception as e:
                last_error = f"Gemini Error: {str(e)}"
                if attempt < retries - 1:
                    time.sleep(2 ** attempt) # Exponential backoff
                    continue

        # PRIORITY 2: OPENAI (Fallback)
        if OPENAI_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
                payload = {
                    "model": "gpt-4o" if mode == "pro" else "gpt-4o-mini",
                    "messages": messages,
                    "max_tokens": max_tokens
                }
                r = requests.post(f"{OPENAI_BASE_URL}/chat/completions", json=payload, headers=headers)
                r.raise_for_status()
                d = r.json()
                return {
                    "content": d["choices"][0]["message"]["content"],
                    "tokens_used": d["usage"]["total_tokens"],
                    "model": d["model"]
                }
            except Exception as e:
                last_error = f"OpenAI Error: {str(e)}"
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue

    return {"content": f"System Error: Failed after {retries} attempts. Last error: {last_error}", "model": "error", "tokens_used": 0}