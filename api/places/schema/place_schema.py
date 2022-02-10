from pydantic import BaseModel


class PlaceResponse(BaseModel):
    google_place_id: str


class PlacePayload(PlaceResponse):
    pass
