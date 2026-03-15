from datetime import date as dt_date
from typing import Literal, Optional

from pydantic import BaseModel, Field, computed_field, model_validator


class DateRangeFilters(BaseModel):
    from_date: Optional[dt_date] = Field(
        None,
        title="Start Date",
        description="Filter matches on or after this date (YYYY-MM-DD)",
        examples=["2026-01-01"],
    )
    to_date: Optional[dt_date] = Field(
        None,
        title="End Date",
        description="Filter matches on or before this date (YYYY-MM-DD)",
        examples=["2026-12-31"],
    )

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValueError("from_date must be before or equal to to_date")
        return self


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(20, ge=1, le=100, description="Items per page (max 100)")

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class SortParams(BaseModel):
    sort_by: Optional[Literal["date", "sport", "status"]] = Field(
        None,
        title="Sort By",
        description="Field to sort results by",
    )
    sort_order: Literal["asc", "desc"] = Field(
        "asc",
        title="Sort Order",
        description="Sort direction — asc for ascending, desc for descending",
    )