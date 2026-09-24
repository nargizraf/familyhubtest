"""Switch the default currency from EUR to PLN.

Revision ID: 0002_currency_pln
Revises: 0001_initial
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_currency_pln"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("UPDATE expenses SET currency = 'PLN' WHERE currency = 'EUR'")
    op.execute("UPDATE budgets SET currency = 'PLN' WHERE currency = 'EUR'")
    op.alter_column("expenses", "currency", server_default="PLN", existing_type=sa.String(length=3))
    op.alter_column("budgets", "currency", server_default="PLN", existing_type=sa.String(length=3))


def downgrade() -> None:
    op.execute("UPDATE expenses SET currency = 'EUR' WHERE currency = 'PLN'")
    op.execute("UPDATE budgets SET currency = 'EUR' WHERE currency = 'PLN'")
    op.alter_column("expenses", "currency", server_default="EUR", existing_type=sa.String(length=3))
    op.alter_column("budgets", "currency", server_default="EUR", existing_type=sa.String(length=3))
