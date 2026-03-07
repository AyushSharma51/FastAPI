from sqlalchemy import Date, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date as dt_date

class Base(DeclarativeBase):
    pass


class MatchModel(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    home_team: Mapped[str] = mapped_column(String(50))
    away_team: Mapped[str] = mapped_column(String(50))
    venue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date: Mapped[dt_date] = mapped_column(Date)
    sport: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    winner: Mapped[str | None] = mapped_column(String(20), nullable=True)