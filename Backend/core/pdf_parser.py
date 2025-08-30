import fitz
from sentence_transformers import SentenceTransformer
import numpy as np
from io import BytesIO

# Model to detect topic similarity between paragraphs
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_source):
    """Extract all text from a PDF. Supports both file paths and file-like objects."""
    if hasattr(pdf_source, "read"):  # Streamlit file uploader object
        pdf_bytes = pdf_source.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    else:  # Local file path
        doc = fitz.open(pdf_source)

    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_by_topic(text, similarity_threshold=0.75):
    """Splits PDF text into chunks based on topic similarity."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []

    if not paragraphs:
        return chunks

    current_chunk = [paragraphs[0]]
    current_embedding = semantic_model.encode([paragraphs[0]])[0]

    for para in paragraphs[1:]:
        para_embedding = semantic_model.encode([para])[0]
        similarity = cosine_similarity(current_embedding, para_embedding)

        if similarity >= similarity_threshold:
            current_chunk.append(para)
            combined_text = " ".join(current_chunk)
            current_embedding = semantic_model.encode([combined_text])[0]
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [para]
            current_embedding = para_embedding

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def cosine_similarity(vec1, vec2):
    """Computes cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
