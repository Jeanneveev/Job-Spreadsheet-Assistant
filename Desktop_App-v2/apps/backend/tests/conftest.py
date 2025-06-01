"""A file to hold all the fixtures for the pytests"""
import os
import sys
import pytest
from flask.testing import FlaskClient   #for type hint

#add the parent directory, "backend" to sys.path to allow for imports from backend/
basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
#the above allows the relative import to work
from routes.app import create_app

@pytest.fixture(scope="module")
def test_client():
    os.environ["CONFIG_TYPE"] = "config.config.TestConfig"
    flask_app = create_app("config.config.TestConfig")

    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            yield test_client