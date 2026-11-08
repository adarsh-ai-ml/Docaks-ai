from pathlib import Path


# PROJECT CONFIGURATION

STORAGE_DIR = Path("D:/DOCAKS_STORAGE")

PDF_DIR = STORAGE_DIR / "data"

DB_PATH = str(STORAGE_DIR / "chroma_db")

COLLECTION_NAME = "rag_project_cosine_v1"


# RETRIEVAL CONFIGURATION

TOP_K = 3

RELEVANCE_THRESHOLD = 0.70


# AI MODEL CONFIGURATION

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

LLM_MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"