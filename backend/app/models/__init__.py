from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), unique=True)

    runs: Mapped[list["WorkflowRun"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
    )


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "github_id",
            name="uq_workflow_runs_repository_github_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE")
    )
    github_id: Mapped[str] = mapped_column(String(80))
    workflow_name: Mapped[str] = mapped_column(String(255))
    branch: Mapped[str] = mapped_column(String(255))
    commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(40))
    conclusion: Mapped[str | None] = mapped_column(String(40), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    html_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    repository: Mapped["Repository"] = relationship(back_populates="runs")