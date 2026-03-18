from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import date as dt_date


class TeamBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    city: str = Field(min_length=2, max_length=50)
    founded_year: int = Field(ge=1800, le=2030)
    stadium: Optional[str] = Field(None, min_length=3, max_length=100)

    @field_validator("founded_year")
    def validate_year(cls, value):
        if value > dt_date.today().year:
            raise ValueError("Founded year cannot be in the future")
        return value

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int

    class Config:
        from_attributes = True

class TeamNameResponse(BaseModel):
    name: str 
    class Config:
        from_attributes = True

