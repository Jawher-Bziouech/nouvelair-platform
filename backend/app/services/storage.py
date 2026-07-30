import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_MB, UPLOAD_DIR


def ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def validate_upload(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    ext = _extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    return ext


async def save_upload(file: UploadFile) -> tuple[str, str]:
    """
    Save uploaded file under backend/uploads/.
    Returns (relative_path, extension_without_dot).
    """
    ensure_upload_dir()
    ext = validate_upload(file)

    unique_name = f"{uuid.uuid4().hex}{ext}"
    destination = UPLOAD_DIR / unique_name

    content = await file.read()
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size is {MAX_UPLOAD_SIZE_MB} MB",
        )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file is not allowed",
        )

    destination.write_bytes(content)
    # Store path relative to backend/ for portability
    relative_path = f"uploads/{unique_name}"
    return relative_path, ext.lstrip(".")


def resolve_stored_path(chemin_fichier: str | None) -> Path | None:
    if not chemin_fichier:
        return None

    path = Path(chemin_fichier)
    if not path.is_absolute():
        path = UPLOAD_DIR.parent / chemin_fichier
    return path if path.exists() else None


def delete_stored_file(chemin_fichier: str | None) -> None:
    path = resolve_stored_path(chemin_fichier)
    if path and path.exists() and path.is_file():
        path.unlink()
