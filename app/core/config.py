import os
from dotenv import load_dotenv

load_dotenv()

COGNEE_API_KEY = os.getenv("COGNEE_API_KEY", "")
COGNEE_BASE_URL = os.getenv("COGNEE_BASE_URL", "https://api.cognee.ai")
COGNEE_VERIFY_SSL = os.getenv("COGNEE_VERIFY_SSL", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
