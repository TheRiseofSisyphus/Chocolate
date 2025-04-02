"""Initial

Revision ID: 181b053b221f
Revises: 
Create Date: 2025-04-02 15:59:07.673219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '181b053b221f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('agents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('operators',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('agent_bank_accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=False),
    sa.Column('bank_name', sa.String(length=255), nullable=False),
    sa.Column('card_number', sa.String(length=50), nullable=False),
    sa.Column('account_number', sa.String(length=100), nullable=True),
    sa.Column('iban', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('agent_phones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(length=30), nullable=False),
    sa.Column('is_primary', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('agent_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=False),
    sa.Column('operator_id', sa.Integer(), nullable=False),
    sa.Column('session_start', sa.DateTime(), nullable=True),
    sa.Column('session_end', sa.DateTime(), nullable=True),
    sa.Column('start_balance', sa.Numeric(precision=18, scale=2), nullable=True),
    sa.Column('stop_balance', sa.Numeric(precision=18, scale=2), nullable=True),
    sa.Column('agent_percent', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('agent_payment', sa.Numeric(precision=18, scale=2), nullable=True),
    sa.Column('turnover', sa.Numeric(precision=18, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['operator_id'], ['operators.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_session_id', sa.Integer(), nullable=False),
    sa.Column('deposit_id', sa.String(length=100), nullable=True),
    sa.Column('deposit_amount', sa.Numeric(precision=18, scale=2), nullable=True),
    sa.Column('withdraw_id', sa.String(length=100), nullable=True),
    sa.Column('withdraw_amount', sa.Numeric(precision=18, scale=2), nullable=True),
    sa.Column('commission', sa.Numeric(precision=18, scale=2), nullable=True),
    sa.Column('transaction_type', sa.String(length=50), nullable=True),
    sa.Column('exchange_rate', sa.Numeric(precision=18, scale=8), nullable=True),
    sa.ForeignKeyConstraint(['agent_session_id'], ['agent_sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('agent_sessions')
    op.drop_table('agent_phones')
    op.drop_table('agent_bank_accounts')
    op.drop_table('operators')
    op.drop_table('agents')
    # ### end Alembic commands ###
