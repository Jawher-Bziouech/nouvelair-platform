from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.crud.categorie import get_categorie
from app.crud.ressource import (
    create_ressource,
    delete_ressource,
    get_ressource,
    get_ressources,
    update_ressource,
)
from app.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.ressource import RessourceCreate, RessourceRead, RessourceUpdate
from app.models.assistant import Citation
from app.services.indexer import delete_ressource_vectors, index_ressource
from app.services.storage import delete_stored_file, resolve_stored_path, save_upload

router = APIRouter(prefix="/ressources", tags=["ressources"])

_MIME_TYPES = {
    "pdf": "application/pdf",
    "txt": "text/plain; charset=utf-8",
    "md": "text/markdown; charset=utf-8",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc": "application/msword",
}


def _file_meta(ressource) -> tuple[Path, str, str]:
    path = resolve_stored_path(ressource.chemin_fichier)
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk",
        )
    ext = (ressource.type_fichier or path.suffix.lstrip(".")).lower()
    mime = _MIME_TYPES.get(ext, "application/octet-stream")
    filename = f"{ressource.titre}.{ext}"
    return path, mime, filename


def _safe_index(db: Session, ressource):
    """Index into the local vector store; never fail HTTP create/update if indexing fails."""
    try:
        index_ressource(db, ressource)
    except Exception:
        ressource.est_indexe = False
        db.add(ressource)
        db.commit()
        db.refresh(ressource)
    return get_ressource(db, ressource.id)


@router.get("/", response_model=list[RessourceRead])
def list_ressources(
    categorie_id: int | None = None,
    type: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_ressources(db, categorie_id=categorie_id, type=type, q=q)


@router.post("/upload", response_model=RessourceRead, status_code=status.HTTP_201_CREATED)
async def upload_ressource(
    titre: str = Form(...),
    type: str = Form(...),
    categorie_id: int = Form(...),
    contenu: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Administrateur", "Manager")),
):
    """
    Create a knowledge resource. File and text content are optional.
    After save, text is chunked and indexed for the assistant (RAG).
    """
    categorie = get_categorie(db, categorie_id)
    if not categorie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid categorie_id",
        )

    relative_path = None
    type_fichier = None
    if file is not None and file.filename:
        relative_path, type_fichier = await save_upload(file)

    texte = contenu.strip() if contenu else None

    ressource_in = RessourceCreate(
        titre=titre,
        type=type,
        contenu=texte or None,
        type_fichier=type_fichier,
        chemin_fichier=relative_path,
        categorie_id=categorie_id,
    )
    ressource = create_ressource(db, ressource_in, auteur_id=current_user.id)
    return _safe_index(db, ressource)


@router.get("/{ressource_id}", response_model=RessourceRead)
def retrieve_ressource(
    ressource_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    ressource = get_ressource(db, ressource_id)
    if not ressource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )
    return ressource


@router.get("/{ressource_id}/download")
def download_ressource(
    ressource_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    ressource = get_ressource(db, ressource_id)
    if not ressource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    path, mime, filename = _file_meta(ressource)
    return FileResponse(
        path=path,
        filename=filename,
        media_type=mime,
        content_disposition_type="attachment",
    )


@router.get("/{ressource_id}/preview")
def preview_ressource(
    ressource_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Serve the file inline for in-browser preview (PDF, text, etc.)."""
    ressource = get_ressource(db, ressource_id)
    if not ressource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    path, mime, filename = _file_meta(ressource)
    return FileResponse(
        path=path,
        filename=filename,
        media_type=mime,
        content_disposition_type="inline",
    )


@router.post("/{ressource_id}/reindex", response_model=RessourceRead)
def reindex_ressource(
    ressource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Administrateur", "Manager")),
):
    """Force re-index of a resource (useful after seed or a failed index)."""
    ressource = get_ressource(db, ressource_id)
    if not ressource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    role_name = current_user.role.nom if current_user.role else None
    if role_name != "Administrateur" and ressource.auteur_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only reindex their own resources",
        )

    try:
        index_ressource(db, ressource)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {exc}",
        ) from exc
    return get_ressource(db, ressource.id)


@router.post("/", response_model=RessourceRead, status_code=status.HTTP_201_CREATED)
def create_new_ressource(
    ressource_in: RessourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Administrateur", "Manager")),
):
    """Metadata-only create (no file). Prefer /ressources/upload when you have a document."""
    categorie = get_categorie(db, ressource_in.categorie_id)
    if not categorie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid categorie_id",
        )

    ressource = create_ressource(db, ressource_in, auteur_id=current_user.id)
    return _safe_index(db, ressource)


@router.put("/{ressource_id}", response_model=RessourceRead)
def update_existing_ressource(
    ressource_id: int,
    ressource_in: RessourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Administrateur", "Manager")),
):
    ressource = get_ressource(db, ressource_id)
    if not ressource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    role_name = current_user.role.nom if current_user.role else None
    if role_name != "Administrateur" and ressource.auteur_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only modify their own resources",
        )

    if ressource_in.categorie_id is not None:
        categorie = get_categorie(db, ressource_in.categorie_id)
        if not categorie:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid categorie_id",
            )

    ressource = update_ressource(db, ressource, ressource_in)
    return _safe_index(db, ressource)


@router.delete("/{ressource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_ressource(
    ressource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Administrateur", "Manager")),
):
    ressource = get_ressource(db, ressource_id)
    if not ressource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    role_name = current_user.role.nom if current_user.role else None
    if role_name != "Administrateur" and ressource.auteur_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only delete their own resources",
        )

    try:
        delete_ressource_vectors(ressource.id)
    except Exception:
        pass
    db.query(Citation).filter(Citation.ressource_id == ressource.id).delete()
    delete_stored_file(ressource.chemin_fichier)
    delete_ressource(db, ressource)
    return None
