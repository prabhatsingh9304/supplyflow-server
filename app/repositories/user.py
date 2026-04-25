import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User


async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    result = await db.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_organization(
    db: AsyncSession,
    name: str,
    phone: str,
    gst_number: str | None = None,
) -> Organization:
    org = Organization(name=name, phone=phone, gst_number=gst_number)
    db.add(org)
    await db.flush()
    return org


async def create_user(
    db: AsyncSession,
    organization_id: uuid.UUID,
    role: str,
    name: str,
    phone: str,
    password_hash: str,
) -> User:
    user = User(
        organization_id=organization_id,
        role=role,
        name=name,
        phone=phone,
        password_hash=password_hash,
    )
    db.add(user)
    await db.flush()
    return user


async def update_user_password(
    db: AsyncSession, user: User, new_password_hash: str
) -> User:
    user.password_hash = new_password_hash
    await db.flush()
    return user
