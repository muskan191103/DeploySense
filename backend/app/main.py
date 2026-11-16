from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine
from app.api.repositories import router as repositories_router
from app.api.workflow_runs import router as workflow_runs_router

app = FastAPI(title="DeploySense API")
app.include_router(repositories_router)
app.include_router(workflow_runs_router)

@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from exc

    return {"status": "ok", "database": "connected"}