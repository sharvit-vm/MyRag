from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

_vectorstore = None


def get_vectorstore():
    """Initialize or load Chroma vector DB (singleton)."""
    global _vectorstore
 
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        _vectorstore = Chroma(
            persist_directory="db",
            embedding_function=embeddings
        )
 
    return _vectorstore