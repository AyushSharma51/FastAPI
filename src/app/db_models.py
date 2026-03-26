import enum
from datetime import date as dt_date

from sqlalchemy import Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass


class Role(str, enum.Enum):
    """Enum for user roles"""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    # Primary Key → uniquely identifies each user
    id: Mapped[int] = mapped_column(primary_key=True)

    # Index added because username is frequently searched (login, lookup)
    # unique=True also creates an index internally
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # Stores hashed password (never plain text)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Index used for filtering users by role (admin/editor/viewer)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.VIEWER, index=True)

    # Index used for filtering active/inactive users
    is_active: Mapped[bool] = mapped_column(default=True, index=True)


# -------------------------
# League
# -------------------------


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Index because leagues are searched by name
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Used for soft delete filtering → hence indexed
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)

    # Relationship: One league → many seasons
    # back_populates connects this to Season.league
    seasons: Mapped[list["Season"]] = relationship(back_populates="league")


# -------------------------
# Season
# -------------------------


class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign Key → links season to league
    # Index added because joins/filtering happen on league_id
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), index=True)

    # Index because filtering by country is common
    country: Mapped[str] = mapped_column(String(100), index=True)

    start_date: Mapped[dt_date]
    end_date: Mapped[dt_date]

    # Relationship mapping
    league: Mapped["League"] = relationship(back_populates="seasons")

    # One season → many matches
    matches: Mapped[list["Match"]] = relationship(back_populates="season")

    # One season → many team-player entries
    team_players: Mapped[list["TeamPlayer"]] = relationship(back_populates="season")


# -------------------------
# Team
# -------------------------


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Index because teams are searched by name
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Index for filtering teams by city
    city: Mapped[str] = mapped_column(String(100), index=True)

    # Index for queries like "teams founded after X year"
    founded_year: Mapped[int] = mapped_column(index=True)

    stadium: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # One team → many players
    players: Mapped[list["TeamPlayer"]] = relationship(back_populates="team")

    # One team → many match participations
    match_participations: Mapped[list["MatchParticipant"]] = relationship(
        back_populates="team"
    )


# -------------------------
# Player
# -------------------------


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Index for searching players
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Index for filtering by age/date
    birth_date: Mapped[dt_date] = mapped_column(index=True)

    # Index for filtering by nationality
    nationality: Mapped[str] = mapped_column(String(100), index=True)

    # Many-to-many via TeamPlayer
    teams: Mapped[list["TeamPlayer"]] = relationship(back_populates="player")

    # One player → many match stats
    match_stats: Mapped[list["PlayerMatchStat"]] = relationship(back_populates="player")


# -------------------------
# Team Player (Roster)
# -------------------------


class TeamPlayer(Base):
    __tablename__ = "team_players"

    # Unique constraint ensures:
    # One player can belong to one team per season only
    __table_args__ = (
        UniqueConstraint("team_id", "player_id", "season_id", name="uq_roster_entry"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign Keys + indexes → critical for joins
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), index=True)

    jersey_number: Mapped[int | None]

    # Relationship mappings
    team: Mapped["Team"] = relationship(back_populates="players")
    player: Mapped["Player"] = relationship(back_populates="teams")
    season: Mapped["Season"] = relationship(back_populates="team_players")


# -------------------------
# Match
# -------------------------


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)

    # FK + index → used in joins
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), index=True)

    # Indexed for filtering/search
    venue: Mapped[str] = mapped_column(String(100), index=True)

    # Indexed for sorting/filtering matches by date
    date: Mapped[dt_date] = mapped_column(index=True)

    # Indexed for filtering by match status
    status: Mapped[str] = mapped_column(String(50), index=True)

    season: Mapped["Season"] = relationship(back_populates="matches")

    participants: Mapped[list["MatchParticipant"]] = relationship(
        back_populates="match"
    )

    player_stats: Mapped[list["PlayerMatchStat"]] = relationship(back_populates="match")


# -------------------------
# Match Participants
# -------------------------


class MatchParticipant(Base):
    __tablename__ = "match_participants"

    # Constraint ensures only one home team per match
    __table_args__ = (
        UniqueConstraint("match_id", "is_home", name="uq_match_home_side"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # FK + index → improves join performance
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)

    score: Mapped[int] = mapped_column(default=0)

    # Index for filtering home/away teams
    is_home: Mapped[bool] = mapped_column(Boolean, index=True)

    match: Mapped["Match"] = relationship(back_populates="participants")
    team: Mapped["Team"] = relationship(back_populates="match_participations")


# -------------------------
# Player Match Stats
# -------------------------


class PlayerMatchStat(Base):
    __tablename__ = "player_match_stats"

    id: Mapped[int] = mapped_column(primary_key=True)

    # FK + index → used heavily in joins
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)

    goals: Mapped[int] = mapped_column(default=0)
    assists: Mapped[int] = mapped_column(default=0)
    minutes_played: Mapped[int] = mapped_column(default=0)

    # Ensures one stat per player per match
    __table_args__ = (
        UniqueConstraint("match_id", "player_id", name="uq_player_match_stat"),
    )

    match: Mapped["Match"] = relationship(back_populates="player_stats")
    player: Mapped["Player"] = relationship(back_populates="match_stats")
    team: Mapped["Team"] = relationship()