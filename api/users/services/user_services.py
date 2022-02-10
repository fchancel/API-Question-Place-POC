import re
from datetime import datetime, timedelta

from config import get_settings
from fastapi import Request
from general.schema.email_schema import EmailValidation
from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from pydantic.typing import Optional
from users.nodes.gamification_node import GamificationNode
from users.nodes.profile_node import ProfileNode
from users.nodes.statistic_profile_node import StatisticProfileNode
from users.nodes.user_node import UserNode
from users.schema.profile_schema import ProfilePayloadCreate
from users.schema.user_schema import UserPayloadCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_password_hash(password):
    return pwd_context.hash(password)


def create_username(first_name: str, last_name: str) -> str:
    """
    Create a unique username from first name and last name user.
    Username format: <first_name><first_char_of_last_name>#<int>
    example: Florian Chancelade = florianc3918

    How it work : Retrieve all users thanks to the first part of username,
    split all username for separate first part of username and the unique
    number. Finds the last unique number. Create the unique username.
    """
    first_name = first_name.translate(str.maketrans('', '', '- '))
    base_username = first_name.lower() + last_name[0].lower()
    nb = 0
    indice = 0
    for result in UserNode.nodes.filter(username__startswith=base_username):
        if indice == 0:
            first_digit = re.search(r"\d", result.username).start()
        id_username = result.username[first_digit:]
        if int(id_username) >= nb:
            nb = int(id_username)
    username = f"{base_username}{str(nb+1)}"
    return username


def save_user(user_payload: UserPayloadCreate, profile_payload: ProfilePayloadCreate):
    username = create_username(user_payload.first_name, user_payload.last_name)
    user_payload.password = create_password_hash(user_payload.password)
    user = UserNode(**user_payload.dict(),
                    username=username)
    user.save()
    profile = ProfileNode(**profile_payload.dict())
    profile.save()
    gamification = GamificationNode()
    gamification.save()
    statistic_profile = StatisticProfileNode()
    statistic_profile.save()
    user.profile.connect(profile)
    user.gamification.connect(gamification)
    user.statistic_profile.connect(statistic_profile)
    return user


def send_validation_email(user: UserNode, request: Request):
    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes_mail)
    access_token = create_access_token(data={"uid": user.uid}, expires_delta=access_token_expires
                                       )
    link = request.url_for("verify_email", **{'token': str(access_token)})
    email_body = f"Hi {user.first_name}, use the link below to validate your email address {link}"
    email_subject = 'Validate your email - Tripeerz'
    data = EmailValidation(email_body=email_body,
                           email_subject=email_subject,
                           to_email=[user.email])
    return data


def authenticate_user(email: EmailStr, password: str):
    user = UserNode.get_node_with_email(email)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


def check_autorization_authenticate_user(user: UserNode):
    if not user.is_active:
        return False
    elif not user.email_verified:
        return False
    return True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    settings = get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm_hash)
    return encoded_jwt
