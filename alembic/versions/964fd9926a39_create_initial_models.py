"""create initial models

Revision ID: 964fd9926a39
Revises: 
Create Date: 2026-10-09 01:59:27.173253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '964fd9926a39'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_nome'), 'categories', ['nome'], unique=True)

    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=150), nullable=False),
        sa.Column('cnpj', sa.String(length=18), nullable=False),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_suppliers_id'), 'suppliers', ['id'], unique=False)
    op.create_index(op.f('ix_suppliers_cnpj'), 'suppliers', ['cnpj'], unique=True)
    op.create_index(op.f('ix_suppliers_email'), 'suppliers', ['email'], unique=True)

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=150), nullable=False),
        sa.Column('sku', sa.String(length=50), nullable=False),
        sa.Column('preco_custo', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('preco_venda', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('quantidade_em_estoque', sa.Integer(), server_default='0', nullable=False),
        sa.Column('estoque_minimo', sa.Integer(), server_default='0', nullable=False),
        sa.Column('data_cadastro', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('categoria_id', sa.Integer(), nullable=False),
        sa.Column('fornecedor_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['categoria_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['fornecedor_id'], ['suppliers.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_nome'), 'products', ['nome'], unique=False)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=True)
    op.create_index(op.f('ix_products_categoria_id'), 'products', ['categoria_id'], unique=False)
    op.create_index(op.f('ix_products_fornecedor_id'), 'products', ['fornecedor_id'], unique=False)

    op.create_table(
        'stock_movements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=10), nullable=False),
        sa.Column('quantidade', sa.Integer(), nullable=False),
        sa.Column('data', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('observacao', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['produto_id'], ['products.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_stock_movements_id'), 'stock_movements', ['id'], unique=False)
    op.create_index(op.f('ix_stock_movements_produto_id'), 'stock_movements', ['produto_id'], unique=False)
    op.create_index(op.f('ix_stock_movements_tipo'), 'stock_movements', ['tipo'], unique=False)
    op.create_index(op.f('ix_stock_movements_data'), 'stock_movements', ['data'], unique=False)


def downgrade() -> None:
    op.drop_table('stock_movements')
    op.drop_table('products')
    op.drop_table('suppliers')
    op.drop_table('categories')
