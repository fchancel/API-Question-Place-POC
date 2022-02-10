import logging

import pytest
from fastapi.testclient import TestClient

from config import Settings, get_settings
from initial_data.generators.users_gen import random_email as _random_mail
from main import create_application

log = logging.getLogger("uvicorn")


def get_settings_override() -> Settings:
    """
    override the settings to get the database to be the testing db
    """
    test_settings = get_settings()
    test_settings.testing = True
    test_settings.neo4j_host = "db_test"
    return test_settings


@pytest.fixture(scope="module")
def test_app():
    """
        Start the application with overided settings for tests
        The retuned object is a FastAPI Testclient object.
    """
    settings = get_settings_override()
    app = create_application(settings)
    app.dependency_overrides[get_settings] = get_settings_override

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def random_email():
    return _random_mail()
