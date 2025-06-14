"""Add refresh_token field to User

Revision ID: 0cafc69b0e84
Revises: a1c2d513623c
Create Date: 2025-06-05 20:30:22.566286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cafc69b0e84'
down_revision: Union[str, None] = 'a1c2d513623c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('refresh_token', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'refresh_token')
    # ### end Alembic commands ###
