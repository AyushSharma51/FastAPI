from fastapi import FastAPI
from .routes.matches import router as matches_router
from .database import create_tables



app = FastAPI(title="Sports Matches API")


@app.on_event("startup")
def on_startup():
    create_tables()
    


app.include_router(matches_router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}
