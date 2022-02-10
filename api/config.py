import logging
import os.path
from functools import lru_cache

from click import style
from fastapi_mail import ConnectionConfig
from pydantic import BaseSettings, validator

log = logging.getLogger('uvicorn')


class Settings(BaseSettings):

    # ENVIRONMENT
    environment: str = 'dev'
    testing: bool = False
    base_dir = os.path.dirname(os.path.abspath(__file__))

    def is_dev(self):
        return self.environment == 'dev'

    @validator('environment')
    def environment_validation(cls, v):
        if v not in ["dev", "prod"]:
            raise ValueError(
                f'Environment invalid: should be "dev" or "prod", found {style(v, fg="red")}')
        return v

    # FASTAPI
    app_title: str = "Super API"
    app_description: str = "A super API !"
    documentation_url: str = "/docs"

    # EMAIL
    mail_conf = ConnectionConfig(
        MAIL_USERNAME="",
        MAIL_PASSWORD="",
        MAIL_FROM="no-reply@project.com",
        MAIL_PORT=0,
        MAIL_SERVER="",
        MAIL_TLS=True,
        MAIL_SSL=False,
        USE_CREDENTIALS=True
    )

    # TOKEN
    secret_key: str = ''
    algorithm_hash: str = ''
    access_token_expire_minutes_mail: int = 60 * 24
    access_token_expire_minutes_login: int = 60

    # NEO4J
    neo4j_user: str = ''
    neo4j_password: str = ''
    neo4j_scheme: str = ''
    neo4j_port: str = ''
    neo4j_host: str = ''

    def neo4j_url(self):
        return f"{self.neo4j_scheme}://{self.neo4j_user}:{self.neo4j_password}@{self.neo4j_host}:{self.neo4j_port}"


@ lru_cache()
def get_settings() -> Settings:
    settings = None
    try:
        settings = Settings()
    except ValueError as err:
        log.critical(err)
        exit(0)

    return settings
