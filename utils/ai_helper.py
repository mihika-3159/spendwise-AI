# utils/ai_helper.py
import logging
import cohere
import streamlit as st

COHERE_API_KEY = st.secrets["COHERE_API_KEY"]

if not COHERE_API_KEY:
    logging.warning("COHERE_API_KEY not set. AI tips will not work.")

try:
    co = cohere.Client(COHERE_API_KEY)
    COHERE_AVAILABLE = True
except Exception as e:
    COHERE_AVAILABLE = False
    logging.error(f"Cohere initialization failed: {e}")


def get_ai_suggestion(prompt: str, context: str = None, temperature: float = 0.7) -> str:
    """Return AI suggestion using Cohere Chat API."""
    if not COHERE_AVAILABLE:
        return "AI unavailable. Cohere not initialized."
    if not COHERE_API_KEY:
        return "AI unavailable. Please check your Cohere API key."

    full_prompt = prompt
    if context:
        full_prompt += f"\nUser context: {context}"

    try:
        response = co.chat(
            model="command-r-08-2024", 
            message=full_prompt,
            temperature=temperature,
        )
        return response.text.strip()
    except cohere.error.CohereError as e:
        logging.error(f"Cohere Chat API call failed: {e.status_code}, body: {e.body}")
        return f"AI tip unavailable. Error: {e.status_code}"
    except Exception as e:
        logging.error(f"Unexpected Cohere error: {e}")
        return f"AI tip unavailable. Error: {e}"
