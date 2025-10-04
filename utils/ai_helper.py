# utils/ai_helper.py
import os
import time
import logging
import requests
from typing import Optional
from cachetools import TTLCache, cached

HF_API_KEY = os.getenv("HF_API_KEY", "")
HF_MODEL = os.getenv("HF_MODEL", "google/flan-t5-base")
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}
API_BASE = "https://api-inference.huggingface.co/models/"

_ai_cache = TTLCache(maxsize=256, ttl=300)

def _call_hf_inference(prompt: str, max_tokens: int = 80, temperature: float = 0.5) -> str:
    url = API_BASE + HF_MODEL
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": float(temperature),
            "return_full_text": False
        }
    }
    attempts = 0
    while attempts < 4:
        try:
            resp = requests.post(url, headers=HEADERS, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and "generated_text" in data[0]:
                    return data[0]["generated_text"].strip()
                if isinstance(data, dict) and "generated_text" in data:
                    return data["generated_text"].strip()
                if isinstance(data, str):
                    return data.strip()
            elif resp.status_code in (401, 403):
                raise RuntimeError("Hugging Face auth failed. Check HF_API_KEY.")
            elif resp.status_code in (429, 503):
                attempts += 1
                wait = 2 ** attempts
                logging.warning(f"HF rate/503 error. Retry in {wait}s")
                time.sleep(wait)
            else:
                resp.raise_for_status()
        except requests.RequestException as e:
            attempts += 1
            wait = 1.5 ** attempts
            logging.warning(f"HF request failed: {e}. Retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError("HF inference unavailable after retries")

def _local_fallback(prompt: str) -> str:
    return "Track your expenses daily to build awareness of your spending."

@cached(_ai_cache)
def get_ai_suggestion(prompt: Optional[str] = None, max_tokens: int = 80, temperature: float = 0.5, fallback: bool = True) -> str:
    if not prompt:
        prompt = "Give one short money-saving tip (single sentence)."
    if HF_API_KEY:
        try:
            return _call_hf_inference(prompt, max_tokens=max_tokens, temperature=temperature)
        except Exception as e:
            logging.warning("HF inference failed: %s", e)
            if fallback:
                return _local_fallback(prompt)
            raise
    return _local_fallback(prompt)