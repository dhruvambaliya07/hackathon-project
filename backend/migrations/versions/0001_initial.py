"""Create the initial Aatmoday Connect schema."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table("profiles", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("display_name", sa.String(120), nullable=False), sa.Column("bio", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("groups", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("name", sa.String(160), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("category", sa.String(80), nullable=False))
    op.create_index("ix_groups_name", "groups", ["name"])
    op.create_index("ix_groups_category", "groups", ["category"])
    op.create_table("events", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id")), sa.Column("title", sa.String(200), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False), sa.Column("location", sa.String(200), nullable=False))
    op.create_index("ix_events_title", "events", ["title"])
    op.create_index("ix_events_starts_at", "events", ["starts_at"])
    op.create_table("feedback", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("target_type", sa.String(40), nullable=False), sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("rating", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("events")
    op.drop_table("groups")
    op.drop_table("profiles")