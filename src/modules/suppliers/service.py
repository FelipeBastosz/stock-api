from typing import List
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BusinessRuleException, ConflictException, EntityNotFoundException
from src.modules.products.models import Product
from src.modules.suppliers.models import Supplier
from src.modules.suppliers.schemas import SupplierCreate, SupplierUpdate


async def create_supplier(db: AsyncSession, data: SupplierCreate) -> Supplier:
    cnpj_clean = data.cnpj.strip()
    stmt_cnpj = select(Supplier).where(Supplier.cnpj == cnpj_clean)
    if (await db.execute(stmt_cnpj)).scalar_one_or_none():
        raise ConflictException(f"Já existe um fornecedor cadastrado com o CNPJ '{cnpj_clean}'.")

    email_clean = str(data.email).lower().strip()
    stmt_email = select(Supplier).where(func.lower(Supplier.email) == email_clean)
    if (await db.execute(stmt_email)).scalar_one_or_none():
        raise ConflictException(f"Já existe um fornecedor cadastrado com o email '{data.email}'.")

    supplier = Supplier(
        nome=data.nome.strip(),
        cnpj=cnpj_clean,
        telefone=data.telefone.strip() if data.telefone else None,
        email=email_clean,
    )
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier


async def list_suppliers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Supplier]:
    stmt = select(Supplier).offset(skip).limit(limit).order_by(Supplier.id.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_supplier_by_id(db: AsyncSession, supplier_id: int) -> Supplier:
    stmt = select(Supplier).where(Supplier.id == supplier_id)
    result = await db.execute(stmt)
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise EntityNotFoundException("Fornecedor", supplier_id)

    return supplier


async def update_supplier(db: AsyncSession, supplier_id: int, data: SupplierUpdate) -> Supplier:
    supplier = await get_supplier_by_id(db, supplier_id)

    if data.cnpj is not None:
        cnpj_clean = data.cnpj.strip()
        if cnpj_clean != supplier.cnpj:
            conflict_stmt = select(Supplier).where(
                Supplier.cnpj == cnpj_clean,
                Supplier.id != supplier_id,
            )
            if (await db.execute(conflict_stmt)).scalar_one_or_none():
                raise ConflictException(f"Já existe um fornecedor cadastrado com o CNPJ '{cnpj_clean}'.")
            supplier.cnpj = cnpj_clean

    if data.email is not None:
        email_clean = str(data.email).lower().strip()
        if email_clean != supplier.email.lower():
            conflict_stmt = select(Supplier).where(
                func.lower(Supplier.email) == email_clean,
                Supplier.id != supplier_id,
            )
            if (await db.execute(conflict_stmt)).scalar_one_or_none():
                raise ConflictException(f"Já existe um fornecedor cadastrado com o email '{data.email}'.")
            supplier.email = email_clean

    if data.nome is not None:
        supplier.nome = data.nome.strip()

    if data.telefone is not None:
        supplier.telefone = data.telefone.strip() if data.telefone else None

    await db.commit()
    await db.refresh(supplier)
    return supplier


async def delete_supplier(db: AsyncSession, supplier_id: int) -> None:
    supplier = await get_supplier_by_id(db, supplier_id)

    count_stmt = select(func.count(Product.id)).where(Product.fornecedor_id == supplier_id)
    linked_products = (await db.execute(count_stmt)).scalar() or 0

    if linked_products > 0:
        raise BusinessRuleException(
            f"Não é possível excluir o fornecedor '{supplier.nome}' pois existem {linked_products} produto(s) vinculado(s) a ele."
        )

    await db.delete(supplier)
    await db.commit()
