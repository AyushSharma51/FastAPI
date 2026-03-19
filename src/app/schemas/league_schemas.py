from pydantic import BaseModel


class League(BaseModel):
    name: str


class LeagueCreate(League):
    pass


class LeagueResponse(League):
    id: int

    class Config:
        from_attributes = True
