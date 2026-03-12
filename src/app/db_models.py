from sqlalchemy import Date, ForeignKey, String, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date as dt_date


class Base(DeclarativeBase):
    pass


class MatchModel(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    venue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date: Mapped[dt_date] = mapped_column(Date)
    sport: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    winner_id: Mapped[int| None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    is_draw:Mapped[bool] = mapped_column(Boolean,default=False)                #add this functionality

    home_team: Mapped["TeamModel"] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped["TeamModel"] = relationship(foreign_keys=[away_team_id])
    winner: Mapped["TeamModel"] = relationship(foreign_keys=[winner_id])


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))
    founded_year: Mapped[int] = mapped_column(Integer)
    stadium: Mapped[str | None] = mapped_column(String(100), nullable=True)
