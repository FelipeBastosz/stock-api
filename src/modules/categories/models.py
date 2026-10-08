from sqlalchemy import Column, Integer, String
from src.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)