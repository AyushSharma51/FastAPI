from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator, field_validator


class LeagueName(str, Enum):
    champions_league = "champions league"
    premier_league = "premier league"
    la_liga = "la liga"
    bundesliga = "bundesliga"
    serie_a = "serie a"
    ligue_1 = "ligue 1"


class Country(str, Enum):
    england = "england"
    spain = "spain"
    france = "france"
    italy = "italy"
    germany = "germany"


LEAGUE_COUNTRY_MAP = {
    LeagueName.premier_league: Country.england,
    LeagueName.la_liga: Country.spain,
    LeagueName.bundesliga: Country.germany,
    LeagueName.serie_a: Country.italy,
    LeagueName.ligue_1: Country.france,
}


class League(BaseModel):
    name: LeagueName
    country: Optional[Country] = Field(min_length=2, max_length=50)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value):
        if value is not None:
            return value.strip().lower()
        return value

    @model_validator(mode="after")
    def validate_league_country(self):

        # Champions League allowed everywhere
        if self.name == LeagueName.champions_league:
            return self

        expected_country = LEAGUE_COUNTRY_MAP.get(self.name)

        if expected_country != self.country:
            raise ValueError(
                f"{self.name.value} can only be played in {expected_country.value}"
            )

        return self


class LeagueCreate(League):
    pass


class LeagueResponse(League):
    id: int

    class Config:
        from_attributes = True
