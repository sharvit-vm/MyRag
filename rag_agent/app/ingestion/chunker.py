from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents):
    """Split documents into smaller chunks for embedding."""
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=400
    )

    return splitter.split_documents(documents)