# utils/tips.py
from .ai_helper import get_ai_suggestion
import pandas as pd
from .data_utils import expenses_df

def get_ai_tip(username: str) -> str:
    """Generate AI-based financial tip based on user's recent expenses."""
    df = expenses_df(username)
    prompt = "You are a friendly personal finance coach. Give one short, actionable money-saving tip."

    if not df.empty:
        last_30 = df[df['date'] >= (pd.Timestamp.today().date() - pd.Timedelta(days=30))]
        if not last_30.empty:
            top = last_30.groupby('category')['amount'].sum().sort_values(ascending=False).head(3)
            context = ", ".join([f"{cat}: ${val:.0f}" for cat, val in top.items()])
        else:
            context = "No recent expenses recorded."
    else:
        context = "No expenses logged yet."

    return get_ai_suggestion(prompt, context=context)

def generate_tip() -> str:
    """Fallback tip when AI is unavailable."""
    return "Track your spending for one week and identify the top non-essential category to cut."
