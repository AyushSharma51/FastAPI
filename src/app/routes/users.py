from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.app.database import get_db
from src.app.db_models import Role, User
from src.app.schemas.user_schemas import UserCreate, UserResponse, UserRoleUpdate
from src.app.security.auth import get_password_hash
from src.app.security.deps import RoleChecker, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# Require Admin role
allow_admin = RoleChecker([Role.ADMIN])


# ================== REGISTER ==================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Public route: Create a new user with default VIEWER role.
    """

    # ❌ db.query → ✅ select
    result = await db.execute(
        select(User).where(User.username == user_in.username)
    )
    user_exists = result.scalar_one_or_none()

    if user_exists:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    hashed_pwd = get_password_hash(user_in.password)

    new_user = User(
        username=user_in.username,
        hashed_password=hashed_pwd,
        role=Role.VIEWER
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


# ================== LIST USERS ==================

@router.get(
    "/",
    response_model=List[UserResponse],
    dependencies=[Depends(allow_admin)]
)
async def list_users(
    db: AsyncSession = Depends(get_db)
):
    """
    Admin only: List all users.
    """
    result = await db.execute(select(User))
    return result.scalars().all()


# ================== ASSIGN ROLE ==================

@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    dependencies=[Depends(allow_admin)]
)
async def assign_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Admin only: Update user role.
    """

    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.role = role_update.role

    await db.commit()
    await db.refresh(user)

    return user


# ================== CURRENT USER ==================

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current logged-in user's profile.
    """
    return current_user