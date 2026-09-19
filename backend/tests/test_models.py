from sqlalchemy import CheckConstraint, ForeignKeyConstraint

from app.db.base import Base, EMBEDDING_DIMENSION
from app.models import Event, Feedback, Group, Interest, Recommendation, User


def test_requested_tables_are_registered() -> None:
    assert {
        "users",
        "interests",
        "groups",
        "group_interests",
        "events",
        "event_interests",
        "user_interests",
        "recommendations",
        "feedback",
    } <= set(Base.metadata.tables)


def test_vector_columns_use_selected_dimension() -> None:
    assert Group.__table__.c.embedding.type.dim == EMBEDDING_DIMENSION
    assert Event.__table__.c.embedding.type.dim == EMBEDDING_DIMENSION


def test_integrity_constraints_and_foreign_keys_exist() -> None:
    assert any(isinstance(constraint, CheckConstraint) and "member_count" in str(constraint.sqltext) for constraint in Group.__table__.constraints)
    assert any(isinstance(constraint, CheckConstraint) and "end_time" in str(constraint.sqltext) for constraint in Event.__table__.constraints)
    assert any(isinstance(constraint, ForeignKeyConstraint) for constraint in Feedback.__table__.constraints)
    assert any(isinstance(constraint, ForeignKeyConstraint) for constraint in Recommendation.__table__.constraints)


def test_unique_business_fields_are_present() -> None:
    assert User.__table__.c.email.unique is True
    assert Interest.__table__.c.name.unique is True
