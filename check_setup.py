
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from config import (
    GROQ_API_KEY,
    EMBEDDING_MODEL,
    LLM_MODEL,
    TEMPERATURE,
)

load_dotenv()

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Check your .env file."
    )

print("Testing embedding model locally...")

emb = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

vec = emb.embed_query("deep learning for medical imaging")

print("Embedding length:", len(vec))
print("Embedding test successful!")

print("\nTesting Groq API connection...")
print("Model configured:", LLM_MODEL)

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model=LLM_MODEL,
    temperature=TEMPERATURE,
)

try:
    response = llm.invoke(
        "Say hello in one short sentence."
    )
    print("LLM says:", response.content)
    print("Groq API test successful!")

except Exception as e:
    print("Groq API test failed:")
    print(type(e).__name__, ":", e)
