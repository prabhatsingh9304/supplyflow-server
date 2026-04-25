from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    SupplierRegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register-supplier", response_model=UserResponse, status_code=201)
async def register_supplier(
    data: SupplierRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await auth_service.register_supplier(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await auth_service.login(db, data)


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await auth_service.get_me(current_user)


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await auth_service.change_password(db, current_user, data)
