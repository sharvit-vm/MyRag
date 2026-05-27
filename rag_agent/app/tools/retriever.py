from langchain.tools import tool
from vectordb.chroma_store import get_vectorstore


@tool
def document_search(query: str) -> str:
    """Retrieve relevant document chunks with sources."""

    vectordb = get_vectorstore()
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
   

    results = []
    for doc in docs:
        results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown")
        })

    return str(results)