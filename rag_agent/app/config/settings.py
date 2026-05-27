from dotenv import load_dotenv
load_dotenv()

class Settings:
    MODEL_NAME = "qwen2.5:latest"
    VECTOR_DB_DIR = "db"
    DATA_DIR = "data/docs"

settings = Settings()