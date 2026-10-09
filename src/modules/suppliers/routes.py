from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.suppliers import service
from src.modules.suppliers.schemas import (
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)

router = APIRouter(prefix="/suppliers", tags=["Fornecedores"])


@router.post(
    "",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo fornecedor",
)
async def create_supplier(
    payload: SupplierCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_supplier(db, payload)


@router.get(
    "",
    response_model=List[SupplierResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar fornecedores",
)
async def list_suppliers(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros retornados"),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_suppliers(db, skip=skip, limit=limit)


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar fornecedor por ID",
)
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_supplier_by_id(db, supplier_id)


@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar fornecedor",
)
async def update_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await service.update_supplier(db, supplier_id, payload)


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir fornecedor",
)
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
):
    await service.delete_supplier(db, supplier_id)
