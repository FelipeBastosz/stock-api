from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.modules.products.models import Product


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    produto_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    observacao: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="movements")
