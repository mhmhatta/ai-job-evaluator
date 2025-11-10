import os
import uuid
import logging
from typing import Optional, List
from fastapi import UploadFile
import pdfplumber
from PyPDF2 import PdfReader

# --- PATH SETUP ---
UPLOAD_DIR = "app/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- FILENAME SANITIZER ---
def _sanitize_filename(name: str) -> str:
    """Remove invalid characters to prevent path traversal"""
    return "".join(c for c in name if c.isalnum() or c in (" ", ".", "_", "-")).strip()

# --- FILE VALIDATION ---
ALLOWED_EXT = {".pdf", ".txt"}

def _is_allowed(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXT

# --- SAVE FILE ---
async def save_uploaded_file(file: UploadFile):
    """Save uploaded file asynchronously and return metadata"""
    ext = os.path.splitext(file.filename)[1].lower()
    if not _is_allowed(file.filename):
        raise ValueError(f"File type {ext} not allowed.")

    file_id = str(uuid.uuid4())
    safe_name = _sanitize_filename(file.filename)
    filename = f"{file_id}_{safe_name}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    file_bytes = await file.read()
    with open(filepath, "wb") as f:
        f.write(file_bytes)

    return {"file_id": file_id, "filename": safe_name, "path": filepath}

# --- RETRIEVE FILE BY ID ---
def get_uploaded_file_path(file_id: str) -> Optional[str]:
    """Find stored file by file_id. Returns full path or None."""
    prefix = f"{file_id}_"
    for name in os.listdir(UPLOAD_DIR):
        if name.startswith(prefix):
            return os.path.join(UPLOAD_DIR, name)
    return None

# --- LIST ALL UPLOADED FILES ---
def list_uploaded_files() -> List[dict]:
    """Return list of all stored file metadata."""
    files = []
    for name in os.listdir(UPLOAD_DIR):
        try:
            fid, orig = name.split("_", 1)
        except ValueError:
            continue
        files.append({
            "file_id": fid,
            "filename": orig,
            "path": os.path.join(UPLOAD_DIR, name)
        })
    return files

# --- DELETE FILE BY ID ---
def delete_uploaded_file(file_id: str) -> bool:
    """Delete file by id. Returns True if deleted."""
    path = get_uploaded_file_path(file_id)
    if path and os.path.exists(path):
        os.remove(path)
        return True
    return False

# --- PDF TEXT EXTRACTION ---
def extract_text_from_pdf(path: str) -> str:
    """Extract text from PDF using pdfplumber (preferred) or PyPDF2 fallback."""
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    text_parts = []

    # try pdfplumber first
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    text_parts.append(txt)
        full = "\n\n".join(text_parts).strip()
        if full:
            return full
    except Exception as e:
        logging.debug(f"pdfplumber failed: {e}")

    # fallback to PyPDF2
    try:
        reader = PdfReader(path)
        for page in reader.pages:
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            if txt:
                text_parts.append(txt)
        return "\n\n".join(text_parts).strip()
    except Exception as e:
        logging.exception(f"Failed to extract PDF text: {e}")
        return ""
