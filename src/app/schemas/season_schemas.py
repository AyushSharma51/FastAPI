from datetime import date as dt_date

from pydantic import BaseModel, model_validator

from ..schemas.league_schemas import League


class Season(BaseModel):

    league_id: int
    country: str
    start_date: dt_date
    end_date: dt_date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date == self.end_date:
            raise ValueError("Season cannot start and end on the same date")
        return self


class SeasonCreate(Season):
    pass


class SeasonResponsewoLeague(Season):
    league: League


class SeasonResponse(Season):
    id: int
    league: League

    class Config:
        from_attributes = True
