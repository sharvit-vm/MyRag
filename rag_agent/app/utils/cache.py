from functools import lru_cache
from agent.rag_agent import get_rag_chain

_chain, _ = get_rag_chain()

@lru_cache(maxsize=100)
def cached_query(query: str):
    try:
        return _chain.invoke(query)
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "sources": []
        }