from datetime import datetime

from pydantic import BaseModel
from pydantic.typing import List, Optional
from users.schema.user_schema import UserBasicResponse


class CommentBase(BaseModel):
    text: str


class CommentResponse(CommentBase):
    uid: str
    created: datetime
    edited: Optional[datetime]
    author: UserBasicResponse


class CommentPagination(BaseModel):
    skip: int
    limit: int
    total: int
    data: List[CommentResponse]


class CommentPayload(CommentBase):
    pass
