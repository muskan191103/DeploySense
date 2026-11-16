from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Repository, WorkflowRun
from app.schemas.workflow_run import (
    WorkflowRunCreate,
    WorkflowRunPage,
    WorkflowRunRead,
)


router = APIRouter(
    prefix="/api/runs",
    tags=["workflow runs"],
)


@router.post("", response_model=WorkflowRunRead, status_code=201)
def create_workflow_run(
    payload: WorkflowRunCreate,
    db: Session = Depends(get_db),
):
    repository = db.get(Repository, payload.repository_id)
    if repository is None:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    existing = db.scalar(
        select(WorkflowRun).where(
            WorkflowRun.repository_id == payload.repository_id,
            WorkflowRun.github_id == payload.github_id,
        )
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Workflow run already exists for this repository",
        )

    workflow_run = WorkflowRun(
        **payload.model_dump(),
        repository=repository,
    )
    db.add(workflow_run)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Workflow run already exists for this repository",
        )

    db.refresh(workflow_run)
    return workflow_run


@router.get("", response_model=WorkflowRunPage)
def list_workflow_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    repository_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    filters = []
    if repository_id is not None:
        filters.append(WorkflowRun.repository_id == repository_id)

    total = db.scalar(
        select(func.count(WorkflowRun.id)).where(*filters)
    ) or 0

    runs = db.scalars(
        select(WorkflowRun)
        .options(joinedload(WorkflowRun.repository))
        .where(*filters)
        .order_by(WorkflowRun.started_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return WorkflowRunPage(
        items=runs,
        total=total,
        page=page,
        page_size=page_size,
    )

@router.get("/{run_id}", response_model=WorkflowRunRead)
def get_workflow_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    workflow_run = db.scalar(
        select(WorkflowRun)
        .options(joinedload(WorkflowRun.repository))
        .where(WorkflowRun.id == run_id)
    )

    if workflow_run is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow run not found",
        )

    return workflow_run