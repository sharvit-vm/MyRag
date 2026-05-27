from dotenv import load_dotenv
load_dotenv()
 
from utils.cache import cached_query
from ingestion.pipeline import ingest
from vectordb.chroma_store import get_vectorstore
 
 
def initialize_data():
    """Check if DB is empty → run ingestion"""
 
    vectordb = get_vectorstore()
 
    try:
        count = vectordb._collection.count()
    except:
        count = 0
 
    if count == 0:
        print(" No data found. Running ingestion...")
 
        # PUT YOUR FILE PATH HERE
        ingest("data/docs/Intern_Training_Plan_Feb2026.docx")
 
    else:
        print(f" DB already has {count} documents")
 
 
def main():
    print(" Starting RAG System...")
 
    initialize_data()  
 
    print(" RAG System Ready")
 
    while True:
        query = input("\nAsk: ")
 
        if query.lower() in ["exit", "quit"]:
            break
 
        response = cached_query(query)
 
        if isinstance(response, dict):
            print("\nAnswer:\n", response.get("answer", response))
            sources = response.get("sources", [])
            if sources:
                print("\nSources:")
                for src in sources:
                    print("-", src.get("source", src))
            else:
                print("\nSources: None")
        else:
            print("\nAnswer:\n", response.answer)
 
            print("\nSources:")
            for src in response.sources:
                print("-", src.source)
 
 
if __name__ == "__main__":
    main()