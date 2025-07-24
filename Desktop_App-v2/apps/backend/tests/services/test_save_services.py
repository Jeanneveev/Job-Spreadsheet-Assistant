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

def test_get_preexisting_filenames_only_only_gets_valid_filenames(test_client:FlaskClient, tmp_path):
    test_upload_folder = tmp_path / "upload"
    valid_1 = test_upload_folder / "qg_valid.json"
    valid_2 = test_upload_folder / "qg_test_name.json"
    invalid_1 = test_upload_folder / "not_qg.json"
    invalid_2 = test_upload_folder / "wrong_filetype.csv"
    test_upload_folder.mkdir()
    valid_1.touch()
    valid_2.touch()
    invalid_1.touch()
    invalid_2.touch()
    config_params = {"UPLOAD_FOLDER": test_upload_folder}
    set_test_config(test_client, config_params)

    expected = ["test_name", "valid"]
    assert get_preexisting_filenames() == expected

def test_is_unique_filename_only_validates_new_filenames(test_client:FlaskClient, test_session):
    existing_filenames = ["1", "2", "3"]
    sess_var = {"filenames": existing_filenames}
    test_session(test_client, sess_var)

    test_client.get("/") #throwaway call to establish session

    assert is_unique_filename("1") == False
    assert is_unique_filename("4") == True

def test_write_ll_to_file_cannot_write_to_existing_filenames(test_client:FlaskClient, test_session):
    existing_filenames = ["1", "2", "3"]
    test_filename = "1"
    sess_var = {"filenames": existing_filenames}
    test_session(test_client, sess_var)

    test_client.get("/") #throwaway call to establish session

    with pytest.raises(ValueError, match="Name already exists"):
        ll = None # not accessed this test, just a placeholder
        write_ll_to_file(ll, test_filename)    

def test_write_ll_to_file_can_write_to_unique_filenames(test_client:FlaskClient, mocker:MockerFixture, test_session, tmp_path):
    # Make the linked list
    node_1:Node = generate_node(generate_question(q_detail="first"))
    node_2:Node = generate_node(generate_question(q_detail="second"))
    ll = build_test_ll(test_client, nodes=[node_1, node_2])
    
    # Make the temporary Saves folder
    test_save_dir = tmp_path / "Saves"
    test_save_dir.mkdir(parents=True)
    mocker.patch("app.services.save.os.path.join", return_value=str(test_save_dir / "qg_4.json"))

    # Set up session
    existing_filenames = ["1", "2", "3"]
    sess_var = {"filenames": existing_filenames}
    test_session(test_client, sess_var)
    test_client.get("/") #throwaway call to establish session

    test_filename = "4"
    expected_save_path = test_save_dir / "qg_4.json"
    assert write_ll_to_file(ll, test_filename) == f"Question group saved to {expected_save_path}"



    