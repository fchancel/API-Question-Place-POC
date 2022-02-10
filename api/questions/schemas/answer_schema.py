from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic.typing import List, Optional
from users.schema.user_schema import UserBasicResponse


class AnswerBase(BaseModel):
    text: str


class VoteEnum(str, Enum):
    up = 'up'
    down = 'down'


class AnswerResponse(AnswerBase):
    uid: str
    created: datetime
    edited: Optional[datetime]
    number_comments: int
    vote: int
    validated: bool
    deprecated: bool
    author: UserBasicResponse


class AnswerPagination(BaseModel):
    skip: int
    limit: int
    total: int
    data: List[AnswerResponse]


class AnswerPayload(AnswerBase):
    pass
