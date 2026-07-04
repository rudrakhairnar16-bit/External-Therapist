import os
from dotenv import load_dotenv

load_dotenv()

COGNEE_API_KEY = os.getenv("COGNEE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./external_therapist.db")
