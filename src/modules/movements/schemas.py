from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.modules.products.schemas import ProductResponse


class MovementType(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class StockMovementCreate(BaseModel):
    produto_id: int
    tipo: MovementType
    quantidade: int = Field(..., gt=0)
    observacao: Optional[str] = Field(None, max_length=255)


class StockMovementResponse(BaseModel):
    id: int
    produto_id: int
    tipo: str
    quantidade: int
    data: datetime
    observacao: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StockMovementDetailResponse(StockMovementResponse):
    product: Optional[ProductResponse] = None


class MovementSummaryResponse(BaseModel):
    total_movimentacoes: int
    total_itens_entrada: int
    total_itens_saida: int
    saldo_periodo: int

