from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.dependencies import require_role
from src.modules.movements import service
from src.modules.movements.schemas import (
    MovementSummaryResponse,
    MovementType,
    StockMovementCreate,
    StockMovementDetailResponse,
)

router = APIRouter(
    prefix="/movements",
    tags=["Movimentações"],
    dependencies=[Depends(require_role("admin", "operator"))],
)


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
    description="Retorna o histórico de auditoria imutável com filtros estratégicos por período, fornecedor, produto e tipo.",
)
async def list_movements(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros retornados"),
    produto_id: Optional[int] = Query(None, description="Filtrar movimentações por ID de produto"),
    fornecedor_id: Optional[int] = Query(None, description="Filtrar movimentações por fornecedor do produto"),
    tipo: Optional[MovementType] = Query(None, description="Filtrar por tipo (entrada ou saida)"),
    data_inicio: Optional[datetime] = Query(None, description="Data/hora inicial do período (ISO 8601)"),
    data_fim: Optional[datetime] = Query(None, description="Data/hora final do período (ISO 8601)"),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_movements(
        db,
        skip=skip,
        limit=limit,
        produto_id=produto_id,
        fornecedor_id=fornecedor_id,
        tipo=tipo,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get(
    "/summary",
    response_model=MovementSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Relatório consolidado de movimentações",
    description="Gera totais consolidados de movimentações, entradas, saídas e saldo líquido do período.",
)
async def get_movements_summary(
    produto_id: Optional[int] = Query(None, description="Filtrar por produto"),
    fornecedor_id: Optional[int] = Query(None, description="Filtrar por fornecedor"),
    data_inicio: Optional[datetime] = Query(None, description="Data/hora inicial do período"),
    data_fim: Optional[datetime] = Query(None, description="Data/hora final do período"),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_movements_summary(
        db,
        produto_id=produto_id,
        fornecedor_id=fornecedor_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


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

