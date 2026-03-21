from datetime import date as dt_date

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# -------------------------
# League
# -------------------------


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    seasons: Mapped[list["Season"]] = relationship(back_populates="league")


# -------------------------
# Season
# -------------------------


class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(primary_key=True)

    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"))
    country: Mapped[str] = mapped_column(String(100))

    start_date: Mapped[dt_date]
    end_date: Mapped[dt_date]

    league: Mapped["League"] = relationship(back_populates="seasons")
    matches: Mapped[list["Match"]] = relationship(back_populates="season")
    team_players: Mapped[list["TeamPlayer"]] = relationship(back_populates="season")


# -------------------------
# Team
# -------------------------


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), unique=True)
    city: Mapped[str] = mapped_column(String(100))
    founded_year: Mapped[int]
    stadium: Mapped[str | None] = mapped_column(String(100), nullable=True)

    players: Mapped[list["TeamPlayer"]] = relationship(back_populates="team")
    match_participations: Mapped[list["MatchParticipant"]] = relationship(
        back_populates="team"
    )


# -------------------------
# Player
# -------------------------


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), unique=True)
    birth_date: Mapped[dt_date]
    nationality: Mapped[str] = mapped_column(String(100))

    teams: Mapped[list["TeamPlayer"]] = relationship(back_populates="player")
    match_stats: Mapped[list["PlayerMatchStat"]] = relationship(back_populates="player")


# -------------------------
# Team Player (Roster)
# -------------------------


class TeamPlayer(Base):
    __tablename__ = "team_players"

    __table_args__ = (
        UniqueConstraint("team_id", "player_id", "season_id", name="uq_roster_entry"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"))

    jersey_number: Mapped[int | None]

    team: Mapped["Team"] = relationship(back_populates="players")
    player: Mapped["Player"] = relationship(back_populates="teams")
    season: Mapped["Season"] = relationship(back_populates="team_players")


# -------------------------
# Match
# -------------------------


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)

    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"))

    venue: Mapped[str] = mapped_column(String(100))
    date: Mapped[dt_date]
    status: Mapped[str] = mapped_column(String(50))

    season: Mapped["Season"] = relationship(back_populates="matches")
    participants: Mapped[list["MatchParticipant"]] = relationship(
        back_populates="match"
    )
    player_stats: Mapped[list["PlayerMatchStat"]] = relationship(back_populates="match")


# -------------------------
# Match Participants (Teams in Match)
# -------------------------


class MatchParticipant(Base):
    __tablename__ = "match_participants"

    __table_args__ = (
        UniqueConstraint("match_id", "is_home", name="uq_match_home_side"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    score: Mapped[int] = mapped_column(default=0)

    is_home: Mapped[bool] = mapped_column(Boolean)
  

    @property
    def is_winner(self) -> bool | None:
        if self.score is None:
            return None
        other = next((p for p in self.match.participants if p.id != self.id), None)
        if other is None or other.score is None:
            return None
        return self.score > other.score

    match: Mapped["Match"] = relationship(back_populates="participants")
    team: Mapped["Team"] = relationship(back_populates="match_participations")


# -------------------------
# Player Match Stats
# -------------------------


class PlayerMatchStat(Base):
    __tablename__ = "player_match_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))  # ← ADD THIS

    goals: Mapped[int] = mapped_column(default=0)
    assists: Mapped[int] = mapped_column(default=0)
    minutes_played: Mapped[int] = mapped_column(default=0)

    # Also add a unique constraint — one stat row per player per match
    __table_args__ = (
        UniqueConstraint("match_id", "player_id", name="uq_player_match_stat"),
    )

    match: Mapped["Match"] = relationship(back_populates="player_stats")
    player: Mapped["Player"] = relationship(back_populates="match_stats")
    team: Mapped["Team"] = relationship()
