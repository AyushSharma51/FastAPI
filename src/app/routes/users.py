from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.database import get_db
from src.app.db_models import Role, User
from src.app.schemas.user_schemas import UserCreate, UserResponse, UserRoleUpdate
from src.app.security.auth import get_password_hash
from src.app.security.deps import RoleChecker, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# Require Admin role
allow_admin = RoleChecker([Role.ADMIN])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Public route: Creates a new user with the default 'VIEWER' role."""
    user_exists = db.query(User).filter(User.username == user_in.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pwd = get_password_hash(user_in.password)
    # The first user created should probably be an admin for setup purposes,
    # but normally we default to VIEWER. Let's default to VIEWER.
    new_user = User(
        username=user_in.username, hashed_password=hashed_pwd, role=Role.VIEWER
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=List[UserResponse], dependencies=[Depends(allow_admin)])
def list_users(db: Session = Depends(get_db)):
    """Admin only: List all registered users."""
    return db.query(User).all()


@router.patch(
    "/{user_id}/role", response_model=UserResponse, dependencies=[Depends(allow_admin)]
)
def assign_role(
    user_id: int, role_update: UserRoleUpdate, db: Session = Depends(get_db)
):
    """Admin only: Change a user's role."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the profile and role of the currently logged-in user."""
    return current_user
