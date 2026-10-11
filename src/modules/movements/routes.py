from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.movements import service
from src.modules.movements.schemas import (
    StockMovementCreate,
    StockMovementDetailResponse,
)

router = APIRouter(prefix="/movements", tags=["Movimentações"])


@router.post(
    "",
    response_model=StockMovementDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimentação de estoque",
    description="Cria uma movimentação de entrada ou saída de forma atômica com lock pessimista.",
)
async def create_movement(
    payload: StockMovementCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_movement(db, payload)


@router.get(
    "",
    response_model=List[StockMovementDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar histórico de movimentações",
    description="Retorna o histórico de auditoria imutável ordenado pelas mais recentes.",
)
async def list_movements(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros retornados"),
    produto_id: Optional[int] = Query(None, description="Filtrar movimentações por ID de produto"),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_movements(db, skip=skip, limit=limit, produto_id=produto_id)


@router.get(
    "/{movement_id}",
    response_model=StockMovementDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar movimentação por ID",
)
async def get_movement(
    movement_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_movement_by_id(db, movement_id)
