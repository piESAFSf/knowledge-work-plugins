"""add line user id to company"""

from alembic import op
import sqlalchemy as sa

revision = '20240902_0002'
down_revision = '20240901_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('companies', sa.Column('line_user_id', sa.String(length=255), nullable=True))
    op.create_unique_constraint('uq_companies_line_user_id', 'companies', ['line_user_id'])


def downgrade() -> None:
    op.drop_constraint('uq_companies_line_user_id', 'companies', type_='unique')
    op.drop_column('companies', 'line_user_id')
