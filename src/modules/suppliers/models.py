from sqlalchemy import Column, Integer, String
from src.core.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)