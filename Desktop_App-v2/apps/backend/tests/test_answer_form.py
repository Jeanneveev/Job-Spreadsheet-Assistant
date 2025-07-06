import pytest
from flask.testing import FlaskClient   #for type hint
from pytest_mock import MockerFixture   #for type hints
from app.models import LinkedList
from tests.helpers import generate_node, generate_question, build_test_ll
import app.routes.blueprints.answer_form as answer_form

@pytest.mark.parametrize("is_last", [True, False])  #ensure that it works both if and if not first question == last question
def test_get_first_question_display_info_returns_question_display_info(test_client:FlaskClient, mocker:MockerFixture, is_last):
    # add test question(s) and node(s) to test ll
    first_question = generate_question(q_str="Enter job name")
    first_node = generate_node(first_question)
    nodes = [first_node]
    if not is_last:
        next_question = generate_question(q_detail="next", a_type="multiple-choice")
        next_node = generate_node(next_question)
        nodes.append(next_node)
    
    build_test_ll(test_client, nodes)

    mocker.patch("app.routes.blueprints.answer_form.get_first_non_preset_node", return_value=first_node)
    mocker.patch("app.routes.blueprints.answer_form.answer_leading_presets")

    spy = mocker.spy(answer_form, "get_current_question_display_info")

    response = test_client.get("/get_first_question")
    assert response.status_code == 200

    result = response.get_json()
    if is_last:
        expected = {
            "q_str": "Enter job name",
            "is_last": str(is_last).lower()
        }
    else:
        expected = {
            "q_str": "Enter job name",
            "next_question_a_type": "multiple-choice",
            "is_last": str(is_last).lower()
        }
    assert result == expected
    spy.assert_called_once_with(first_node, first_question)
    

# def test_get_first_a_type_returns_a_type_value(test_client: FlaskClient, mocker:MockerFixture):
#     mock_head = mocker.Mock()
#     mock_head.question.a_type.value = "multiple-choice"

#     mocker.patch("app.routes.blueprints.answer_form.get_first_non_preset_node", return_value=mock_head)
#     response = test_client.get("/get_first_a_type")
#     assert response.status_code == 200
#     result = response.text
#     assert result == "multiple-choice"
# def test_get_first_a_type_returns_202_if_none(test_client: FlaskClient, mocker:MockerFixture):
#     mocker.patch("app.routes.blueprints.answer_form.get_first_non_preset_node", return_value=None)
#     response = test_client.get("/get_first_a_type")
#     assert response.status_code == 202
#     result = response.text
#     assert result == "Please add at least one non-preset question"

# @pytest.mark.parametrize("if_is_last, if_is_addon", [(True, True), (True, False), (False, True), (False, False)])
# def test_get_next_question_display_info_returns_question_display_info(test_client: FlaskClient, mocker:MockerFixture, if_is_last, if_is_addon):
#     mock_ll = mocker.Mock()
#     mock_node = mocker.Mock()
#     mock_ll.getByDetail.return_value = mock_node
#     mocker.patch("app.routes.blueprints.answer_form.get_ll", return_value=mock_ll)

#     # set up session variables
#     with test_client.session_transaction() as session:
#         session["curr_node"] = {
#             "question": {
#                 "q_str": "mock question 1",
#                 "q_detail": "mock q_detail value 1",
#                 "a_type": "multiple-choice"
#             }
#         }
#         session["curr_question"] = {
#             "q_str": "mock question 1",
#             "q_detail": "mock q_detail value 1",
#             "a_type": "multiple-choice"
#         }

#     mock_next_node = mocker.Mock()
#     mock_next_question = mocker.Mock()
#     mock_next_node.as_dict.return_value = {
#         "q_str": "mock question 2",
#         "q_detail": "mock q_detail value 2",
#         "a_type": "multiple-choice"
#     }
#     mock_next_node.display_info.return_value = {
#         "q_str": "mock question 2",
#         "next_question_a_type": "multiple_choice",
#         "is_last": str(if_is_last).lower()
#     }
#     mock_next_question.as_dict.return_value = {
#         "question": {
#             "q_str": "mock question 2",
#             "q_detail": "mock q_detail value 2",
#             "a_type": "multiple-choice"
#         }
#     }
#     mocker.patch("app.routes.blueprints.answer_form.get_next_node_and_question",
#         return_value=(mock_next_node, mock_next_question, if_is_addon)
#     )

#     mocker.patch("app.routes.blueprints.answer_form.is_last_question", return_value=if_is_last)
    
#     response = test_client.get("/get_next_question")
#     assert response.status_code == 200
#     result = response.get_json()
#     assert result == {
#         "q_str": "mock question 2",
#         "next_question_a_type": "multiple_choice",
#         "is_last": str(if_is_last).lower(), "is_addon": str(if_is_addon).lower()
#     }
    
# def test_get_prev_question_display_info_returns_question_display_info(test_client: FlaskClient, mocker:MockerFixture):
#     ...