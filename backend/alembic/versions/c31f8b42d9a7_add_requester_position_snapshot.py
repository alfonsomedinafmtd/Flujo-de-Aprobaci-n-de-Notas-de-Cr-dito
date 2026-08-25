"""add requester position snapshot

Revision ID: c31f8b42d9a7
Revises: 9168bb41f184
Create Date: 2026-08-25 12:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c31f8b42d9a7"
down_revision: Union[str, Sequence[str], None] = "9168bb41f184"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "credit_notes",
        sa.Column("requester_position_title", sa.String(length=100), nullable=True),
    )
    op.execute(
        """
        UPDATE credit_notes
        SET requester_position_title = COALESCE(
            (
                SELECT positions.title
                FROM user_accounts
                JOIN employees ON employees.id = user_accounts.employee_id
                JOIN positions ON positions.id = employees.position_id
                WHERE user_accounts.id = credit_notes.created_by_user_id
            ),
            'Cargo no disponible'
        )
        """
    )
    with op.batch_alter_table("credit_notes") as batch_op:
        batch_op.alter_column(
            "requester_position_title",
            existing_type=sa.String(length=100),
            nullable=False,
        )
        batch_op.create_index(
            "ix_credit_notes_requester_position_title",
            ["requester_position_title"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("credit_notes") as batch_op:
        batch_op.drop_index("ix_credit_notes_requester_position_title")
        batch_op.drop_column("requester_position_title")
