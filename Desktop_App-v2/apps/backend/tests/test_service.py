import pytest
from pytest_mock import MockerFixture
from app.models import QTypeOptions, ATypeOptions, Question, Node
from app.service.service import *

## HELPER FUNCTIONS
def generate_question(q_str="test", q_detail="test", q_type="singular", a_type="open-ended") -> Question:
    return Question(
        q_str = q_str,
        q_detail = q_detail,
        q_type = QTypeOptions("singular"),
        a_type = ATypeOptions("open-ended")
    )
def generate_node(add_addon:bool, question:Question=None) -> Node:
    if question:
        q = question
    else:
        q = generate_question()
    if add_addon:
        return Node(question=q, addon=generate_question())
    else:
        return Node(q)

## TESTS
@pytest.mark.parametrize("is_last, is_addon", [(True, True), (True, False), (False, True), (False, False)])
def test_get_current_question_display_info_returns_display_info(mocker:MockerFixture, is_last, is_addon):
    test_node:Node = generate_node(False)
    if is_addon:
        test_node.addon = generate_question(q_str="test-addon")
        test_question:Question = test_node.addon
    else:
        test_question:Question = test_node.question
    
    mocker.patch("app.service.service.is_last_question", return_value=is_last)
    if not is_last:
        test_node.next = generate_node(False)
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

def test_get_next_question_display_info_returns_display_info(mocker:MockerFixture):
    test_curr_node:Node = generate_node(False)
    test_next_node:Node = generate_node