from pathlib import Path

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
