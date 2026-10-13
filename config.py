
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PAPERS_DIR = "papers"
VECTOR_DB_DIR = "vector_db"
METADATA_DIR = "metadata"

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300
NUM_RETRIEVED_DOCS = 8

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Updated Groq model
LLM_MODEL = "openai/gpt-oss-120b"

TEMPERATURE = 0.3
