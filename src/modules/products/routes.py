from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.dependencies import require_role
from src.modules.products import service
from src.modules.products.schemas import (
    ProductCreate,
    ProductDetailResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["Produtos"])


@router.post(
    "",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo produto",
    dependencies=[Depends(require_role("admin"))],
)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_product(db, payload)


@router.get(
    "",
    response_model=List[ProductDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar produtos",
    description="Lista produtos cadastrados com suporte a busca textual e filtros estratégicos.",
)
async def list_products(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros retornados"),
    busca: Optional[str] = Query(None, description="Busca textual por nome ou SKU"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    fornecedor_id: Optional[int] = Query(None, description="Filtrar por fornecedor"),
    abaixo_minimo: Optional[bool] = Query(None, description="Filtrar apenas produtos com estoque no mínimo ou abaixo"),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_products(
        db,
        skip=skip,
        limit=limit,
        busca=busca,
        categoria_id=categoria_id,
        fornecedor_id=fornecedor_id,
        abaixo_minimo=abaixo_minimo,
    )


@router.get(
    "/low-stock",
    response_model=List[ProductDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Relatório de estoque crítico / mínimo",
    description="Retorna produtos que atingiram ou estão abaixo do estoque mínimo, ordenados pela criticidade do déficit.",
)
async def get_low_stock_products(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros retornados"),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_low_stock_products(db, skip=skip, limit=limit)


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar produto por ID",
)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_product_by_id(db, product_id)



@router.put(
    "/{product_id}",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar produto",
    dependencies=[Depends(require_role("admin"))],
)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await service.update_product(db, product_id, payload)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir produto",
    dependencies=[Depends(require_role("admin"))],
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    await service.delete_product(db, product_id)
