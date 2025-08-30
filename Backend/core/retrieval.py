import faiss
import numpy as np
import os
import json
from core.embeddings import embedding_model
from config.settings import INDEX_DIR, CHUNKS_DIR

def create_faiss_index(embeddings):
    """Create and return a FAISS index from embeddings."""
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def retrieve_top_k(query, index, chunks, top_k=3):
    """Retrieve top-k most relevant chunks for a given query."""
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0]]

def save_faiss_index(index, filename="study_index.index"):
    """Save FAISS index to disk."""
    path = os.path.join(INDEX_DIR, filename)
    faiss.write_index(index, path)
    return path

def load_faiss_index(filename="study_index.index"):
    """Load FAISS index from disk."""
    path = os.path.join(INDEX_DIR, filename)
    if os.path.exists(path):
        return faiss.read_index(path)
    return None

def save_chunks(chunks, filename="chunks.json"):
    """Save chunks to JSON file."""
    path = os.path.join(CHUNKS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    return path

def load_chunks(filename="chunks.json"):
    """Load chunks from JSON file."""
    path = os.path.join(CHUNKS_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
