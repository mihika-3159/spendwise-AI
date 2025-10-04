# utils/tips.py
import random
from .ai_helper import get_ai_suggestion

_TIPS = [
    "Pack a lunch twice a week and track the money you saved.",
    "Set automatic transfers to savings right after payday.",
    "Cancel one subscription you don’t use regularly.",
    "Use cash for discretionary spending to feel the impact.",
    "Compare prices and wait 48 hours before large purchases."
]

def generate_tip() -> str:
    try:
        prompt = "Give one practical, single-sentence personal finance tip."
        ai_text = get_ai_suggestion(prompt, max_tokens=40, fallback=True)
        if ai_text and len(ai_text.strip()) > 10:
            return ai_text.strip()
    except Exception:
        pass
    return random.choice(_TIPS)
