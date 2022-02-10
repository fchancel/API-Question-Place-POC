import re

import unidecode
from pydantic import BaseModel, EmailStr, validator
from users.schema.validator.user_validator import (password_validator,
                                                   passwords_match,
                                                   unique_email)

# -------------------------------------------------#
#               Responses                          #
# -------------------------------------------------#


class UserBasicResponse(BaseModel):
    username: str
    first_name: str
    last_name: str
    picture: str


class UserFullPublicResponse(UserBasicResponse):
    email_verified: bool
    is_verified: bool
    private_profile: bool


class UserFullResponse(UserFullPublicResponse):
    email: EmailStr
    password: str
    is_active: bool

# -------------------------------------------------#
#               Payloads                           #
# -------------------------------------------------#


class UserPayloadLogin(BaseModel):
    email: EmailStr
    password: str

    # validator
    _password_validator_password = validator(
        'password', allow_reuse=True)(password_validator)


class UserPayloadCreate(UserPayloadLogin):
    first_name: str
    last_name: str
    password2: str

    # validator
    _email_validator_unique_email = validator(
        'email', allow_reuse=True)(unique_email)
    _password_validator_match_password = validator(
        'password', 'password2', allow_reuse=True)(passwords_match)

    @ validator('first_name', 'last_name')
    def name_validator(cls, name):
        # ?# REGEX NAME : minimum 2 characters, accepts any alphanumeric
        # ?# character, space and hyphen (-)
        name = name.strip(' -')
        regex_name = "^(?:[a-zA-Z]{2,}[ |-]?)+$"
        pattern_name = re.compile(regex_name)

        name = unidecode.unidecode(name)
        if not pattern_name.match(name):
            raise ValueError('value is not a valid name')
        return name.title()


class UserPayloadUpdate(BaseModel):
    email_verified: bool
    is_active: bool
    is_verified: bool


class UserPayloadUpdateByUser(BaseModel):
    email: EmailStr
    private_profile: bool
    hashed_password: str

    # validator
    _email_validator_unique_email = validator(
        'email', allow_reuse=True)(unique_email)


class UserPayloadCreateInDB(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    first_name: str
    last_name: str
    private_profile: bool = False
    email_verified: bool = False
    is_active: bool = True
    is_verified: bool = False
    picture: str = 'media/picture/default.jpg'


class UserCreatePassword(BaseModel):
    password: str
    password2: str

    # validator
    _password_validator_password = validator(
        'password', allow_reuse=True)(password_validator)
    _password_validator_match_password = validator(
        'password', 'password2', allow_reuse=True)(passwords_match)
