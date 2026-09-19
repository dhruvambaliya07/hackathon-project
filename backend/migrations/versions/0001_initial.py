"""Create the complete Aatmoday Connect PostgreSQL schema."""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

EMBEDDING_DIMENSION = 1536


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "interests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_interests_name"),
    )
    op.create_index("ix_interests_name", "interests", ["name"])
    op.create_index("ix_interests_category", "interests", ["category"])

    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("meeting_frequency", sa.String(80), nullable=True),
        sa.Column("member_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSION), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("member_count >= 0", name="ck_groups_member_count_nonnegative"),
    )
    op.create_index("ix_groups_name", "groups", ["name"])
    op.create_index("ix_groups_category", "groups", ["category"])

    op.create_table(
        "group_interests",
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("interest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("weight", sa.Float(), server_default="1", nullable=False),
        sa.UniqueConstraint("group_id", "interest_id", name="uq_group_interests_group_interest"),
        sa.CheckConstraint("weight >= 0 AND weight <= 1", name="ck_group_interests_weight_range"),
    )
    op.create_index("ix_group_interests_interest_id", "group_interests", ["interest_id"])

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location", sa.String(200), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSION), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("capacity IS NULL OR capacity >= 0", name="ck_events_capacity_nonnegative"),
        sa.CheckConstraint("end_time IS NULL OR end_time > start_time", name="ck_events_end_after_start"),
    )
    op.create_index("ix_events_group_id", "events", ["group_id"])
    op.create_index("ix_events_name", "events", ["name"])
    op.create_index("ix_events_start_time", "events", ["start_time"])

    op.create_table(
        "event_interests",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("interest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("weight", sa.Float(), server_default="1", nullable=False),
        sa.UniqueConstraint("event_id", "interest_id", name="uq_event_interests_event_interest"),
        sa.CheckConstraint("weight >= 0 AND weight <= 1", name="ck_event_interests_weight_range"),
    )
    op.create_index("ix_event_interests_interest_id", "event_interests", ["interest_id"])

    op.create_table(
        "user_interests",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("interest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("weight", sa.Float(), server_default="1", nullable=False),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("weight >= 0 AND weight <= 1", name="ck_user_interests_weight_range"),
    )
    op.create_index("ix_user_interests_interest_id", "user_interests", ["interest_id"])

    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_type", sa.String(40), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("reason", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("score >= 0 AND score <= 1", name="ck_recommendations_score_range"),
    )
    op.create_index("ix_recommendations_user_id", "recommendations", ["user_id"])
    op.create_index("ix_recommendations_target", "recommendations", ["target_type", "target_id"])

    op.create_table(
        "feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("target_type", sa.String(40), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feedback_type", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])
    op.create_index("ix_feedback_recommendation_id", "feedback", ["recommendation_id"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("recommendations")
    op.drop_table("user_interests")
    op.drop_table("event_interests")
    op.drop_table("events")
    op.drop_table("group_interests")
    op.drop_table("groups")
    op.drop_table("interests")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
