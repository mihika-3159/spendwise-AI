import transformers

def generate_tip(user_spending_summary: str) -> str:
    """
    Generate an AI-based daily money tip based on the user's spending summary.

    Args:
        user_spending_summary (str): A summary of the user's recent spending.

    Returns:
        str: An AI-generated money tip.
    """
    generator = transformers.pipeline("text-generation", model="gpt2")
    prompt = (
        "Based on the following spending summary, give a concise daily money-saving tip:\n"
        f"{user_spending_summary}\nTip:"
    )
    result = generator(prompt, max_length=60, num_return_sequences=1)
    tip = result[0]['generated_text'].split("Tip:")[-1].strip().split('\n')[0]
    return tip