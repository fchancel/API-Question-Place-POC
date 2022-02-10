from datetime import timedelta
from typing import Optional

from config import get_settings
from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException, Query,
                     Request, responses, status)
from fastapi.security import OAuth2PasswordRequestForm
from general.schema.email_schema import EmailValidation
from general.services.utils_services import send_email
from jose import jwt
from users.dependencies.fields_dependencies import FilterParams, filter_fields
from users.dependencies.user_dependencies import GetCurrentUser
from users.nodes.user_node import UserNode
from users.schema.profile_schema import ProfilePayloadCreate
from users.schema.token_schema import Token
from users.schema.user_schema import (UserBasicResponse,
                                      UserFullPublicResponse,
                                      UserPayloadCreate)
from users.services.user_services import (authenticate_user,
                                          check_autorization_authenticate_user,
                                          create_access_token, save_user,
                                          send_validation_email)

tags_metadata = [{"name": "users",  "description": "Operations with users. The **login** logic is also here.", }]
router = APIRouter(tags={"Users"}, prefix='/users')


@ router.post('', response_model=UserBasicResponse, status_code=status.HTTP_201_CREATED,
              summary="Create a new user")
def create_user(request: Request,
                bg_tasks: BackgroundTasks,
                user_payload: UserPayloadCreate,
                profile_payload: ProfilePayloadCreate):
    user = save_user(user_payload, profile_payload)

    data_email: EmailValidation = send_validation_email(user, request)

    bg_tasks.add_task(send_email,
                      data_email.email_body,
                      data_email.to_email,
                      data_email.email_subject)
    return user.dict()


@ router.get("/verify_email/{token}", summary="Verify user email with a token")
def verify_email(token: str):
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.secret_key,
            algorithms=[settings.algorithm_hash])
        user = UserNode.get_node_with_uid(payload.get('uid'))
        if not user.email_verified:
            user.email_verified = True
            user.save()
        return responses.JSONResponse({'message': 'successfully activated'}, status_code=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        return responses.JSONResponse({'error': 'activation expired'}, status_code=status.HTTP_400_BAD_REQUEST)
    except jwt.JWTError:
        return responses.JSONResponse({'error': 'invalid token'}, status_code=status.HTTP_400_BAD_REQUEST)


@ router.post("/token", response_model=Token, summary="Create a new authentification token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not check_autorization_authenticate_user(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes_login)
    access_token = create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@ router.get("/current", response_model=UserBasicResponse, summary='Get the authenticate user')
async def read_users_me(current_user: UserNode = Depends(GetCurrentUser(active=True, auto_error=True))):
    user = UserFullPublicResponse(**current_user.dict())
    return user


possible_fields = ["gender", "birthdate", "job", "biography", "email_verified", "is_verified",
                   "private_profile", "username", "first_name", "last_name", "picture", "rating", "response_rate",
                   "date_joined", "response_time", "last_connection", ]

display_types = {"card": ["username", "first_name", "last_name", "picture", "rating"],
                 "complete": possible_fields}


@ router.get("/{username}")
def get_profile(username: str,
                display_type: str = Query(None, enum=[i for i in display_types.keys()]),
                fields: Optional[str] = Depends(filter_fields)):
    """
    - **return**: An object representing the user profile, which will be composed of the fields
    specified in the "fields" parameter.
        If no users are found, a 404 error is returned
    """
    user = UserNode.get_user_full_profile(username)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    filter_params = FilterParams(display_type, fields)
    fields = filter_params.validate(possible_fields, display_types)

    response = {}
    for field in fields:
        response[field] = user[field]

    return response


@ router.get("/search/{search}")
def search_profile(search: str,
                   display_type: str = Query(None, enum=[i for i in display_types.keys()]),
                   fields: Optional[str] = Depends(filter_fields),
                   limit: int = Query(10)):
    """
    - **search**: A String that starts the same as the first_name or last_name of the users (case insensitive)
    - **return**: A list of objects representing the user profiles, which will be composed of the fields
        specified in the "fields" parameter.
    If no users are found, an empty list is returned
    """
    filter_params = FilterParams(display_type, fields)
    fields = filter_params.validate(possible_fields, display_types)

    users = UserNode.search_profile(search, limit=limit, fields=fields)

    return users
