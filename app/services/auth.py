from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories import user as user_repo
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    SupplierRegisterRequest,
    TokenResponse,
    UserResponse,
)


async def register_supplier(
    db: AsyncSession, data: SupplierRegisterRequest
) -> UserResponse:
    existing = await user_repo.get_user_by_phone(db, data.phone)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )

    org = await user_repo.create_organization(
        db,
        name=data.organization_name,
        phone=data.phone,
        gst_number=data.gst_number,
    )

    user = await user_repo.create_user(
        db,
        organization_id=org.id,
        role=UserRole.supplier,
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.password),
    )

    return UserResponse.model_validate(user)


async def login(db: AsyncSession, data: LoginRequest) -> TokenResponse:
    user = await user_repo.get_user_by_phone(db, data.phone)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    token = create_access_token(
        data={"sub": str(user.id), "org": str(user.organization_id), "role": user.role.value}
    )
    return TokenResponse(access_token=token)


async def get_me(user: User) -> UserResponse:
    return UserResponse.model_validate(user)


async def change_password(
    db: AsyncSession, user: User, data: ChangePasswordRequest
) -> dict:
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )

    await user_repo.update_user_password(
        db, user, hash_password(data.new_password)
    )
    return {"message": "Password changed successfully"}
