import pytest
from flask.testing import FlaskClient   #for type hint
from pytest_mock import MockerFixture   #for type hint
from app.models import Node, LinkedList
from tests.helpers import generate_node, generate_question, build_test_ll

def test_save_file_cannot_save_to_given_existing_filename(test_client:FlaskClient, test_session):
    existing_filenames = ["1", "2", "3"]
    sess_var = {"filenames": existing_filenames}
    test_session(test_client, sess_var)

    response = test_client.post("/save_file", data="1")
    assert response.status_code == 409

def test_save_file_can_save_to_given_unique_filename(test_client:FlaskClient, mocker:MockerFixture, test_session, tmp_path):
    # Make the linked list
    node_1:Node = generate_node(generate_question(q_detail="first"))
    node_2:Node = generate_node(generate_question(q_detail="second"))
    _ = build_test_ll(test_client, nodes=[node_1, node_2])
    
    # Make the temporary Saves folder
    test_save_dir = tmp_path / "Saves"
    test_save_dir.mkdir(parents=True)
    mocker.patch("app.services.save.os.path.join", return_value=str(test_save_dir / "qg_4.json"))

    # Set up session
    existing_filenames = ["1", "2", "3"]
    sess_var = {"filenames": existing_filenames}
    test_session(test_client, sess_var)

    expected_save_path = test_save_dir / "qg_4.json"
    response = test_client.post("/save_file", data="4")
    response.status_code == 200
    result = response.text
    assert result == f"Question group saved to {expected_save_path}"