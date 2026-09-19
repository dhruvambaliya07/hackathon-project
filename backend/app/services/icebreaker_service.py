from uuid import UUID


class IcebreakerService:
    async def generate(self, user_id: UUID | None, group_id: UUID | None, event_id: UUID | None, context: str | None) -> list[str]:
        return []