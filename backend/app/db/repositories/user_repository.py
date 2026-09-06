from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Account
async def get_account_by_email(db:AsyncSession,email:str)->Account|None:
    return await db.scalar(select(Account).where(Account.email==email.lower()))
