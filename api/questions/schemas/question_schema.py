from datetime import datetime

from places.schema.place_schema import PlacePayload, PlaceResponse
from pydantic import BaseModel
from pydantic.typing import List, Optional
from users.schema.user_schema import UserBasicResponse


class QuestionBase(BaseModel):
    title: str
    text: str
    place: PlaceResponse

# -------------------------------------------------#
#               Responses                          #
# -------------------------------------------------#


class QuestionResponse(QuestionBase):
    uid: str
    slug: str
    created: datetime
    edited: Optional[datetime]
    number_answers: int
    validated: bool
    deprecated: bool
    follow: bool
    hidden: bool
    author: UserBasicResponse


class QuestionPagination(BaseModel):
    skip: int
    limit: int
    total: int
    data: List[QuestionResponse]


# -------------------------------------------------#
#               Payloads                           #
# -------------------------------------------------#


class QuestionPayload(QuestionBase):
    place: PlacePayload
