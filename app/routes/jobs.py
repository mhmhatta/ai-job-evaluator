from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.storage import save_uploaded_file
from app.services.jobs_manager import create_job, get_job, JOBS
import logging

router = APIRouter()

# Upload Candidate Documents
@router.post("/upload")
async def upload_files(
    cv: UploadFile = File(...),
    project: UploadFile = File(...)
):
    try:
        cv_info = await save_uploaded_file(cv)
        project_info = await save_uploaded_file(project)
        logging.info(f"[UPLOAD] Received files: {cv.filename}, {project.filename}")
        return {"cv": cv_info, "project": project_info}
    except Exception as e:
        logging.exception("[UPLOAD] Failed to process upload")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Trigger Job Evaluation
@router.post("/evaluate")
async def evaluate_job(
    title: str = Form(...),
    cv_id: str = Form(...),
    project_id: str = Form(...)
):
    """
    Create a new asynchronous job for candidate evaluation.
    Use /result/{job_id} to check progress or final output.
    """
    try:
        job_data = {"title": title, "cv_id": cv_id, "project_id": project_id}
        job = create_job(job_data)
        logging.info(f"[EVALUATE] Job created successfully | ID={job['id']}")
        return {"id": job["id"], "status": job["status"]}
    except Exception as e:
        logging.exception("[EVALUATE] Failed to create evaluation job")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

# Retrieve Evaluation Result
@router.get("/result/{job_id}")
async def get_result(job_id: str):
    """
    Retrieve current job status or final evaluation result.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    status = job["status"]
    logging.info(f"[RESULT] Checking job {job_id} — Status: {status}")

    if status in ("queued", "processing"):
        return {"id": job["id"], "status": status}

    if status == "completed":
        return {
            "id": job["id"],
            "status": status,
            "result": job.get("result"),
        }

    if status == "failed":
        return {
            "id": job["id"],
            "status": status,
            "error": job.get("error", "Unknown error occurred."),
        }


# 4️⃣ System Metrics
@router.get("/metrics")
async def get_metrics():
    """
    Return high-level system performance metrics.
    Includes average CV match rate and project score.
    """
    total_jobs = len(JOBS)
    completed = sum(1 for j in JOBS.values() if j["status"] == "completed")
    failed = sum(1 for j in JOBS.values() if j["status"] == "failed")

    avg_cv = (
        sum(j["result"].get("cv_match_rate", 0) for j in JOBS.values() if j.get("result"))
        / max(completed, 1)
    )
    avg_proj = (
        sum(j["result"].get("project_score", 0) for j in JOBS.values() if j.get("result"))
        / max(completed, 1)
    )

    logging.info(f"[METRICS] Total={total_jobs} | Completed={completed} | Failed={failed}")

    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed,
        "failed_jobs": failed,
        "avg_cv_match_rate": round(avg_cv, 2),
        "avg_project_score": round(avg_proj, 2),
    }

# Replay Existing Job
@router.post("/replay/{job_id}")
async def replay_job(job_id: str):
    """
    Re-run a previous evaluation using identical parameters.
    Useful for testing LLM consistency or updated prompt logic.
    """
    prev_job = get_job(job_id)
    if not prev_job:
        raise HTTPException(status_code=404, detail="Job not found")

    data = prev_job["data"]
    new_job = create_job(data)
    logging.info(f"[REPLAY] Replayed job {job_id} → New ID={new_job['id']}")
    return {
        "replay_of": job_id,
        "new_job_id": new_job["id"],
        "status": new_job["status"],
    }