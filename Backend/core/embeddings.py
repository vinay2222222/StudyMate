from sentence_transformers import SentenceTransformer

# Reuse the same embedding model as pdf_parser.py for consistency
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings(chunks):
    """Generate embeddings for a list of text chunks."""
    return embedding_model.encode(chunks)
