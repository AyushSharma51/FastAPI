from datetime import date as dt_date
from pydantic import BaseModel, Field, field_validator

class PlayerLite(BaseModel):
    name: str = Field(min_length=3, max_length=99)

class Player(PlayerLite):
    
    birth_date: dt_date
    nationality: str

    @field_validator("name", "nationality")
    @classmethod
    def normalize_name(cls, value):
        if value is not None:
            return value.strip().lower()
        return value


class PlayerCreate(Player):
    pass


class PlayerResponse(Player):
    id: int
    
    class Config:
        from_attributes = True



