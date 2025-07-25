import pytest
import json
from flask.testing import FlaskClient   #for type hint
from pytest_mock import MockerFixture   #for type hints
from app.models import Node, LinkedList
from tests.helpers import generate_node, generate_question, build_test_ll, set_test_config
import app.routes.blueprints.q_crud as q_crud

@pytest.mark.parametrize("is_mult", [True, False])
def test_add_question_can_add_new_question_and_node_to_ll(test_client:FlaskClient, is_mult):
    _ = build_test_ll(test_client, [])

    form = {"q_str": "test", "q_detail": "test", "q_type": "singular"}
    if is_mult:
        form["a_type"] = "multiple-choice"
        form["options"] = json.dumps(["True", "False"])
    else:
        form["a_type"] = "open-ended"

    response = test_client.post("/add_question", data=form)
    assert response.status_code == 200
    result = response.get_json()["new_q_a_type"]
    if is_mult:
        assert result == "multiple-choice"
    else:
        assert result == "singular"

@pytest.mark.parametrize("is_mult", [True, False])
def test_add_question_addon_can_add_new_addon_question_to_existing_base_node(test_client:FlaskClient, is_mult):
    base_node:Node = generate_node(generate_question(q_type="base", q_detail="test base"))
    _ = build_test_ll(test_client, [base_node])

    form = {"q_str": "test addon", "q_detail": "test addon", "q_type": "singular", "addon_to": "test base"}
    if is_mult:
        form["a_type"] = "multiple-choice"
        form["options"] = json.dumps(["True", "False"])
    else:
        form["a_type"] = "open-ended"

    response = test_client.post("/add_question/addon", data=form)
    assert response.status_code == 200
    result = response.get_json()["new_q_a_type"]
    if is_mult:
        assert result == "multiple-choice"
    else:
        assert result == "singular"

def test_add_question_preset_cannot_add_nonexistent_preset_types(test_client:FlaskClient):
    _ = build_test_ll(test_client, [])
    wrong_value = "invalid"
    response = test_client.post("/add_question/preset", data=wrong_value)
    assert response.status_code == 409

@pytest.mark.parametrize("preset_type", ["appDate", "empty"])
def test_add_question_preset_can_add_valid_preset_types(test_client:FlaskClient, preset_type):
    _ = build_test_ll(test_client, [])
    response = test_client.post("/add_question/preset", data=preset_type)
    assert response.status_code == 200
    if preset_type == "appDate":
        assert response.text == f"Preset question: {preset_type} added"

def test_all_to_json_can_get_json_of_linked_list(test_client:FlaskClient):
    question_1 = generate_question("test name", "test detail", "singular", "open-ended")
    addon = generate_question("addon name", "addon detail", "add-on", "multiple-choice")
    addon.options = ["1", "2", "3"]
    question_2 = generate_question("test name 2", "test detail 2", "singular", "open-ended")
    node_1 = generate_node(question_1, addon)
    node_2 = generate_node(question_2)
    _ = build_test_ll(test_client, [node_1, node_2])
    
    expected = [
        {
            "question": {
                "q_str": "test name",
                "q_detail": "test detail",
                "q_type": "singular",
                "a_type": "open-ended"
            },
            "addon": {
                "q_str": "addon name",
                "q_detail": "addon detail",
                "q_type": "add-on",
                "a_type": "multiple-choice",
                "options": [
                    "1",
                    "2",
                    "3"
                ]
            }
        },
        {
            "question": {
                "q_str": "test name 2",
                "q_detail": "test detail 2",
                "q_type": "singular",
                "a_type": "open-ended"
            }
        }
    ]

    response = test_client.get("/get_ll_json")
    assert response.status_code == 200
    assert response.get_json() == expected

def test_check_if_questions_exists_returns_false_if_no_questions_exist(test_client:FlaskClient):
    ll_1 = build_test_ll(test_client, [])
    response = test_client.get("/check_if_questions_exists")
    assert response.status_code == 200
    assert response.text == "false"

    node = Node(None)
    ll_2 = build_test_ll(test_client, [node])
    response = test_client.get("/check_if_questions_exists")
    assert response.status_code == 200
    assert response.text == "false"

def test_check_if_questions_exists_returns_true_if_some_questions_exist(test_client:FlaskClient):
    node = generate_node(generate_question())
    _ = build_test_ll(test_client, [node])
    response = test_client.get("/check_if_questions_exists")
    assert response.status_code == 200
    assert response.text == "true"

def test_reorder_questions_cannot_reorder_nonexistent_q_details(test_client:FlaskClient):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    _ = build_test_ll(test_client, [node_1, node_2, node_3])

    wrong_order = {"order": ["2", "4", "1"]}

    response = test_client.post("/reorder_questions", json=wrong_order)
    assert response.status_code == 404

def test_reorder_questions_can_reorder_linked_list(test_client:FlaskClient, mocker:MockerFixture):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    _ = build_test_ll(test_client, [node_1, node_2, node_3])

    new_order = {"order": ["2", "1", "0"]}

    spy = mocker.spy(q_crud, "get_reordered_ll")
    
    response = test_client.post("/reorder_questions", json=new_order)
    assert response.status_code == 200

    expected = LinkedList()
    expected.append(node_3)
    expected.append(node_2)
    expected.append(node_1)
    assert spy.spy_return == expected

def test_delete_question_cannot_delete_nonexistent_addon(test_client:FlaskClient):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    _ = build_test_ll(test_client, [node_1, node_2, node_3])

    data = {"deleting_detail": "0", "is_addon": "true"}

    response = test_client.delete("/delete_question", json=data)
    assert response.status_code == 404 

def test_delete_question_cannot_delete_nonexistent_question(test_client:FlaskClient):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    _ = build_test_ll(test_client, [node_1, node_2, node_3])

    data = {"deleting_detail": "4", "is_addon": "false"}

    response = test_client.delete("/delete_question", json=data)
    assert response.status_code == 404 

def test_delete_question_can_delete_addon_question(test_client:FlaskClient):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    _ = build_test_ll(test_client, [node_1, node_2, node_3])

    data = {"deleting_detail": "+1", "is_addon": "true"}

    response = test_client.delete("/delete_question", json=data)
    assert response.status_code == 200
    assert response.text == f'Addon question "+1" deleted'

def test_delete_question_can_delete_question_node(test_client:FlaskClient):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    _ = build_test_ll(test_client, [node_1, node_2, node_3])

    data = {"deleting_detail": "0", "is_addon": "false"}

    response = test_client.delete("/delete_question", json=data)
    assert response.status_code == 200
    assert response.text == f'Node "0" deleted'
