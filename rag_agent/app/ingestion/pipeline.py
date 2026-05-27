from ingestion.loader import load_documents
from ingestion.chunker import split_documents
from vectordb.chroma_store import get_vectorstore


def is_already_ingested(file_path: str) -> bool:
    """Check if this file's chunks already exist in ChromaDB by inspecting metadata."""
    vectordb = get_vectorstore()

    try:
        existing = vectordb._collection.get(
            where={"source": file_path},
            limit=1
        )
        return len(existing["ids"]) > 0
    except Exception:
        return False


def ingest(file_path: str) -> dict:
    """Load → Split → Store documents. Returns status dict."""

    if is_already_ingested(file_path):
        print(f"Already ingested: {file_path} — skipping.")
        return {"status": "skipped", "reason": "already_ingested", "chunks": 0}

    docs = load_documents(file_path)
    chunks = split_documents(docs)

    vectordb = get_vectorstore()

    print("Adding documents:", len(chunks))
    vectordb.add_documents(chunks)

    print("Ingestion complete")
    return {"status": "success", "chunks": len(chunks)}