from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import settings

def get_llm():
    return Ollama(model=settings.MODEL_NAME, temperature=0)

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )