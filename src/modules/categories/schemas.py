from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)


class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
