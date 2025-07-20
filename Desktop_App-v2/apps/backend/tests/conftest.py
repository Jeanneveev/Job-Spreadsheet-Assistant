"""A file to hold all the fixtures for the pytests"""
import pytest
from pathlib import Path
#the above allows the relative import to work
from app.app import create_app

@pytest.fixture(scope="module")
def test_client():
    app = create_app("config.config.TestConfig")
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

@pytest.fixture
def test_session(test_client):
    def setter(test_client, sess_vars:dict):
        with test_client.session_transaction() as sess:
            sess.update(sess_vars)

    yield setter    # let test run with the ability to use the setter function via test_session

    # after test is done, clear the session
    with test_client.session_transaction() as sess:
        sess.clear()

@pytest.fixture()
def test_upload_folder():
    print(f"save folder is {Path(__file__).parent / 'upload'}")
    return str(Path(__file__).parent / "upload")