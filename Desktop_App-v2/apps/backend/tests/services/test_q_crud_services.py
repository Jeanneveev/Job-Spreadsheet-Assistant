import pytest
from flask.testing import FlaskClient   #for type hint
from pytest_mock import MockerFixture   #for type hints
from tests.helpers import generate_node, generate_question, build_test_ll, set_test_config
from app.services.q_crud import *
import app.services.q_crud as q_crud

@pytest.mark.parametrize("is_q_type_2, is_mult", [
    (True, True), (True, False),
    (False, True), (False, False)
])
def test_get_question_from_form_can_create_different_types_of_questions(is_q_type_2, is_mult):
    form = {}
    if not is_q_type_2:
        form["q_type"] = "singular"
        q_type = QTypeOptions("singular")
    else:
        form["q_type_2"] = "base"
        q_type = QTypeOptions("base")
    if is_mult:
        form["a_type"] = "multiple-choice"
        a_type = ATypeOptions("multiple-choice")
        form["options"] = '["1", "2", "3", "4"]'
        options = ["1", "2", "3", "4"]
    else:
        form["a_type"] = "open-ended"
        a_type = ATypeOptions("open-ended")
        options = None
    
    q_str = "test"
    q_detail = "test detail"
    form["q_str"] = q_str
    form["q_detail"] = q_detail

    expected = Question(q_str, q_detail, q_type, a_type, options)
    assert get_question_from_form(form) == expected
    
    
def test_add_preset_cannot_add_invalid_preset_type(test_client:FlaskClient):
    node:Node = generate_node(generate_question())
    ll = build_test_ll(test_client, [node])

    name = "invalid"
    with pytest.raises(ValueError, match='Preset "invalid" not found'):
        add_preset(ll, name)

@pytest.mark.parametrize("preset_type", ["appDate", "empty"])
def test_add_preset_can_add_valid_preset_types(test_client:FlaskClient, test_session, mocker, preset_type):
    node:Node = generate_node(generate_question())
    ll = build_test_ll(test_client, [node])

    sess_var = {"empty_cntr": 0}
    test_session(test_client, sess_var)
    test_client.get("/")
    
    if preset_type == "appDate":
        expected = Question("appDate", "Application Date", QTypeOptions("singular"), ATypeOptions("preset"))
        spy = mocker.spy(q_crud, "add_application_date")
    else:
        expected = Question("empty", "Empty-0", QTypeOptions("singular"), ATypeOptions("preset"))
        spy = mocker.spy(q_crud, "add_empty_question")

    assert add_preset(ll, preset_type) == preset_type
    spy.assert_called_once()
    assert spy.spy_return == expected

def test_get_reordered_ll_cannot_order_nonexistent_nodes(test_client:FlaskClient):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    old_ll = build_test_ll(test_client, [node_1, node_2, node_3])

    wrong_order = ["2", "4", "1"]

    with pytest.raises(ValueError, match="Node not found"):
        get_reordered_ll(old_ll, wrong_order)

def test_get_reordered_ll_can_return_reordered_ll(test_client:FlaskClient):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    old_ll = build_test_ll(test_client, [node_1, node_2, node_3])

    new_order = ["2", "0", "1"]

    actual_ll = get_reordered_ll(old_ll, new_order)
    expected_ll = build_test_ll(test_client, [node_3, node_1, node_2])
    assert actual_ll == expected_ll

def test_delete_question_or_node_cannot_delete_nonexistent_addon(test_client:FlaskClient, mocker:MockerFixture):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    ll = build_test_ll(test_client, [node_1, node_2, node_3])

    q_detail_to_delete = "0"

    with pytest.raises(ValueError, match="Question not found"):
        delete_question_or_node(ll, q_detail_to_delete, True)

def test_delete_question_or_node_cannot_delete_nonexistent_question(test_client:FlaskClient, mocker:MockerFixture):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    ll = build_test_ll(test_client, [node_1, node_2, node_3])

    q_detail_to_delete = "4"

    with pytest.raises(ValueError, match="Question not found"):
        delete_question_or_node(ll, q_detail_to_delete, False)

def test_delete_question_or_node_can_delete_addon_questions(test_client:FlaskClient, mocker:MockerFixture):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    ll = build_test_ll(test_client, [node_1, node_2, node_3])

    q_detail_to_delete = "+1"

    spy = mocker.spy(ll, "getByAddonDetail")
    assert delete_question_or_node(ll, q_detail_to_delete, True) == f'Addon question "{q_detail_to_delete}" deleted'
    assert spy.spy_return == node_2

def test_delete_question_or_node_can_delete_node(test_client:FlaskClient, mocker:MockerFixture):
    node_1 = generate_node(generate_question(q_detail="0"))
    node_2 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_3 = generate_node(generate_question(q_detail="2"))
    ll = build_test_ll(test_client, [node_1, node_2, node_3])

    q_detail_to_delete = "2"

    spy = mocker.spy(ll, "getByDetail")
    assert delete_question_or_node(ll, q_detail_to_delete, False) == f'Node "{q_detail_to_delete}" deleted'
    assert spy.spy_return == node_3