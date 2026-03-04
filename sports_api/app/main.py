from fastapi import FastAPI
from .routes.matches import router as matches_router

app = FastAPI(title="Sports Matches API")

app.include_router(matches_router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}

