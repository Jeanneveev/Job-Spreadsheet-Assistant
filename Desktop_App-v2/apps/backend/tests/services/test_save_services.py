import pytest
from flask.testing import FlaskClient   #for type hint
from pytest_mock import MockerFixture   #for type hint
from app.models import Question, Node
from tests.helpers import generate_node, generate_question, build_test_ll, set_test_config
from app.services.save import *

def test_get_root_filename_returns_root_filename():
    filename = "qg_valid.json"
    assert get_root_filename(filename) == "valid"

def test_get_full_filename_returns_full_filename():
    root = "root"
    assert get_full_filename(root) == "qg_root.json"

def test_get_preexisting_filenames_only_only_gets_valid_filenames(test_client:FlaskClient, test_upload_folder):
    config_params = {"UPLOAD_FOLDER": test_upload_folder}
    set_test_config(test_client, config_params)

    expected = ["valid", "wrong_format"]
    assert get_preexisting_filenames() == expected

def test_is_unique_filename_only_validates_new_filenames(test_client:FlaskClient, test_session):
    existing_filenames = ["1", "2", "3"]
    sess_var = {"filenames": existing_filenames}
    test_session(test_client, sess_var)

    test_client.get("/") #throwaway call to establish session

    assert is_unique_filename("1") == False
    assert is_unique_filename("4") == True

def test_write_ll_to_file_cannot_write_to_existing_filenames():
    ...

def test_write_ll_to_file_can_write_to_unique_filenames():
    ...