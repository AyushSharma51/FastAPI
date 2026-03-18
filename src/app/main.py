from fastapi import FastAPI
from .routes.matches import router as matches_router
from .routes.teams import router as teams_router
from .routes.league import router as league_router
from .routes.players import router as player_router
from .routes.seasons import router as season_router
from .routes.standings import router as standings_router
from .routes.team_players import router as team_players_router
from .routes.match_participants import router as match_participants_router
from .routes.player_match_stats import router as player_stats_router
from .database import create_tables


app = FastAPI(title="Football League Management System")


@app.on_event("startup")
def on_startup():
    create_tables()

app.include_router(league_router)
app.include_router(season_router)
app.include_router(teams_router)
app.include_router(player_router)
app.include_router(team_players_router)
app.include_router(matches_router)
app.include_router(match_participants_router)
app.include_router(player_stats_router)
app.include_router(standings_router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}
