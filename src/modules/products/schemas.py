from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.modules.categories.schemas import CategoryResponse
from src.modules.suppliers.schemas import SupplierResponse


class ProductBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    sku: str = Field(..., min_length=2, max_length=50)
    preco_custo: Decimal = Field(..., gt=0)
    preco_venda: Decimal = Field(..., gt=0)
    quantidade_em_estoque: int = Field(0, ge=0)
    estoque_minimo: int = Field(0, ge=0)
    categoria_id: int
    fornecedor_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    sku: Optional[str] = Field(None, min_length=2, max_length=50)
    preco_custo: Optional[Decimal] = Field(None, gt=0)
    preco_venda: Optional[Decimal] = Field(None, gt=0)
    quantidade_em_estoque: Optional[int] = Field(None, ge=0)
    estoque_minimo: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = None
    fornecedor_id: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    data_cadastro: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductDetailResponse(ProductResponse):
    category: Optional[CategoryResponse] = None
    supplier: Optional[SupplierResponse] = None

