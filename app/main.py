import os
import time
import logging
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from app.routes.jobs import router as jobs_router
load_dotenv()

# Logging Configuration
LOG_DIR = "app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "app.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Adding console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# Initialize FastAPI app
app = FastAPI(title="AI Job Assistant")

# Logging Middleware
@app.middleware("http")
async def log_req(request: Request, call_next):
    start_time = time.time()
    logging.info(f"[HTTP] {request.method} {request.url.path}")
    response = await call_next(request)
    elapsed = round(time.time() - start_time, 2)
    logging.info(f"[HTTP] Completed {request.method} {request.url.path} in {elapsed}s ({response.status_code})")
    response.headers["X-Process-Time"] = str(elapsed)
    return response

# Routers
app.include_router(jobs_router)

# Health Check
@app.get("/")
def root():
    return {
        "message": "Server is running",
        "api_key_detected": bool(os.getenv("GEMINI_API_KEY"))
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok", "llm": "Gemini connected"}
