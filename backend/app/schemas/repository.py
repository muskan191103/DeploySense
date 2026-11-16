from pydantic import BaseModel, ConfigDict, Field


class RepositoryCreate(BaseModel):
    full_name: str = Field(
        min_length=3,
        max_length=255,
        pattern=r"^[^/\s]+/[^/\s]+$",
    )


class RepositoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str

class RepositoryUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
        pattern=r"^[^/\s]+/[^/\s]+$",
    )