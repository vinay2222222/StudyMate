import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

import numpy as np

# --- project modules (you already have these) ---
# pdf parsing & chunking
from core.pdf_parser import extract_text_from_pdf, chunk_by_topic
# embeddings
from core.embeddings import get_embeddings
# retrieval + persistence
from core.retrieval import (
    create_faiss_index,
    retrieve_top_k,
    save_faiss_index,
    load_faiss_index,
    save_chunks,
    load_chunks,
)
# LLM (Hugging Face Hub chat)
from core.llm_integration import generate_answer

# base config (directories + defaults)
from config.settings import (
    BASE_DATA_DIR,
    UPLOADS_DIR,
    CHUNKS_DIR,
    INDEX_DIR,
    TOP_K as DEFAULT_TOP_K,
    MODEL_ID as DEFAULT_MODEL_ID,
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -----------------------------------------------

app = Flask(__name__)

# Configure CORS to allow requests from http://localhost:5173
CORS(app, resources={
    r"/upload": {"origins": "*"},
    r"/ask": {"origins": "*"},
    r"/chunks": {"origins": "*"},
    r"/settings": {"origins": "*"},
    r"/reset": {"origins": "*"},
    r"/health": {"origins": "*"},
    r"/uploads/*": {"origins": "*"}
}, supports_credentials=True)

# Where we persist app-level settings that the user can change live
SETTINGS_PATH = os.path.join(BASE_DATA_DIR, "settings.json")
os.makedirs(BASE_DATA_DIR, exist_ok=True)

# Default runtime settings (user can override via /settings)
DEFAULT_SETTINGS = {
    "mode": "topic",                  # "topic" | "fixed"
    "similarity_threshold": 0.80,     # used only for topic mode
    "chunk_size": 500,                # used only for fixed mode
    "chunk_overlap": 100,             # used only for fixed mode
    "top_k": DEFAULT_TOP_K,           # retrieval
    "model_id": DEFAULT_MODEL_ID      # HF model id
}

def load_runtime_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
                return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_runtime_settings(settings: dict):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

RUNTIME = load_runtime_settings()

# ------------- helpers -------------

def fixed_chunk(text: str, size: int = 500, overlap: int = 100):
    """Simple fixed-size chunking with overlap (word-based)."""
    words = text.split()
    if size <= 0:
        size = 1
    if overlap < 0:
        overlap = 0

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def build_index_from_chunks(chunks):
    embeddings = get_embeddings(chunks)
    index = create_faiss_index(np.array(embeddings))
    return index

def auto_summary_from_chunks(chunks):
    """
    Build a concise summary across all chunks.
    We keep it safe by sampling a subset (avoid huge prompts).
    """
    if not chunks:
        return "No content to summarize."

    # Take up to ~12 representative chunks spread across the document(s)
    take = min(12, len(chunks))
    step = max(1, len(chunks) // take)
    sampled = [chunks[i] for i in range(0, len(chunks), step)][:take]

    prompt = (
        "Provide a concise, student-friendly summary with bullet points. "
        "Highlight key concepts, definitions, formulas, and workflows. "
        "Be faithful to the source and avoid hallucinations."
    )
    # Reuse our chat model with a 'summary' style question
    return generate_answer(sampled, prompt)

def touch_dirs():
    for d in (BASE_DATA_DIR, UPLOADS_DIR, CHUNKS_DIR, INDEX_DIR):
        os.makedirs(d, exist_ok=True)

touch_dirs()

# ------------- endpoints -------------

@app.get("/health")
def health():
    # Current date and time: 11:34 AM IST, Thursday, August 14, 2025
    current_time = datetime(2025, 8, 14, 11, 34, tzinfo=datetime.now().astimezone().tzinfo)
    return jsonify({"status": "ok", "time": current_time.isoformat()})

@app.get("/settings")
def get_settings():
    global RUNTIME
    return jsonify(RUNTIME)

@app.post("/settings")
def update_settings():
    """
    Body (any subset is fine):
    {
      "mode": "topic"|"fixed",
      "similarity_threshold": 0.75,
      "chunk_size": 500,
      "chunk_overlap": 100,
      "top_k": 3,
      "model_id": "mistralai/Mixtral-8x7B-Instruct-v0.1"
    }
    """
    global RUNTIME
    data = request.get_json(force=True, silent=True) or {}

    # Validate and merge settings
    updated_settings = {}
    for key, value in data.items():
        if key in DEFAULT_SETTINGS:
            if key in ["similarity_threshold", "chunk_size", "chunk_overlap", "top_k"]:
                try:
                    updated_settings[key] = float(value) if key == "similarity_threshold" else int(value)
                except (ValueError, TypeError):
                    return jsonify({"ok": False, "error": f"Invalid value for {key}"}), 400
            elif key == "mode" and value in ["topic", "fixed"]:
                updated_settings[key] = value
            elif key == "model_id" and isinstance(value, str):
                updated_settings[key] = value

    RUNTIME = {**RUNTIME, **updated_settings}
    save_runtime_settings(RUNTIME)
    return jsonify({"ok": True, "settings": RUNTIME})

@app.post("/upload")
def upload_pdfs():
    """
    Accepts multiple PDFs under form field name 'files'.
    Saves PDFs, extracts text, chunks (topic OR fixed), builds FAISS index,
    persists chunks/index, and returns an auto summary.
    """
    global RUNTIME
    files = request.files.getlist("files")
    if not files:
        return jsonify({"ok": False, "error": "No files uploaded (use field 'files')."}), 400

    all_chunks = []

    for f in files:
        # Save upload
        save_path = os.path.join(UPLOADS_DIR, f.filename)
        try:
            f.save(save_path)
            logger.debug(f"Saved file: {f.filename}")
        except Exception as e:
            logger.error(f"Failed to save {f.filename}: {e}")
            return jsonify({"ok": False, "error": f"Failed to save {f.filename}: {str(e)}"}), 500

        # Extract text
        try:
            text = extract_text_from_pdf(save_path)
            logger.debug(f"Extracted text from {f.filename}")
            if not text:
                raise ValueError("No text extracted")
        except Exception as e:
            logger.error(f"Failed to extract text from {f.filename}: {e}")
            return jsonify({"ok": False, "error": f"Could not extract text from {f.filename}: {str(e)}"}), 500

        # Chunk based on settings
        try:
            if RUNTIME["mode"] == "topic":
                chunks = chunk_by_topic(text, similarity_threshold=RUNTIME["similarity_threshold"])
            else:
                chunks = fixed_chunk(text, size=RUNTIME["chunk_size"], overlap=RUNTIME["chunk_overlap"])
            logger.debug(f"Chunked {f.filename} into {len(chunks)} chunks")
            all_chunks.extend(chunks)
        except Exception as e:
            logger.error(f"Failed to chunk {f.filename}: {e}")
            return jsonify({"ok": False, "error": f"Failed to chunk {f.filename}: {str(e)}"}), 500

    if not all_chunks:
        return jsonify({"ok": False, "error": "Could not extract text from the uploaded PDFs."}), 400

    # Persist chunks
    try:
        save_chunks(all_chunks, "study_chunks.json")
        logger.debug("Saved chunks")
    except Exception as e:
        logger.error(f"Failed to save chunks: {e}")
        return jsonify({"ok": False, "error": "Failed to save chunks"}), 500

    # Build & persist index
    try:
        index = build_index_from_chunks(all_chunks)
        save_faiss_index(index, "study_index.index")
        logger.debug("Built and saved index")
    except Exception as e:
        logger.error(f"Failed to build index: {e}")
        return jsonify({"ok": False, "error": "Failed to build index"}), 500

    # Auto summary
    try:
        summary = auto_summary_from_chunks(all_chunks)
        logger.debug("Generated summary")
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        return jsonify({"ok": False, "error": "Failed to generate summary"}), 500

    return jsonify({
        "ok": True,
        "files": [f.filename for f in files],
        "chunks": len(all_chunks),
        "summary": summary,
        "settings_used": RUNTIME
    })

@app.post("/ask")
def ask():
    """
    Body:
    { "question": "Your question here" }

    Uses saved chunks + saved FAISS index + current top_k to answer.
    """
    global RUNTIME
    payload = request.get_json(force=True, silent=True) or {}
    question = payload.get("question", "").strip()

    if not question:
        return jsonify({"ok": False, "error": "Missing 'question'"}), 400

    chunks = load_chunks("study_chunks.json")
    index = load_faiss_index("study_index.index")

    if not chunks or index is None:
        return jsonify({"ok": False, "error": "No knowledge base loaded. Upload PDFs first."}), 400

    top_k = int(RUNTIME.get("top_k", DEFAULT_TOP_K)) or DEFAULT_TOP_K
    top_chunks = retrieve_top_k(question, index, chunks, top_k=top_k)
    answer = generate_answer(top_chunks, question)

    return jsonify({
        "ok": True,
        "answer": answer,
        "context_count": len(top_chunks),
        "used_top_k": top_k
    })

@app.get("/chunks")
def get_chunks_info():
    """
    Inspect current chunk store.
    """
    chunks = load_chunks("study_chunks.json") or []
    sample = chunks[:3]
    return jsonify({"count": len(chunks), "sample": sample})

@app.post("/reset")
def reset_all():
    """
    Clear saved chunks, index, and (optionally) uploads.
    """
    # Remove chunks file
    chunks_file = os.path.join(CHUNKS_DIR, "study_chunks.json")
    if os.path.exists(chunks_file):
        os.remove(chunks_file)

    # Remove index file
    index_file = os.path.join(INDEX_DIR, "study_index.index")
    if os.path.exists(index_file):
        os.remove(index_file)

    # (optional) Clear uploads — comment out if you want to keep PDFs
    for name in os.listdir(UPLOADS_DIR):
        try:
            os.remove(os.path.join(UPLOADS_DIR, name))
        except Exception:
            pass

    return jsonify({"ok": True, "message": "Cleared chunks, index, and uploads."})

if __name__ == "__main__":
    # Run on 127.0.0.1:8000 for local development
    app.run(host="127.0.0.1", port=8000, debug=True)