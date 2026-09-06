from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.executor import execute_query


def add_funnel_rates(rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    previous_users: int | None = None

    for row in rows:
        users = int(row["users"])
        conversion = 1.0 if previous_users is None else (users / previous_users if previous_users else 0.0)
        dropoff = 0.0 if previous_users is None else 1.0 - conversion
        output.append(
            {
                "stage": row["stage"],
                "users": users,
                "conversion_from_previous": round(conversion, 4),
                "dropoff_from_previous": round(dropoff, 4),
            }
        )
        previous_users = users

    return output


async def get_funnel(
    db: AsyncSession,
    days: int = 30,
    channel: str | None = None,
) -> list[dict]:
    rows = await execute_query(db, "funnel", {"days": days, "channel": channel})
    return add_funnel_rates(rows)
