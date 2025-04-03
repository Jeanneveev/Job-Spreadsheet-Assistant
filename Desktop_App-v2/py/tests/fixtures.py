"""A file to hold all the fixtures for the pytests"""
import os
import pytest
from routes.main import create_app

@pytest.fixture(scope="module")
def test_client():
    os.environ["CONFIG_TYPE"] = "config.config.TestConfig"
    flask_app = create_app("config.config.TestConfig")

    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            yield test_client