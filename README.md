# 🧠 AI Job Evaluator
Automated CV and Project Evaluation Service powered by LLMs and PDF parsing.
This backend system automatically evaluates a candidate's **CV** and **Project Report** using **Google Gemini LLM**, providing structured feedback and scoring for job matching.

---
## 🚀 Features
* Upload and store candidate CV and Project report securely.
* Automated evaluation pipeline with async job handling.
* Integration with **Gemini AI** for intelligent candidate assessment.
* PDF text extraction with `pdfplumber` and `PyPDF2`.
* Clear scoring output with CV match rate, project score, and summarized feedback.
* Monitoring endpoints for job metrics and evaluation status.
---

## 🧬 Tech Stack

| Layer                      | Technology                                |
| -------------------------- | ----------------------------------------- |
| **Backend Framework**      | FastAPI                                   |
| **LLM Provider**           | Google Gemini (via `google-generativeai`) |
| **Document Parsing**       | pdfplumber, PyPDF2                        |
| **Async Job Queue**        | Python `asyncio`                          |
| **Environment Management** | python-dotenv                             |
| **Data Handling**          | Pandas                                    |
| **Logging**                | Python logging middleware                 |

---
## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mhmhatta/ai-job-evaluator.git
cd ai-job-evaluator
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate    # (or .venv\Scripts\activate on Windows)
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment File

Make a `.env` file (or copy from `.env.example`) and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will run at:

```
http://127.0.0.1:8000
```

---

## API Endpoints

### `POST /upload`

Upload candidate CV and project report files (PDFs).

**Body (form-data):**

| Field   | Type | Description              |
| ------- | ---- | ------------------------ |
| cv      | file | Candidate CV             |
| project | file | Candidate Project Report |

**Response Example:**

```json
{
  "cv": {"file_id": "uuid", "filename": "CV.pdf"},
  "project": {"file_id": "uuid", "filename": "Project.pdf"}
}
```

---

### 📟 `POST /evaluate`

Trigger automated evaluation using uploaded file IDs.

**Body (form-data):**

| Field      | Type | Description            |
| ---------- | ---- | ---------------------- |
| title      | text | Job title to evaluate  |
| cv_id      | text | ID of uploaded CV      |
| project_id | text | ID of uploaded project |

**Response Example:**

```json
{
  "id": "a40bcefe-9bd6-48ac-8e66-2f8628569xxx",
  "status": "queued"
}
```

---

### 📊 `GET /result/{job_id}`

Retrieve the final evaluation result.

**Response Example:**

```json
{
  "id": "a40bcefe-9bd6-48ac-8e66-2f8628xxxx",
  "status": "completed",
  "result": {
    "cv_match_rate": 0.82,
    "cv_feedback": "Strong in backend and cloud, limited AI integration experience.",
    "project_score": 4.5,
    "project_feedback": "Meets chaining requirements, could improve error handling.",
    "overall_summary": "Good candidate fit with solid backend and AI knowledge."
  }
}
```

---

### 🔁 `POST /replay/{job_id}`

Replay or re-run an existing evaluation job (for comparison).

**Response Example:**

```json
{
  "replay_of": "40bcefe-9bd6-48ac-8e66-2f862856922c",
  "new_job_id": "145fdb31-81cd-4474-b1c0-33336cb7af9a",
  "status": "queued"
}
```

---

### 📈 `GET /metrics`

System-wide metrics summary.

**Response Example:**

```json
{
  "total_jobs": 3,
  "completed_jobs": 3,
  "failed_jobs": 0,
  "avg_cv_match_rate": 0.81,
  "avg_project_score": 4.6
}
```

---

## 🧦 Evaluation Logic

The system performs LLM-based evaluation using:

1. **Text extraction** from PDF CV & project files.
2. **Prompt generation** including:

   * Job title
   * Candidate background summary
   * Project details
3. **Structured LLM response** for:

   * CV match rate (0–1)
   * CV feedback
   * Project score (1–5)
   * Project feedback
   * Overall summary (3–5 sentences)

If Gemini fails or times out, a fallback mechanism ensures a default response is returned safely.

---

## 🧰 Folder Structure

```
app/
 ├── main.py                 # FastAPI entrypoint
 ├── routes/                 # API route definitions
 ├── services/               # Core logic (jobs, storage, pipeline, llm)
 ├── utils/                  # Helper scripts (prompt builder, logger)
 └── data/                   # Uploaded files & CSV samples
```

---

## 🧠 Bonus Work

* **Replay Evaluation API** → Allows re-running a previous evaluation job for benchmarking LLM consistency.
* **Metrics Endpoint** → Summarizes evaluation statistics for monitoring and QA tracking.
* **Enhanced Logging System** → Middleware and structured log timestamps for performance & debugging insight.
* **LLM Fallback Mechanism** → Prevents complete failure by returning default structured responses if AI call fails.

---

## 📊 Example Workflow

1. Upload your CV and project report → `/upload`
2. Trigger evaluation → `/evaluate`
3. Check results → `/result/{job_id}`
4. (Optional) Re-run job → `/replay/{job_id}`
5. Monitor system status → `/metrics`

---