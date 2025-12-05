"""Initial empty migration placeholder.

Generate a new autogen migration after reviewing models.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Intentionally empty; run `alembic revision --autogenerate -m "init"` to capture models.
    pass


def downgrade() -> None:
    pass

