from datetime import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.modules.categories.models import Category
    from src.modules.suppliers.models import Supplier
    from src.modules.movements.models import StockMovement


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    preco_custo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    preco_venda: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantidade_em_estoque: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estoque_minimo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    data_cadastro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    fornecedor_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="products")
    movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="product",
        cascade="save-update",
    )
