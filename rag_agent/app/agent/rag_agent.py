from langchain_ollama import OllamaLLM
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from tools.retriever import document_search
from prompts.rag_prompt import get_prompt
from parser.output_parser import get_output_parser


def get_rag_chain():
    """LCEL-based RAG pipeline."""

    
    llm = OllamaLLM(model="llama3", format="json",temperature=0.3 )

    parser = get_output_parser()
    prompt = get_prompt(parser)

    # 🔹 Step 1: Retrieve documents
    def retrieve(query: str):
        return document_search.invoke({"query": query})

    # 🔹 Step 2: Prepare input for prompt
    def prepare(data):
        return {
            "input": data["query"],
            "context": data["context"]
        }

    # 🔹 Step 3: Full chain
    chain = (
        {
            "query": lambda x: x,
            "context": RunnableLambda(retrieve),
        }
        | RunnableLambda(prepare)
        | prompt
        | llm
        | StrOutputParser()
        | RunnableLambda(parser.parse)
    )

    return chain, parser