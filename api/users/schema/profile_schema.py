from datetime import date
from enum import Enum

from pydantic import BaseModel, validator
from pydantic.typing import Optional

# -------------------------------------------------#
#               Responses                          #
# -------------------------------------------------#


class GenderEnum(str, Enum):
    male = 'M'
    female = 'F'
    other = 'O'


class ProfileBaseResponse(BaseModel):
    gender: GenderEnum
    birthdate: date


class ProfileFullResponse(ProfileBaseResponse):
    job: Optional[str]
    hobbies: Optional[str]
    biography: Optional[str]


# -------------------------------------------------#
#               Payloads                           #
# -------------------------------------------------#

class ProfilePayloadCreate(ProfileBaseResponse):
    @validator('birthdate')
    def birthdate_validator(cls, birthdate):
        today = date.today()
        age_of_user = today - birthdate
        age_limit = 16
        if age_of_user.days < (age_limit * 365):
            raise ValueError("user is too young")
        return birthdate


class ProfilePayloadUpdate(BaseModel):
    gender: str
    job: Optional[str]
    hobbies: Optional[str]
    biography: Optional[str]
