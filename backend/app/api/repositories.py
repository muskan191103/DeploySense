from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Repository
from app.schemas.repository import RepositoryCreate, RepositoryRead, RepositoryUpdate


router = APIRouter(
    prefix="/api/repositories",
    tags=["repositories"],
)


@router.post("", response_model=RepositoryRead, status_code=201)
def create_repository(
    payload: RepositoryCreate,
    db: Session = Depends(get_db),
):
    full_name = payload.full_name.strip()

    existing = db.scalar(
        select(Repository).where(Repository.full_name == full_name)
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Repository already exists",
        )

    repository = Repository(full_name=full_name)
    db.add(repository)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Repository already exists",
        )

    db.refresh(repository)
    return repository


@router.get("", response_model=list[RepositoryRead])
def list_repositories(db: Session = Depends(get_db)):
    return db.scalars(
        select(Repository).order_by(Repository.full_name)
    ).all()

@router.get("/{repository_id}", response_model=RepositoryRead)
def get_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):
    repository = db.get(Repository, repository_id)

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    return repository

@router.patch("/{repository_id}", response_model=RepositoryRead)
def update_repository(
    repository_id: int,
    payload: RepositoryUpdate,
    db: Session = Depends(get_db),
):
    repository = db.get(Repository, repository_id)
    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    changes = payload.model_dump(exclude_unset=True)
    if not changes or changes.get("full_name") is None:
        raise HTTPException(
            status_code=422,
            detail="Provide a repository name to update",
        )

    full_name = changes["full_name"].strip()
    duplicate = db.scalar(
        select(Repository).where(
            Repository.full_name == full_name,
            Repository.id != repository_id,
        )
    )
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Repository already exists",
        )

    repository.full_name = full_name

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Repository already exists",
        )

    db.refresh(repository)
    return repository

@router.delete("/{repository_id}", status_code=204)
def delete_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):
    repository = db.get(Repository, repository_id)

    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    db.delete(repository)
    db.commit()

    return Response(status_code=204)