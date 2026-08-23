import os
from pathlib import Path

# Load backend/.env if present (gitignored)
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

# Auth / security settings for the Nouvelair platform.
# Move SECRET_KEY to an environment variable before production.

SECRET_KEY = "nouvelair-dev-secret-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours

# Local file storage for uploaded knowledge resources
BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}
MAX_UPLOAD_SIZE_MB = 20

# RAG / assistant
VECTOR_DIR = BASE_DIR / "vector_store"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
RAG_TOP_K = 4

# Free LLM (preferred): Google Gemini — https://aistudio.google.com/apikey
GEMINI_API_KEY = (
    os.getenv("GEMINI_API_KEY", "").strip()
    or os.getenv("GOOGLE_API_KEY", "").strip()
)
# Prefer a stable free-tier model; flash-latest often returns 503 under load.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest").strip()

# Free alternative: Groq — https://console.groq.com/keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()

# Optional paid: OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# OCR for scanned PDFs (image pages with little/no text layer)
OCR_ENABLED = os.getenv("OCR_ENABLED", "true").strip().lower() in {"1", "true", "yes"}
OCR_MIN_CHARS = int(os.getenv("OCR_MIN_CHARS", "80"))  # below this → try OCR
OCR_MAX_PAGES = int(os.getenv("OCR_MAX_PAGES", "20"))
OCR_DPI = int(os.getenv("OCR_DPI", "200"))
# Optional local Tesseract binary (Windows example: C:\\Program Files\\Tesseract-OCR\\tesseract.exe)
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "").strip()
