from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


def _normalize_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

from src.core.exceptions import (
    BusinessRuleException,
    EntityNotFoundException,
    InsufficientStockException,
)
from src.modules.movements.models import StockMovement
from src.modules.movements.schemas import (
    MovementSummaryResponse,
    MovementType,
    StockMovementCreate,
)
from src.modules.products.models import Product


async def create_movement(db: AsyncSession, data: StockMovementCreate) -> StockMovement:
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
    fornecedor_id: Optional[int] = None,
    tipo: Optional[MovementType] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
) -> List[StockMovement]:
    if data_inicio and data_fim and _normalize_datetime(data_inicio) > _normalize_datetime(data_fim):
        raise BusinessRuleException("A data de início não pode ser posterior à data de término.")

    stmt = (
        select(StockMovement)
        .options(selectinload(StockMovement.product))
        .order_by(StockMovement.data.desc())
    )

    if produto_id is not None:
        stmt = stmt.where(StockMovement.produto_id == produto_id)

    if fornecedor_id is not None:
        stmt = stmt.join(StockMovement.product).where(Product.fornecedor_id == fornecedor_id)

    if tipo is not None:
        stmt = stmt.where(StockMovement.tipo == tipo.value)

    if data_inicio is not None:
        stmt = stmt.where(StockMovement.data >= data_inicio)

    if data_fim is not None:
        stmt = stmt.where(StockMovement.data <= data_fim)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_movements_summary(
    db: AsyncSession,
    produto_id: Optional[int] = None,
    fornecedor_id: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
) -> MovementSummaryResponse:
    if data_inicio and data_fim and _normalize_datetime(data_inicio) > _normalize_datetime(data_fim):
        raise BusinessRuleException("A data de início não pode ser posterior à data de término.")

    def apply_filters(statement):
        if produto_id is not None:
            statement = statement.where(StockMovement.produto_id == produto_id)
        if fornecedor_id is not None:
            statement = statement.join(StockMovement.product).where(Product.fornecedor_id == fornecedor_id)
        if data_inicio is not None:
            statement = statement.where(StockMovement.data >= data_inicio)
        if data_fim is not None:
            statement = statement.where(StockMovement.data <= data_fim)
        return statement

    count_stmt = apply_filters(select(func.count(StockMovement.id)))
    in_stmt = apply_filters(
        select(func.coalesce(func.sum(StockMovement.quantidade), 0)).where(
            StockMovement.tipo == MovementType.ENTRADA.value
        )
    )
    out_stmt = apply_filters(
        select(func.coalesce(func.sum(StockMovement.quantidade), 0)).where(
            StockMovement.tipo == MovementType.SAIDA.value
        )
    )

    total_movs = (await db.execute(count_stmt)).scalar() or 0
    total_in = (await db.execute(in_stmt)).scalar() or 0
    total_out = (await db.execute(out_stmt)).scalar() or 0

    return MovementSummaryResponse(
        total_movimentacoes=total_movs,
        total_itens_entrada=total_in,
        total_itens_saida=total_out,
        saldo_periodo=total_in - total_out,
    )



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
