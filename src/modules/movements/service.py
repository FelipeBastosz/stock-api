from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import EntityNotFoundException, InsufficientStockException
from src.modules.movements.models import StockMovement
from src.modules.movements.schemas import MovementType, StockMovementCreate
from src.modules.products.models import Product


async def create_movement(db: AsyncSession, data: StockMovementCreate) -> StockMovement:
    # Lock pessimista (SELECT ... FOR UPDATE) para garantir consistência
    # do saldo e evitar race conditions em requisições concorrentes.
    stmt = (
        select(Product)
        .where(Product.id == data.produto_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise EntityNotFoundException("Produto", data.produto_id)

    if data.tipo == MovementType.SAIDA:
        if product.quantidade_em_estoque < data.quantidade:
            raise InsufficientStockException(
                product_name=product.nome,
                current_stock=product.quantidade_em_estoque,
                requested_quantity=data.quantidade,
            )
        product.quantidade_em_estoque -= data.quantidade
    elif data.tipo == MovementType.ENTRADA:
        product.quantidade_em_estoque += data.quantidade

    movement = StockMovement(
        produto_id=data.produto_id,
        tipo=data.tipo.value,
        quantidade=data.quantidade,
        observacao=data.observacao.strip() if data.observacao else None,
    )

    db.add(movement)
    await db.commit()

    return await get_movement_by_id(db, movement.id)


async def list_movements(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    produto_id: Optional[int] = None,
) -> List[StockMovement]:
    stmt = (
        select(StockMovement)
        .options(selectinload(StockMovement.product))
        .order_by(StockMovement.data.desc())
    )

    if produto_id is not None:
        stmt = stmt.where(StockMovement.produto_id == produto_id)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_movement_by_id(db: AsyncSession, movement_id: int) -> StockMovement:
    stmt = (
        select(StockMovement)
        .options(selectinload(StockMovement.product))
        .where(StockMovement.id == movement_id)
    )
    result = await db.execute(stmt)
    movement = result.scalar_one_or_none()

    if not movement:
        raise EntityNotFoundException("Movimentação de estoque", movement_id)

    return movement
