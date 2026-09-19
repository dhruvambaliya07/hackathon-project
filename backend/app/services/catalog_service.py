from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Event, EventInterest, Group, GroupInterest, Interest
from app.schemas.events import EventDetail, EventGroupResponse, EventSummary
from app.schemas.groups import GroupDetail, GroupInterestResponse, GroupSummary


def _event_summary(event: Event) -> EventSummary:
    return EventSummary(
        id=event.id,
        group_id=event.group_id,
        title=event.name,
        description=event.description,
        starts_at=event.start_time,
        ends_at=event.end_time,
        location=event.location,
        capacity=event.capacity,
        image_url=event.image_url,
    )


def _group_summary(group: Group) -> GroupSummary:
    return GroupSummary.model_validate(group)


def _interest_response(link: GroupInterest | EventInterest) -> GroupInterestResponse:
    interest = link.interest
    return GroupInterestResponse(id=interest.id, name=interest.name, category=interest.category, weight=link.weight)


def _group_filters(query, *, search: str | None, category: str | None, interest: str | None):
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(or_(Group.name.ilike(pattern), Group.description.ilike(pattern)))
    if category:
        query = query.where(func.lower(Group.category) == category.strip().lower())
    if interest:
        query = query.join(GroupInterest, GroupInterest.group_id == Group.id).join(Interest, Interest.id == GroupInterest.interest_id)
        query = query.where(func.lower(Interest.name) == interest.strip().lower())
    return query


def list_groups(session: Session, *, search: str | None, category: str | None, interest: str | None, page: int, page_size: int) -> tuple[list[GroupSummary], int]:
    base_query = _group_filters(select(Group.id), search=search, category=category, interest=interest).distinct()
    total = session.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    groups_query = _group_filters(
        select(Group).options(selectinload(Group.interests).selectinload(GroupInterest.interest)),
        search=search,
        category=category,
        interest=interest,
    ).distinct().order_by(Group.name).offset((page - 1) * page_size).limit(page_size)
    groups = session.scalars(groups_query).unique().all()
    return [_group_summary(group) for group in groups], total


def get_group(session: Session, group_id: UUID) -> GroupDetail | None:
    group_query = select(Group).where(Group.id == group_id).options(selectinload(Group.interests).selectinload(GroupInterest.interest))
    group = session.scalar(group_query)
    if group is None:
        return None
    now = datetime.now(timezone.utc)
    upcoming_query = (
        select(Event)
        .where(Event.group_id == group_id, Event.start_time >= now)
        .order_by(Event.start_time)
        .limit(20)
    )
    upcoming_events = session.scalars(upcoming_query).all()
    return GroupDetail(
        **_group_summary(group).model_dump(),
        interests=[_interest_response(link) for link in group.interests],
        upcoming_events=[_event_summary(event) for event in upcoming_events],
    )


def _event_filters(query, *, search: str | None, group_id: UUID | None, category: str | None, from_date: datetime | None, to_date: datetime | None):
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(or_(Event.name.ilike(pattern), Event.description.ilike(pattern), Event.location.ilike(pattern)))
    if group_id:
        query = query.where(Event.group_id == group_id)
    if category:
        query = query.join(Group, Group.id == Event.group_id).where(func.lower(Group.category) == category.strip().lower())
    if from_date:
        query = query.where(Event.start_time >= from_date)
    if to_date:
        query = query.where(Event.start_time <= to_date)
    return query


def list_events(session: Session, *, search: str | None, group_id: UUID | None, category: str | None, from_date: datetime | None, to_date: datetime | None, page: int, page_size: int) -> tuple[list[EventSummary], int]:
    base_query = _event_filters(select(Event.id), search=search, group_id=group_id, category=category, from_date=from_date, to_date=to_date).distinct()
    total = session.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    events_query = _event_filters(
        select(Event).options(selectinload(Event.group)),
        search=search,
        group_id=group_id,
        category=category,
        from_date=from_date,
        to_date=to_date,
    ).distinct().order_by(Event.start_time, Event.name).offset((page - 1) * page_size).limit(page_size)
    events = session.scalars(events_query).unique().all()
    return [_event_summary(event) for event in events], total


def get_event(session: Session, event_id: UUID) -> EventDetail | None:
    event_query = (
        select(Event)
        .where(Event.id == event_id)
        .options(
            selectinload(Event.group),
            selectinload(Event.interests).selectinload(EventInterest.interest),
        )
    )
    event = session.scalar(event_query)
    if event is None:
        return None
    related_query = (
        select(Event)
        .where(Event.group_id == event.group_id, Event.id != event.id, Event.start_time >= datetime.now(timezone.utc))
        .order_by(Event.start_time)
        .limit(10)
    )
    related_events = session.scalars(related_query).all()
    return EventDetail(
        **_event_summary(event).model_dump(),
        group=EventGroupResponse(id=event.group.id, name=event.group.name, category=event.group.category),
        interests=[_interest_response(link) for link in event.interests],
        related_events=[_event_summary(related) for related in related_events],
    )