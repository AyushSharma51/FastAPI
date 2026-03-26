from pydantic import BaseModel

from src.app.db_models import Role


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: Role
    is_active: bool

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str
