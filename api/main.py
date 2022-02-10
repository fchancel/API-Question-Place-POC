import logging
from os import getenv

from click import style
from fastapi import FastAPI

from config import Settings, get_settings
from core.debugger import initialize_server_debugger
from core.events import create_start_app_handler, create_stop_app_handler
from core.routes.core_routes import router as tests_routes
from feedbacks.routes.feedback_routes import router as feedback_routes
from questions.routes.answer_routes import router as answer_routes
from questions.routes.comment_routes import router as comment_routes
from questions.routes.question_routes import router as question_routes
from users.routes.user_routes import router as user_routes

log = logging.getLogger("uvicorn")


if getenv("DEBUGGER") == "True":
    initialize_server_debugger()


def create_application(settings: Settings) -> FastAPI:
    # Logging
    log.info(
        f"Loading settings from the environment... "
        f"[{ style(settings.environment, fg='cyan') }] ")

    log.info(
        f"Loading database settings ... "
        f"[ { style(settings.neo4j_user, fg='cyan') }] on "
        f"[{ style(settings.neo4j_url(), fg='cyan') }] ")
    # ...

    # FastAPI application
    log.info("Creating application ...")
    api = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        docs_url=settings.documentation_url,
        debug=settings.environment == "dev"
    )

    # Routes
    log.info("  ... add routes ...")
    api.include_router(user_routes, prefix="/api")
    api.include_router(feedback_routes, prefix="/api")
    api.include_router(question_routes, prefix="/api")
    api.include_router(answer_routes, prefix="/api")
    api.include_router(comment_routes, prefix="/api")
    if settings.is_dev():
        # these routes are only for testing, they will not be present in prod
        api.include_router(tests_routes, prefix="/api")

    # Event handlers registration
    log.info("  ... add events handlers ...")
    api.add_event_handler("startup", create_start_app_handler(api, settings))
    api.add_event_handler("shutdown", create_stop_app_handler(api, settings))

    # api.add_exception_handler(RequestValidationError, validation_exception_handler)

    return api


api = create_application(get_settings())


# if __name__ == "__main__":
#     uvicorn.run(api, host="0.0.0.0", port=8000, reload=True)
