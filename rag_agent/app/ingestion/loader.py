from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

def load_documents(file_path: str):
    """Load documents based on file type."""
    
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file format")

    return loader.load()