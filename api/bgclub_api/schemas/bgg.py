from pydantic import BaseModel


class BggSearchItem(BaseModel):
    bgg_id: int
    title: str
    year: int | None
