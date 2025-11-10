import os
import logging
import google.generativeai as genai
import time
from dotenv import load_dotenv
from app.utils.prompt import build_prompt
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

#  Initialize model
model = genai.GenerativeModel("gemini-2.5-flash")

def get_ai_response(query: str, retries: int = 3) -> str:
    """Generate AI response using Gemini LLM with retries and logging"""
    for attempt in range(retries):
        try:
            # Build prompt (already includes context via pipeline if needed)
            prompt = build_prompt(query)
            logging.info(f"[LLM] Generating response (attempt {attempt+1})")

            # Generate response
            response = model.generate_content(prompt)

            # Log completion
            logging.info("[LLM] Success")
            return response.text.strip()

        except Exception as e:
            logging.warning(f"[LLM] Attempt {attempt+1} failed: {e}")
            time.sleep(2 * (attempt + 1))  # exponential backoff

    logging.error("[LLM] All retry attempts failed")
    return "LLM request failed after multiple retries"