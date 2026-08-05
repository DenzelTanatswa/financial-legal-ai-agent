import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "Uploads")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RAG_TOP_K = 4
CHUNK_SIZE = 1000
