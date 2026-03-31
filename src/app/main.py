from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_tables
from .routes.league import router as league_router
from .routes.matches import router as matches_router
from .routes.players import player_router, stats_router, team_player_router
from .routes.seasons import router as season_router
from .routes.standings import router as standings_router
from .routes.teams import router as teams_router
from .routes.users import router as users_router  
from .security.auth import router as auth_router


# -------------------------
# LIFESPAN FUNCTION
# -------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan controls app startup & shutdown.

    - Before yield → runs ONCE at startup
    - After yield → runs ONCE at shutdown

    """

    # STARTUP
    await create_tables()

    yield  # App starts handling requests here

    # SHUTDOWN
    print(" App shutting down...")

   
# -------------------------
# FASTAPI APP
# -------------------------

app = FastAPI(
    title="League Management API",
    version="1.0.0",
    lifespan=lifespan,  #  Added lifespan here
)
# Security & Users
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(league_router)
app.include_router(season_router)
app.include_router(teams_router)
app.include_router(player_router)
app.include_router(team_player_router)
app.include_router(stats_router)
app.include_router(matches_router)
app.include_router(standings_router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}
