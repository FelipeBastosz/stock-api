from typing import List
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BusinessRuleException, ConflictException, EntityNotFoundException
from src.modules.categories.models import Category
from src.modules.categories.schemas import CategoryCreate, CategoryUpdate
from src.modules.products.models import Product


async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    normalized_name = data.nome.strip()
    stmt = select(Category).where(func.lower(Category.nome) == normalized_name.lower())
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing:
        raise ConflictException(f"Já existe uma categoria cadastrada com o nome '{normalized_name}'.")

    category = Category(nome=normalized_name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def list_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Category]:
    stmt = select(Category).offset(skip).limit(limit).order_by(Category.id.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_category_by_id(db: AsyncSession, category_id: int) -> Category:
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        raise EntityNotFoundException("Categoria", category_id)

    return category


async def update_category(db: AsyncSession, category_id: int, data: CategoryUpdate) -> Category:
    category = await get_category_by_id(db, category_id)

    if data.nome is not None:
        normalized_name = data.nome.strip()
        if normalized_name.lower() != category.nome.lower():
            conflict_stmt = select(Category).where(
                func.lower(Category.nome) == normalized_name.lower(),
                Category.id != category_id,
            )
            conflict = (await db.execute(conflict_stmt)).scalar_one_or_none()
            if conflict:
                raise ConflictException(f"Já existe uma categoria cadastrada com o nome '{normalized_name}'.")

        category.nome = normalized_name

    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int) -> None:
    category = await get_category_by_id(db, category_id)

    count_stmt = select(func.count(Product.id)).where(Product.categoria_id == category_id)
    linked_products = (await db.execute(count_stmt)).scalar() or 0

    if linked_products > 0:
        raise BusinessRuleException(
            f"Não é possível excluir a categoria '{category.nome}' pois existem {linked_products} produto(s) vinculado(s) a ela."
        )

    await db.delete(category)
    await db.commit()
