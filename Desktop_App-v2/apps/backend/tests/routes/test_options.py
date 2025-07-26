import pytest
from flask.testing import FlaskClient   #for type hint
from pytest_mock import MockerFixture   #for type hints
from app.models import LinkedList, Node, Question
from tests.helpers import generate_node, generate_question, build_test_ll
import app.routes.blueprints.options as options

def test_set_curr_options_adds_only_unique_new_options_to_current_question(test_client:FlaskClient, mocker:MockerFixture, test_session):
    options_to_add = ["1", "2", "4"]
    existing_options = ["1", "3"]
    expected = ["1", "3", "2", "4"]
    sess_var = {"curr_options": existing_options}
    test_session(test_client, sess_var)
    
    # curr_question:Question = generate_question()
    # curr_question.options = existing_options
    # # build linked list so that get_current_question can work
    # curr_node:Node = generate_node(curr_question)
    # build_test_ll(test_client, [curr_node])
    # get_curr_options_spy = mocker.spy(options, "add_options_to_question")

    response = test_client.post("/set_curr_options", json={"options": options_to_add})
    assert response.status_code == 200
    # get_curr_options_spy.assert_called_once_with(options_to_add, curr_question)
    # assert get_curr_options_spy.spy_return == expected

def test_add_options_adds_only_unique_new_options_to_all_opt_lst(test_client:FlaskClient, mocker:MockerFixture, test_session):
    new_options = ["1", "3", "5"]
    existing_options = ["2", "3", "4"]
    expected = ["2", "3", "4", "1", "5"]

    sess_var = {"all_options": existing_options}
    test_session(test_client, sess_var)

    all_options_spy = mocker.spy(options, "add_new_options_to_all_options")

    response = test_client.post("/add_options", json={"options": new_options})
    assert response.status_code == 200
    all_options_spy.assert_called_once_with(new_options)
    assert all_options_spy.spy_return == expected

def test_get_all_options_returns_all_options_json(test_client:FlaskClient, test_session):
    all_options = ["1", "2", "3", "4"]
    sess_var = {"all_options": all_options}
    test_session(test_client, sess_var)

    response = test_client.get("/get_all_options")
    assert response.status_code == 200
    result = response.get_json()
    assert result["all_options"] == all_options

def test_get_current_options_returns_curr_options_json(test_client:FlaskClient, test_session):
    curr_options = ["1", "2", "3", "4"]
    sess_var = {"curr_options": curr_options}
    test_session(test_client, sess_var)

    response = test_client.get("/get_current_options")
    assert response.status_code == 200
    result = response.get_json()
    assert result["curr_options"] == curr_options

def clear_current_options_clears_current_options_session_variable(test_client:FlaskClient, test_session):
    curr_options = ["1", "2", "3", "4"]
    expected = []
    sess_var = {"curr_options": curr_options}
    test_session(test_client, sess_var)

    response = test_client.delete("/clear_current_options")
    assert response.status_code == 200
    result = response.get_json()
    assert result["curr_options"] == expected