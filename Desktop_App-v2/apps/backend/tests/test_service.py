import pytest
from pytest_mock import MockerFixture
from app.models import Question, Node
from tests.helpers import generate_node, generate_question, build_test_ll
import app.service.service as service
from app.service.service import *

## TESTS
@pytest.mark.parametrize("is_last, is_addon", [(True, True), (True, False), (False, True), (False, False)])
def test_get_current_question_display_info_returns_display_info(mocker:MockerFixture, is_last, is_addon):
    test_node:Node = generate_node()
    if is_addon:
        test_node.addon = generate_question(q_str="test-addon")
        test_question:Question = test_node.addon
    else:
        test_question:Question = test_node.question
    
    mocker.patch("app.service.service.is_last_question", return_value=is_last)
    if not is_last:
        test_node.next = generate_node()
        if is_addon:
            assert get_current_question_display_info(test_node, test_question) == {
                "q_str": "test-addon",
                "next_question_a_type": "open-ended",
                "is_last": "false",
                "is_addon": "true"
            }
        else:
            assert get_current_question_display_info(test_node, test_question) == {
                "q_str": "test",
                "next_question_a_type": "open-ended",
                "is_last": "false",
                "is_addon": "false"
            }
    else:
        if is_addon:
            assert get_current_question_display_info(test_node, test_question) == {
                "q_str": "test-addon",
                "is_last": "true",
                "is_addon": "true"
            }
        else:
            assert get_current_question_display_info(test_node, test_question) == {
                "q_str": "test",
                "is_last": "true",
                "is_addon": "false"
            }

@pytest.mark.parametrize("next_is_addon", [True, False])
def test_get_next_question_display_info_returns_display_info(mocker:MockerFixture, next_is_addon):
    if next_is_addon:
        curr_question:Question = generate_question("test curr question")
        next_question:Question = generate_question("test next question")
        curr_node:Node = generate_node(curr_question, next_question)
        next_next_question:Question = generate_question(a_type="multiple-choice")
        next_node:Node = generate_node(next_next_question)
    else:
        curr_question:Question = generate_question("test curr question")
        curr_node:Node = generate_node(curr_question)
        next_question:Question = generate_question("test next question")
        next_next_question:Question = generate_question(a_type="multiple-choice")
        next_node:Node = generate_node(next_question, next_next_question)
    curr_node.next = next_node

    # patch over session variables
    mock_session = {}
    mocker.patch("app.service.service.session", mock_session)
    # patch over is_last_question to avoid having to init ll
    mocker.patch("app.service.service.is_last_question", return_value=False)
    
    spy = mocker.spy(service, "get_current_question_display_info")

    expected = {
        "q_str": "test next question",
        "next_question_a_type": "multiple-choice",
        "is_last": "false",
        "is_addon": str(next_is_addon).lower()
    }
    assert get_next_question_display_info(curr_node, curr_question) == expected
    if next_is_addon:
        spy.assert_called_once_with(curr_node, next_question)
    else:
        spy.assert_called_once_with(next_node, next_question)

@pytest.mark.parametrize("curr_is_addon, prev_is_addon", [(True, False), (False, True), (False, False)])
def test_get_prev_question_display_info_returns_display_info(mocker:MockerFixture, curr_is_addon, prev_is_addon):
    expected = {}

    if curr_is_addon:
        curr_question:Question = generate_question("addon curr question")
        prev_question:Question = generate_question("prev question")
        curr_node:Node = generate_node(prev_question, curr_question)
    elif prev_is_addon:
        curr_question:Question = generate_question("addon curr question")
        curr_node:Node = generate_node(curr_question)
        prev_question:Question = generate_question("prev question")
        prev_node:Node = generate_node(generate_question(), prev_question)
        curr_node.prev = prev_node
        prev_node.next = curr_node
    else:
        curr_question:Question = generate_question("test curr question", a_type="multiple-choice")
        curr_node:Node = generate_node(curr_question)
        prev_question:Question = generate_question("test previous question")
        prev_node:Node = generate_node(prev_question)
        curr_node.prev = prev_node
        prev_node.next = curr_node

    # patch over session variables
    mock_session = {}
    mocker.patch("app.service.service.session", mock_session)
    # patch over is_last_question to avoid having to init ll
    mocker.patch("app.service.service.is_last_question", return_value=False)

    spy = mocker.spy(service, "get_current_question_display_info")

    expected = {
        "q_str": prev_question.q_str,
        "next_question_a_type": curr_question.a_type.value,
        "is_addon": str(prev_is_addon).lower()
    }
    assert get_prev_question_display_info(curr_node, curr_question) == expected
    if curr_is_addon:
        spy.assert_called_once_with(curr_node, prev_question)
    else:
        spy.assert_called_once_with(prev_node, prev_question)


