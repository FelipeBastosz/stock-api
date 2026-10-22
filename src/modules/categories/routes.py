from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.dependencies import require_role
from src.modules.categories import service
from src.modules.categories.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)

router = APIRouter(prefix="/categories", tags=["Categorias"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar nova categoria",
    dependencies=[Depends(require_role("admin"))],
)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_category(db, payload)


@router.get(
    "",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar categorias",
)
async def list_categories(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros retornados"),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_categories(db, skip=skip, limit=limit)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar categoria por ID",
)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_category_by_id(db, category_id)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar categoria",
    dependencies=[Depends(require_role("admin"))],
)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await service.update_category(db, category_id, payload)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir categoria",
    dependencies=[Depends(require_role("admin"))],
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    await service.delete_category(db, category_id)
