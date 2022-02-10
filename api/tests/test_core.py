def test_ping(test_app):
    response = test_app.get("/api/dev/ping")

    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


def test_env(test_app):
    """
        Ensures that the test database is used, and the app is called in testing mode.
    """
    response = test_app.get("/api/dev/env")

    assert response.status_code == 200
    assert response.json() == {
        "environment": "dev",
        "testing": True,
        "neo4j_host": "db_test",
    }


def test_db(test_app):
    """
        Ensures that the test database respond.
    """
    response = test_app.get("/api/dev/db")

    assert response.status_code == 200
    assert response.json() == {"name": "test"}
