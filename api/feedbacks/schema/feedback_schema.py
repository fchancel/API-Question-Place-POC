from datetime import datetime
from feedbacks.schema.distinction_schema import (DistinctionPayload,
                                                 DistinctionResponse)
from places.schema.place_schema import PlacePayload, PlaceResponse
from pydantic import BaseModel, validator
from pydantic.typing import List
from users.schema.user_schema import UserBasicResponse


class FeedbackBase(BaseModel):
    rating: int
    comment: str


# -------------------------------------------------#
#               Responses                          #
# -------------------------------------------------#

class FeedbackResponse(FeedbackBase):
    distinction: DistinctionResponse
    date: datetime
    place: PlaceResponse


class FeedbackWithUser(FeedbackResponse):
    user: UserBasicResponse


class FeedbackPagination(BaseModel):
    skip: int
    limit: int
    total: int
    data: List[FeedbackWithUser]


class FeedbacksNumber(BaseModel):
    number: int


class FeedbackRatingWithNumber(FeedbacksNumber):
    rating: int


# -------------------------------------------------#
#               Payloads                           #
# -------------------------------------------------#


class FeedbackPayload(FeedbackBase):
    distinction: DistinctionPayload
    place: PlacePayload

    @validator('rating')
    def rating_validator(cls, rating):
        if rating > 5 or rating < 0:
            raise ValueError('value is not a valid rating')
        return rating
