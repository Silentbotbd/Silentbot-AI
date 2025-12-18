import os
import requests
import google.generativeai as genai
from ..config import OPENAI_API_KEY, OPENAI_BASE_URL, GEMINI_API_KEY, PRO_MAX_TOKENS, NORMAL_MAX_TOKENS, DEFAULT_MODEL

def call_ai(messages, mode="normal"):
    """
    Universal AI Caller: Supports OpenAI and Gemini (Google).
    Auto-detects available keys and switches providers.
    """
    max_tokens = PRO_MAX_TOKENS if mode == "pro" else NORMAL_MAX_TOKENS
    
    # PRIORITY 1: GEMINI (Since you provided the key)
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Convert OpenAI-style messages to Gemini history
            # System prompt is usually set via model config, but we can prepend it
            system_instruction = next((m["content"] for m in messages if m["role"] == "system"), "You are a helpful AI.")
            chat_history = []
            
            for m in messages:
                if m["role"] == "user":
                    chat_history.append({"role": "user", "parts": [m["content"]]})
                elif m["role"] == "assistant":
                    chat_history.append({"role": "model", "parts": [m["content"]]})
            
            # Determine Model
            model_name = "gemini-1.5-flash" # Default fast model
            if mode == "pro":
                model_name = "gemini-1.5-pro" # Smarter model for Pro users

            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )

            # Generate
            # We pass the last user message as the trigger
            last_msg = messages[-1]["content"] if messages[-1]["role"] == "user" else "Hello"
            
            # If history exists, use start_chat, else generate_content
            if len(chat_history) > 1:
                chat = model.start_chat(history=chat_history[:-1]) # Exclude last msg to send it now
                response = chat.send_message(last_msg, generation_config={"max_output_tokens": max_tokens})
            else:
                response = model.generate_content(last_msg, generation_config={"max_output_tokens": max_tokens})

            return {
                "content": response.text,
                "tokens_used": 0, # Gemini doesn't always return usage easily
                "model": model_name
            }
        except Exception as e:
            # Fallback or Error
            if not OPENAI_API_KEY:
                return {"content": f"Gemini Error: {str(e)}", "model": "error", "tokens_used": 0}

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
            return {"content": f"OpenAI Error: {str(e)}", "model": "error", "tokens_used": 0}

    return {"content": "System Error: No valid API Keys found (OpenAI or Gemini).", "model": "none", "tokens_used": 0}