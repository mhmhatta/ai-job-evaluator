import asyncio
import uuid
from datetime import datetime
from app.services.pipeline import evaluate_candidate

# In-memory job registry
JOBS = {}

async def simulate_evaluation(job_id, job_data):
    JOBS[job_id]["status"] = "processing"
    try:
        result = await evaluate_candidate(
            title=job_data["title"],
            cv_id=job_data["cv_id"],
            project_id=job_data["project_id"]
        )
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["result"] = result
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)

def create_job(job_data):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "id": job_id,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "data": job_data,
    }
    asyncio.create_task(simulate_evaluation(job_id, job_data))
    return JOBS[job_id]

def get_job(job_id):
    return JOBS.get(job_id)
