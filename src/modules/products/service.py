from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import BusinessRuleException, ConflictException, EntityNotFoundException
from src.modules.categories.models import Category
from src.modules.movements.models import StockMovement
from src.modules.products.models import Product
from src.modules.products.schemas import ProductCreate, ProductUpdate
from src.modules.suppliers.models import Supplier


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    sku_clean = data.sku.strip()
    stmt_sku = select(Product).where(func.lower(Product.sku) == sku_clean.lower())
    if (await db.execute(stmt_sku)).scalar_one_or_none():
        raise ConflictException(f"Já existe um produto cadastrado com o SKU '{sku_clean}'.")

    category = await db.get(Category, data.categoria_id)
    if not category:
        raise EntityNotFoundException("Categoria", data.categoria_id)

    supplier = await db.get(Supplier, data.fornecedor_id)
    if not supplier:
        raise EntityNotFoundException("Fornecedor", data.fornecedor_id)

    product = Product(
        nome=data.nome.strip(),
        sku=sku_clean,
        preco_custo=data.preco_custo,
        preco_venda=data.preco_venda,
        quantidade_em_estoque=data.quantidade_em_estoque,
        estoque_minimo=data.estoque_minimo,
        categoria_id=data.categoria_id,
        fornecedor_id=data.fornecedor_id,
    )
    db.add(product)
    await db.commit()

    return await get_product_by_id(db, product.id)


async def list_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    busca: Optional[str] = None,
    categoria_id: Optional[int] = None,
    fornecedor_id: Optional[int] = None,
    abaixo_minimo: Optional[bool] = None,
) -> List[Product]:
    stmt = (
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.supplier))
    )

    if busca:
        termo = f"%{busca.strip()}%"
        stmt = stmt.where(or_(Product.nome.ilike(termo), Product.sku.ilike(termo)))

    if categoria_id is not None:
        stmt = stmt.where(Product.categoria_id == categoria_id)

    if fornecedor_id is not None:
        stmt = stmt.where(Product.fornecedor_id == fornecedor_id)

    if abaixo_minimo is True:
        stmt = stmt.where(Product.quantidade_em_estoque <= Product.estoque_minimo)
    elif abaixo_minimo is False:
        stmt = stmt.where(Product.quantidade_em_estoque > Product.estoque_minimo)

    stmt = stmt.offset(skip).limit(limit).order_by(Product.id.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_low_stock_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> List[Product]:
    stmt = (
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.supplier))
        .where(Product.quantidade_em_estoque <= Product.estoque_minimo)
        .order_by((Product.quantidade_em_estoque - Product.estoque_minimo).asc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())



async def get_product_by_id(db: AsyncSession, product_id: int) -> Product:
    stmt = (
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.supplier))
        .where(Product.id == product_id)
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise EntityNotFoundException("Produto", product_id)

    return product


async def update_product(db: AsyncSession, product_id: int, data: ProductUpdate) -> Product:
    product = await get_product_by_id(db, product_id)

    if data.sku is not None:
        sku_clean = data.sku.strip()
        if sku_clean.lower() != product.sku.lower():
            conflict_stmt = select(Product).where(
                func.lower(Product.sku) == sku_clean.lower(),
                Product.id != product_id,
            )
            if (await db.execute(conflict_stmt)).scalar_one_or_none():
                raise ConflictException(f"Já existe um produto cadastrado com o SKU '{sku_clean}'.")
            product.sku = sku_clean

    if data.categoria_id is not None and data.categoria_id != product.categoria_id:
        category = await db.get(Category, data.categoria_id)
        if not category:
            raise EntityNotFoundException("Categoria", data.categoria_id)
        product.categoria_id = data.categoria_id

    if data.fornecedor_id is not None and data.fornecedor_id != product.fornecedor_id:
        supplier = await db.get(Supplier, data.fornecedor_id)
        if not supplier:
            raise EntityNotFoundException("Fornecedor", data.fornecedor_id)
        product.fornecedor_id = data.fornecedor_id

    if data.nome is not None:
        product.nome = data.nome.strip()

    if data.preco_custo is not None:
        product.preco_custo = data.preco_custo

    if data.preco_venda is not None:
        product.preco_venda = data.preco_venda

    if data.quantidade_em_estoque is not None:
        product.quantidade_em_estoque = data.quantidade_em_estoque

    if data.estoque_minimo is not None:
        product.estoque_minimo = data.estoque_minimo

    await db.commit()
    return await get_product_by_id(db, product.id)


async def delete_product(db: AsyncSession, product_id: int) -> None:
    product = await get_product_by_id(db, product_id)

    count_stmt = select(func.count(StockMovement.id)).where(StockMovement.produto_id == product_id)
    movement_count = (await db.execute(count_stmt)).scalar() or 0

    if movement_count > 0:
        raise BusinessRuleException(
            f"Não é possível excluir o produto '{product.nome}' pois possui histórico de {movement_count} movimentação(ões) de estoque."
        )

    await db.delete(product)
    await db.commit()
