import json
import logging
import asyncio
from app.services.storage import get_uploaded_file_path, extract_text_from_pdf
from app.services.llm import get_ai_response


async def evaluate_candidate(title: str, cv_id: str, project_id: str) -> dict:
    """
    Run the full asynchronous AI evaluation pipeline:
    1. Extract text from uploaded files (CV & Project)
    2. Construct structured evaluation prompt
    3. Query LLM for multi-aspect evaluation
    4. Return structured JSON result (auto-validated)
    """

    logging.info(f"[PIPELINE] Starting evaluation for job title: {title}")

    # Load & extract candidate documents
    cv_path = get_uploaded_file_path(cv_id)
    project_path = get_uploaded_file_path(project_id)

    if not cv_path or not project_path:
        raise FileNotFoundError("Missing CV or Project file path")

    cv_text = extract_text_from_pdf(cv_path)
    project_text = extract_text_from_pdf(project_path)

    # Construct LLM evaluation prompt
    prompt = f"""
    You are an AI evaluator for technical job candidates.

    Job Title: {title}

    Candidate CV Content:
    {cv_text[:2500]}

    Candidate Project Report:
    {project_text[:2500]}

    Please analyze and return a structured JSON output with these fields:
    - cv_match_rate (float 0-1)
    - cv_feedback (2-3 sentences)
    - project_score (1-5 scale)
    - project_feedback (2-3 sentences)
    - overall_summary (3-5 sentences combining strengths, gaps, and recommendations)
    """

    # Run LLM with retry + logging
    result_text = None
    for attempt in range(3):
        try:
            logging.info(f"[PIPELINE] LLM request attempt {attempt+1}")
            result_text = get_ai_response(prompt)
            break
        except Exception as e:
            logging.warning(f"[PIPELINE] Attempt {attempt+1} failed: {e}")
            await asyncio.sleep(2 * (attempt + 1))

    if not result_text:
        raise RuntimeError("All LLM attempts failed")

    # Parse JSON safely
    try:
        cleaned_text = result_text.strip().replace("```json", "").replace("```", "")
        result = json.loads(cleaned_text)
        logging.info("[PIPELINE] LLM JSON parsed successfully")
    except Exception:
        logging.warning("[PIPELINE] Fallback: Non-JSON response detected")
        result = {
            "overall_summary": result_text.strip()[:1000]
        }

    # --- Step 5: Final structured response ---
    final_result = {
        "cv_match_rate": result.get("cv_match_rate", 0.0),
        "cv_feedback": result.get("cv_feedback", "N/A"),
        "project_score": result.get("project_score", 0.0),
        "project_feedback": result.get("project_feedback", "N/A"),
        "overall_summary": result.get(
            "overall_summary",
            "No summary generated due to incomplete LLM response."
        )
    }

    logging.info(f"[PIPELINE] Evaluation completed successfully for {title}")
    return final_result