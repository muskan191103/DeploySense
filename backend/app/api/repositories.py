from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Repository
from app.schemas.repository import RepositoryCreate, RepositoryRead


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