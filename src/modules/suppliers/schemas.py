from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    cnpj: str = Field(..., min_length=14, max_length=18)
    telefone: Optional[str] = Field(None, max_length=20)
    email: EmailStr


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    cnpj: Optional[str] = Field(None, min_length=14, max_length=18)
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class SupplierResponse(SupplierBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
