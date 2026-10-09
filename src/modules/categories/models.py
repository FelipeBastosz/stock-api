from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.modules.products.models import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="save-update",
    )