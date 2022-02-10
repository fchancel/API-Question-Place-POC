import logging

from config import get_settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from users.nodes.user_node import UserNode
from users.schema.token_schema import TokenData

log = logging.getLogger("uvicorn")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token", auto_error=False)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class GetCurrentUser:

    def decode(self, token: str):
        try:
            settings = get_settings()
            payload = jwt.decode(token, settings.secret_key,
                                 algorithms=[settings.algorithm_hash])
            email = payload.get("email")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except jwt.JWTError as e:
            log.info(f"credentials_exception raised: JwtError: {e}")
            raise credentials_exception
        user = UserNode.get_node_with_email(token_data.email)
        if user is None:
            raise credentials_exception
        return user

    def __init__(self, active=True, auto_error=True):
        self.active = active
        self.auto_error = auto_error

    def __call__(self, token: str = Depends(oauth2_scheme)) -> UserNode:
        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        user: UserNode = self.decode(token)
        if self.active and not user.is_active:
            if self.auto_error:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="inactive user")
            else:
                return None
        if self.active and not user.email_verified:
            if self.auto_error:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email not verified")
            else:
                return None
        return user


def get_target_user(username: str) -> UserNode:
    user = UserNode.get_node_with_username(username)
    if not user or not user.email_verified or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user
