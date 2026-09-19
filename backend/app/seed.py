"""Deterministic demo data for the Aatmoday Connect recommendation engine."""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta, timezone
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Event, EventInterest, Group, GroupInterest, Interest, User, UserInterest
from app.services.embedding_service import generate_deterministic_embedding

SEED_NAMESPACE = uuid5(NAMESPACE_URL, "https://aatmoday.example/seed/v1")
PLACEHOLDER_IMAGE = "https://placehold.co/1200x675/png?text={slug}"

INTEREST_DATA: tuple[tuple[str, str], ...] = (
    ("AI", "Technology"),
    ("Machine Learning", "Technology"),
    ("Programming", "Technology"),
    ("Web Development", "Technology"),
    ("Robotics", "Technology"),
    ("Cybersecurity", "Technology"),
    ("Photography", "Creative"),
    ("Filmmaking", "Creative"),
    ("Graphic Design", "Creative"),
    ("Art", "Creative"),
    ("Writing", "Creative"),
    ("Drama", "Creative"),
    ("Public Speaking", "Social"),
    ("Debate", "Social"),
    ("Volunteering", "Social"),
    ("Event Management", "Social"),
    ("Leadership", "Social"),
    ("Travel", "Lifestyle"),
    ("Fitness", "Lifestyle"),
    ("Yoga", "Lifestyle"),
    ("Cooking", "Lifestyle"),
    ("Music", "Entertainment"),
    ("Dance", "Entertainment"),
    ("Gaming", "Entertainment"),
    ("Entrepreneurship", "Business"),
    ("Finance", "Business"),
    ("Marketing", "Business"),
    ("Film Studies", "Creative"),
    ("Data Science", "Technology"),
    ("Mental Wellness", "Lifestyle"),
)

COMMUNITY_DATA: tuple[tuple[str, str, str, str, tuple[tuple[str, float], ...]], ...] = (
    ("Aatmoday AI Lab", "Technology", "Build practical AI projects and learn how intelligent products move from idea to prototype.", "Innovation Hub", (("AI", 1.0), ("Machine Learning", 0.9), ("Programming", 0.8), ("Data Science", 0.7), ("Leadership", 0.4))),
    ("Robotics Makers", "Technology", "A hands-on community for students who enjoy sensors, embedded systems, and friendly robot battles.", "Makerspace 1", (("Robotics", 1.0), ("Programming", 0.8), ("AI", 0.7), ("Machine Learning", 0.5), ("Gaming", 0.3))),
    ("Web Builders Guild", "Technology", "Design, ship, and review accessible web experiences with a supportive group of builders.", "Digital Studio", (("Web Development", 1.0), ("Programming", 0.9), ("Graphic Design", 0.6), ("Marketing", 0.5), ("Entrepreneurship", 0.4))),
    ("CyberSafe Circle", "Technology", "Explore privacy, security fundamentals, and ethical security practice through guided challenges.", "Tech Commons", (("Cybersecurity", 1.0), ("Programming", 0.7), ("Data Science", 0.4), ("Debate", 0.3), ("Leadership", 0.3))),
    ("Street Lens Collective", "Creative", "Document campus life and city stories through thoughtful photography walks and critiques.", "Arts Courtyard", (("Photography", 1.0), ("Travel", 0.7), ("Filmmaking", 0.6), ("Art", 0.5), ("Writing", 0.4))),
    ("Frame by Frame", "Creative", "Learn visual storytelling from script to edit, with short films made by the community.", "Media Lab", (("Filmmaking", 1.0), ("Film Studies", 0.8), ("Photography", 0.6), ("Writing", 0.6), ("Drama", 0.5))),
    ("Design Commons", "Creative", "A critique-friendly studio for posters, interfaces, illustrations, and visual identities.", "Design Studio", (("Graphic Design", 1.0), ("Art", 0.8), ("Web Development", 0.5), ("Marketing", 0.5), ("Photography", 0.4))),
    ("Open Mic Writers", "Creative", "Write bravely, read generously, and turn everyday observations into memorable stories.", "Library Forum", (("Writing", 1.0), ("Public Speaking", 0.7), ("Drama", 0.5), ("Film Studies", 0.4), ("Debate", 0.3))),
    ("Stagecraft Society", "Creative", "Rehearse scenes, improvise together, and make theatre welcoming to first-time performers.", "Black Box Theatre", (("Drama", 1.0), ("Dance", 0.7), ("Music", 0.6), ("Public Speaking", 0.5), ("Writing", 0.4))),
    ("Campus Speakers", "Social", "Practice clear, confident communication through talks, storytelling, and constructive feedback.", "Seminar Hall", (("Public Speaking", 1.0), ("Leadership", 0.8), ("Debate", 0.7), ("Event Management", 0.5), ("Writing", 0.4))),
    ("Civic Action Network", "Social", "Turn concern into action with student-led volunteering projects for local communities.", "Student Union", (("Volunteering", 1.0), ("Leadership", 0.8), ("Event Management", 0.7), ("Public Speaking", 0.5), ("Travel", 0.3))),
    ("Debate and Diplomacy", "Social", "Discuss big ideas, sharpen reasoning, and learn to disagree with curiosity and respect.", "Debate Room", (("Debate", 1.0), ("Public Speaking", 0.8), ("Leadership", 0.6), ("Writing", 0.4), ("Finance", 0.3))),
    ("Trail and Travel Club", "Lifestyle", "Plan low-cost adventures, explore nearby places, and share practical travel skills.", "Campus Gate", (("Travel", 1.0), ("Fitness", 0.7), ("Photography", 0.6), ("Volunteering", 0.4), ("Cooking", 0.4))),
    ("Mindful Movement", "Lifestyle", "Build sustainable routines through yoga, mobility, breathwork, and conversations about wellbeing.", "Wellness Lawn", (("Yoga", 1.0), ("Fitness", 0.7), ("Mental Wellness", 0.8), ("Dance", 0.4), ("Leadership", 0.3))),
    ("Campus Kitchen", "Lifestyle", "Cook affordable, delicious meals together while learning techniques from many food traditions.", "Community Kitchen", (("Cooking", 1.0), ("Travel", 0.6), ("Event Management", 0.4), ("Volunteering", 0.4), ("Mental Wellness", 0.3))),
    ("Rhythm House", "Entertainment", "Find your groove through collaborative music sessions, dance practice, and live showcases.", "Student Plaza", (("Music", 1.0), ("Dance", 0.9), ("Drama", 0.5), ("Event Management", 0.5), ("Public Speaking", 0.3))),
    ("Game Night Union", "Entertainment", "Play together, learn game design thinking, and host welcoming tournaments for all skill levels.", "Recreation Room", (("Gaming", 1.0), ("Programming", 0.6), ("Graphic Design", 0.5), ("Leadership", 0.4), ("Event Management", 0.4))),
    ("Founders Table", "Business", "Test ideas, meet collaborators, and learn the fundamentals of building responsible ventures.", "Business Lounge", (("Entrepreneurship", 1.0), ("Finance", 0.8), ("Marketing", 0.8), ("Leadership", 0.7), ("Public Speaking", 0.5))),
    ("Money Matters", "Business", "Make finance less intimidating through practical sessions on budgeting, investing, and careers.", "Commerce Room", (("Finance", 1.0), ("Entrepreneurship", 0.6), ("Data Science", 0.5), ("Debate", 0.3), ("Leadership", 0.3))),
    ("Brand Story Studio", "Business", "Blend strategy and creativity to help student projects communicate with clarity and purpose.", "Creative Enterprise Lab", (("Marketing", 1.0), ("Graphic Design", 0.7), ("Writing", 0.6), ("Entrepreneurship", 0.6), ("Photography", 0.4))),
)

USER_DATA: tuple[tuple[str, str, str, tuple[tuple[str, float], ...]], ...] = (
    ("Maya Shah", "maya.shah@example.test", "Photography and short films help me notice stories in ordinary places.", (("Photography", 1.0), ("Filmmaking", 0.9), ("Travel", 0.7), ("Public Speaking", 0.6), ("Volunteering", 0.5))),
    ("Arjun Mehta", "arjun.mehta@example.test", "I like building intelligent machines and understanding how they work.", (("Programming", 1.0), ("AI", 0.95), ("Robotics", 0.9), ("Machine Learning", 0.8), ("Cybersecurity", 0.5))),
    ("Ishita Rao", "ishita.rao@example.test", "I express myself through rhythm, performance, and collaborative theatre.", (("Dance", 1.0), ("Music", 0.95), ("Drama", 0.9), ("Public Speaking", 0.5), ("Writing", 0.4))),
    ("Kabir Verma", "kabir.verma@example.test", "I enjoy turning practical ideas into sustainable ventures and learning how money moves.", (("Entrepreneurship", 1.0), ("Finance", 0.9), ("Marketing", 0.85), ("Leadership", 0.7), ("Public Speaking", 0.5))),
    ("Zoya Khan", "zoya.khan@example.test", "I mix gaming, technology, and visual design to make playful digital experiences.", (("Gaming", 1.0), ("Programming", 0.8), ("Graphic Design", 0.8), ("Web Development", 0.7), ("AI", 0.5))),
)


def stable_id(kind: str, key: str) -> UUID:
    return uuid5(SEED_NAMESPACE, f"{kind}:{key}")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _upsert(session: Session, model: type, identifier: UUID, values: dict) -> object:
    record = session.get(model, identifier)
    if record is None:
        record = model(id=identifier, **values)
        session.add(record)
    else:
        for key, value in values.items():
            setattr(record, key, value)
    return record


def _replace_group_interests(session: Session, group_id: UUID, interest_ids: dict[str, UUID], values: tuple[tuple[str, float], ...]) -> None:
    session.execute(delete(GroupInterest).where(GroupInterest.group_id == group_id))
    session.add_all(GroupInterest(group_id=group_id, interest_id=interest_ids[name], weight=weight) for name, weight in values)


def _replace_event_interests(session: Session, event_id: UUID, interest_ids: dict[str, UUID], values: tuple[str, ...]) -> None:
    session.execute(delete(EventInterest).where(EventInterest.event_id == event_id))
    session.add_all(EventInterest(event_id=event_id, interest_id=interest_ids[name], weight=1.0) for name in values)


def seed_database(session: Session) -> dict[str, int]:
    interest_ids: dict[str, UUID] = {}
    for name, category in INTEREST_DATA:
        identifier = stable_id("interest", name)
        interest_ids[name] = identifier
        _upsert(session, Interest, identifier, {"name": name, "category": category})

    group_ids: dict[str, UUID] = {}
    for name, category, description, location, interests in COMMUNITY_DATA:
        identifier = stable_id("group", name)
        group_ids[name] = identifier
        _upsert(session, Group, identifier, {
            "name": name,
            "description": description,
            "category": category,
            "location": location,
            "meeting_frequency": "Every two weeks",
            "member_count": 12 + len(name) % 57,
            "image_url": PLACEHOLDER_IMAGE.format(slug=slugify(name)),
            "embedding": generate_deterministic_embedding(f"{name}. {description}. {category}"),
        })
        _replace_group_interests(session, identifier, interest_ids, interests)

    event_count = 40
    community_names = [entry[0] for entry in COMMUNITY_DATA]
    for index in range(event_count):
        community_index = index % len(community_names)
        community_name = community_names[community_index]
        community = COMMUNITY_DATA[community_index]
        event_name = f"{community_name} {('Workshop', 'Showcase', 'Meetup', 'Open Session')[index % 4]} {index + 1:02d}"
        event_id = stable_id("event", event_name)
        start_date = date.today() + timedelta(days=14 + index * 4)
        start_time = datetime.combine(start_date, time(hour=10 + (index % 7)), tzinfo=timezone.utc)
        event_interests = tuple(name for name, _weight in community[4][: min(4, len(community[4]))])
        _upsert(session, Event, event_id, {
            "group_id": group_ids[community_name],
            "name": event_name,
            "description": f"A welcoming {event_name.lower()} hosted by {community_name}. Meet peers, try something new, and leave with a practical next step.",
            "start_time": start_time,
            "end_time": start_time + timedelta(hours=2),
            "location": community[3],
            "capacity": 20 + (index % 5) * 10,
            "image_url": PLACEHOLDER_IMAGE.format(slug=slugify(event_name)),
            "embedding": generate_deterministic_embedding(f"{event_name}. {community[2]}. {community[1]}. {community[3]}"),
        })
        _replace_event_interests(session, event_id, interest_ids, event_interests)

    for name, email, bio, interests in USER_DATA:
        user_id = stable_id("user", email)
        _upsert(session, User, user_id, {"name": name, "email": email, "bio": bio, "avatar_url": None})
        session.execute(delete(UserInterest).where(UserInterest.user_id == user_id))
        session.add_all(UserInterest(user_id=user_id, interest_id=interest_ids[interest], weight=weight, source="seed") for interest, weight in interests)

    session.commit()
    return {
        "interests": len(INTEREST_DATA),
        "communities": len(COMMUNITY_DATA),
        "events": event_count,
        "users": len(USER_DATA),
        "group_interests": sum(len(item[4]) for item in COMMUNITY_DATA),
        "event_interests": event_count * 4,
        "user_interests": sum(len(item[3]) for item in USER_DATA),
    }


def main() -> None:
    with SessionLocal() as session:
        counts = seed_database(session)
    print("Seed complete")
    for name, count in counts.items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
