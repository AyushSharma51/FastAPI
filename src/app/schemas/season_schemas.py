from datetime import date as dt_date
from pydantic import BaseModel, Field, model_validator


class Season(BaseModel):

    league_id: int
    year: int = Field(ge=1900, le=2100)
    start_date: dt_date
    end_date: dt_date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date == self.end_date:
            raise ValueError("Season cannot start and end on the same date")

        if self.start_date.year != self.year or self.end_date.year != self.year:
            raise ValueError(
                "Season year must match the year of start_date and end_date"
            )
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")

        return self


class SeasonCreate(Season):
    pass


class SeasonResponse(Season):
    id: int

    class Config:
        from_attributes = True
