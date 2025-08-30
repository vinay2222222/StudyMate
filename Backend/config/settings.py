import os
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_ID = os.getenv("MODEL_ID", "mistralai/Mixtral-8x7B-Instruct-v0.1")

# Retrieval settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 200
TOP_K = 10

# Data storage paths
BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
UPLOADS_DIR = os.path.join(BASE_DATA_DIR, "uploads")
CHUNKS_DIR = os.path.join(BASE_DATA_DIR, "chunks")
INDEX_DIR = os.path.join(BASE_DATA_DIR, "index")

# Ensure folders exist
for path in [UPLOADS_DIR, CHUNKS_DIR, INDEX_DIR]:
    os.makedirs(path, exist_ok=True)
