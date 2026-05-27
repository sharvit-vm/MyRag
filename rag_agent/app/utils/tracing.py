import os

def enable_tracing():
    os.environ["LANGCHAIN_TRACING_V2"] = "true"