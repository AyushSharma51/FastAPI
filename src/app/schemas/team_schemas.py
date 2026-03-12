from typing import Optional
from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    city: str = Field(min_length=2, max_length=50)
    founded_year: int = Field(ge=1800, le=2030)
    stadium: Optional[str] = Field(None, min_length=3, max_length=100)


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: int

    class Config:
        from_attributes = True
