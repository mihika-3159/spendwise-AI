import requests
import json
import os
from datetime import datetime

DAILY_TIP_FILE = "daily_tip.json"
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
FALLBACK_MESSAGE = "Here's a simple tip: Track your expenses daily to manage your budget better!"

def get_ai_suggestion(expense_summary: dict) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    # Check if tip for today exists
    if os.path.exists(DAILY_TIP_FILE):
        try:
            with open(DAILY_TIP_FILE, "r") as f:
                data = json.load(f)
                if data.get("date") == today and "tip" in data:
                    return data["tip"]
        except Exception:
            pass  # Ignore errors and proceed to fetch new tip

    # Prepare prompt
    prompt = (
        "Given this expense summary, suggest a daily financial tip:\n"
        f"{json.dumps(expense_summary)}"
    )

    headers = {"Accept": "application/json"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 60}}

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        # HuggingFace returns a list of dicts with 'generated_text'
        tip = result[0].get("generated_text", "").strip() if isinstance(result, list) else ""
        if not tip:
            tip = FALLBACK_MESSAGE
    except Exception:
        tip = FALLBACK_MESSAGE

    # Save tip for today
    try:
        with open(DAILY_TIP_FILE, "w") as f:
            json.dump({"date": today, "tip": tip}, f)
    except Exception:
        pass  # Ignore file write errors

    return tip