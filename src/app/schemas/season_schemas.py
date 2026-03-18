from datetime import date as dt_date
from enum import Enum
from pydantic import BaseModel,  model_validator
from ..schemas.league_schemas import League, LeagueName

class Country(str, Enum):
    england = "england"
    spain = "spain"
    france = "france"
    italy = "italy"
    germany = "germany"
    europe = "europe"



LEAGUE_COUNTRY_MAP = {
    LeagueName.premier_league: Country.england,
    LeagueName.la_liga: Country.spain,
    LeagueName.bundesliga: Country.germany,
    LeagueName.serie_a: Country.italy,
    LeagueName.ligue_1: Country.france,
}


class Season(BaseModel):

    league_id: int
    country:Country
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
    league:League
    


class SeasonResponse(Season):
    id: int
    league: League

    class Config:
        from_attributes = True
