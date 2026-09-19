"""Persist profile goals and traits and prevent duplicate feedback."""

from alembic import op
import sqlalchemy as sa

revision = "0002_profile_feedback_state"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("goals", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("users", sa.Column("traits", sa.JSON(), nullable=False, server_default="[]"))
    op.create_unique_constraint("uq_feedback_user_recommendation_type", "feedback", ["user_id", "recommendation_id", "feedback_type"])


def downgrade() -> None:
    op.drop_constraint("uq_feedback_user_recommendation_type", "feedback", type_="unique")
    op.drop_column("users", "traits")
    op.drop_column("users", "goals")