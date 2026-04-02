from datetime import date 
from typing import Optional

from pydantic import BaseModel, model_validator

from ..schemas.league_schemas import League


class Season(BaseModel):

    league_id: int
    country: str
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date == self.end_date:
            raise ValueError("Season cannot start and end on the same date")
        return self
    model_config = {
        "from_attributes": True
    }

class SeasonCreate(Season):
    pass

class SeasonUpdate(BaseModel):
    league_id: Optional[int] = None
    country: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class SeasonResponsewoLeague(Season):
    league: League


class SeasonResponse(Season):
    id: int
    league: League

    class Config:
        from_attributes = True
