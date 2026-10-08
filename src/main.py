from fastapi import FastAPI
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API robusta para controlo de inventário, produtos, fornecedores e auditoria de movimentações.",
)


@app.get("/health", tags=["Sistema"])
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}