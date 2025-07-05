"""A file to hold all the fixtures for the pytests"""
import pytest
#the above allows the relative import to work
from app.app import create_app

@pytest.fixture(scope="module")
def test_client():
    app = create_app("config.config.TestConfig")
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

