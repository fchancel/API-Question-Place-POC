import logging

from config import Settings, get_settings
from fastapi import FastAPI
from neomodel import clear_neo4j_database, config, db

log = logging.getLogger('uvicorn')


def create_start_app_handler(app: FastAPI, settings: Settings):
    async def start_app() -> None:
        log.info("Event handler: start application")

        config.DATABASE_URL = get_settings().neo4j_url()

    return start_app


def create_stop_app_handler(app: FastAPI, settings: Settings):
    async def stop_app() -> None:
        log.info("Event handler: stop application")

        if settings.testing:
            log.info("Delete database")
            clear_neo4j_database(db)

        get_settings.cache_clear()

    return stop_app
