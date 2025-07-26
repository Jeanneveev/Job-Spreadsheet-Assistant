import pytest
from datetime import date
from flask.testing import FlaskClient   #for type hint
from pytest_mock import MockerFixture   #for type hint
from app.models import Question, Node
from tests.helpers import generate_node, generate_question, build_test_ll
import app.services.answer_form as service
from app.services.answer_form import *

class TestGetNodesAndQuestions:
    def test_get_first_non_preset_node_returns_first_non_preset_node_or_none(self, test_client:FlaskClient):
        first_node:Node = generate_node(generate_question(a_type="preset"))
        second_node:Node = generate_node(generate_question(a_type="multiple-choice"))
        ll = build_test_ll(test_client, nodes=[first_node, second_node])

        assert get_first_non_preset_node(ll) == second_node
    def test_get_first_non_preset_node_returns_none_if_no_non_preset_nodes(self, test_client:FlaskClient):
        node:Node = generate_node(generate_question(a_type="preset"))
        ll = build_test_ll(test_client, nodes=[node])  # rebuild with only preset nodes
        assert get_first_non_preset_node(ll) == None

    @pytest.mark.parametrize("is_addon", [True, False])
    def test_get_question(self, is_addon):
        question:Question = generate_question(q_str="test question")
        q_dict = question.as_dict()
        if is_addon:
            node:Node = generate_node(addon=question)
        else:
            node:Node = generate_node(question=question)
        result = get_question_from_dictionary(node, q_dict)
        assert result == question

    def test_get_current_node_and_question(self, test_client:FlaskClient, test_session):
        first_q:Question = generate_question(q_detail="first")
        second_q:Question = generate_question(q_detail="second")
        first_node:Node = generate_node(question=first_q, addon=second_q)
        ll = build_test_ll(test_client, nodes=[first_node])

        # set up session variables
        sess_vars = {"curr_node": first_node.as_dict(), "curr_question": second_q.as_dict()}
        test_session(test_client, sess_vars)
    
        test_client.get("/")    # throwaway call to establish session
        assert get_current_node(ll) == first_node
        assert get_current_question(ll) == second_q
        assert get_current_question(ll, first_node) == second_q
        assert get_current_node_and_question(ll) == (first_node, second_q)
        
    def test_get_current_node_without_session_variables_returns_first_node_and_question(self, test_client:FlaskClient):
        first_q:Question = generate_question(q_detail="first")
        second_q:Question = generate_question(q_detail="second")
        first_node:Node = generate_node(question=first_q, addon=second_q)
        ll = build_test_ll(test_client, nodes=[first_node])

        test_client.get("/")    # throwaway call to establish session
        assert get_current_node(ll) == first_node
        assert get_current_question(ll, first_node) == first_q


class TestCheckQuestionOrder:
    def test_is_first_question(self, test_client:FlaskClient):
        first_q:Question = generate_question(q_detail="first")
        second_q:Question = generate_question(q_detail="second")
        first_node:Node = generate_node(first_q)
        second_node:Node = generate_node(second_q)
        _ = build_test_ll(test_client, nodes=[first_node, second_node])

        assert is_first_question(first_q) == True
        assert is_first_question(second_q) == False

    def test_is_last_question(self, test_client:FlaskClient):
        first_q:Question = generate_question(q_detail="first")
        last_q:Question = generate_question(q_detail="second")
        first_node:Node = generate_node(first_q)
        last_node:Node = generate_node(last_q)
        _ = build_test_ll(test_client, nodes=[first_node, last_node])

        assert is_last_question(last_q) == True
        assert is_last_question(first_q) == False

class TestGetDisplayInfo:
    @pytest.mark.parametrize("is_last, is_addon", [(True, True), (True, False), (False, True), (False, False)])
    def test_get_current_question_display_info(self, mocker:MockerFixture, is_last, is_addon):
        test_node:Node = generate_node()
        if is_addon:
            test_node.addon = generate_question(q_str="test-addon")
            test_question:Question = test_node.addon
        else:
            test_question:Question = test_node.question
        
        mocker.patch("app.services.answer_form.is_last_question", return_value=is_last)
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
    def test_get_next_question_display_info(self, mocker:MockerFixture, next_is_addon):
        if next_is_addon:
            curr_question:Question = generate_question("test curr question", q_detail="1")
            next_question:Question = generate_question("test next question", q_detail="2")
            curr_node:Node = generate_node(curr_question, next_question)
            next_next_question:Question = generate_question(a_type="multiple-choice", q_detail="3")
            next_node:Node = generate_node(next_next_question)
        else:
            curr_question:Question = generate_question("test curr question", q_detail="1")
            curr_node:Node = generate_node(curr_question)
            next_question:Question = generate_question("test next question", q_detail="2")
            next_next_question:Question = generate_question(a_type="multiple-choice", q_detail="3")
            next_node:Node = generate_node(next_question, next_next_question)
        curr_node.next = next_node

        # patch over session variables
        mock_session = {}
        mocker.patch("app.services.answer_form.session", mock_session)
        # patch over is_last_question to avoid having to init ll
        mocker.patch("app.services.answer_form.is_last_question", return_value=False)
        
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

    @pytest.mark.parametrize("prev_is_first, curr_is_addon, prev_is_addon", [(True, True, False), (False, True, False), (False, False, True), (True, False, False), (False, False, False)])
    def test_get_prev_question_display_info(self, mocker:MockerFixture, prev_is_first, curr_is_addon, prev_is_addon):
        expected = {}

        if curr_is_addon:
            curr_question:Question = generate_question("addon curr question", q_detail="1")
            prev_question:Question = generate_question("prev question", q_detail="2")
            curr_node:Node = generate_node(prev_question, curr_question)
        elif prev_is_addon:
            curr_question:Question = generate_question("addon curr question", q_detail="1")
            curr_node:Node = generate_node(curr_question)
            prev_question:Question = generate_question("prev question", q_detail="2")
            prev_node:Node = generate_node(generate_question(), prev_question)
            curr_node.prev = prev_node
            prev_node.next = curr_node
        else:
            curr_question:Question = generate_question("test curr question", a_type="multiple-choice", q_detail="1")
            curr_node:Node = generate_node(curr_question)
            prev_question:Question = generate_question("test previous question", q_detail="2")
            prev_node:Node = generate_node(prev_question)
            curr_node.prev = prev_node
            prev_node.next = curr_node

        # patch over session variables
        mock_session = {}
        mocker.patch("app.services.answer_form.session", mock_session)
        # patch over is_first_question and is_last_question to avoid having to init ll
        mocker.patch("app.services.answer_form.is_first_question", return_value=prev_is_first)
        mocker.patch("app.services.answer_form.is_last_question", return_value=False)
        

        spy = mocker.spy(service, "get_current_question_display_info")

        expected = {
            "q_str": prev_question.q_str,
            "curr_question_a_type": prev_question.a_type.value,
            "next_question_a_type": curr_question.a_type.value,
            "is_first": str(prev_is_first).lower(),
            "is_addon": str(prev_is_addon).lower()
        }
        assert get_prev_question_display_info(curr_node, curr_question) == expected
        if curr_is_addon:
            spy.assert_called_once_with(curr_node, prev_question)
        else:
            spy.assert_called_once_with(prev_node, prev_question)


class TestAnswerQuestion:
    def test_append_addon_answer(self, mocker:MockerFixture):
        curr_node:Node = generate_node(generate_question())
        # patch over get_current_node
        mocker.patch("app.services.answer_form.get_current_node", return_value=curr_node)
        curr_node.answer = "test base answ"

        assert append_addon_answer(" (addon)", curr_node) == "test base answ (addon)"

    @pytest.mark.parametrize("p_type", ["appDate", "empty"])
    def test_answer_preset_node_answers_known_preset_types(self, p_type):
        node:Node = generate_node(generate_question())
        if p_type == "appDate":
            expected = date.today().strftime("%m/%d/%Y")
        elif p_type == "empty":
            expected = " "
        
        assert answer_preset_node(node, p_type) == expected
        assert node.answer == expected
    def test_answer_preset_node_raises_error_at_unknown_preset_types(self):
        node:Node = generate_node(generate_question())
        wrong_p_type = "smth"
        with pytest.raises(ValueError, match=f"Unidentified preset type {wrong_p_type}"):
            answer_preset_node(node, wrong_p_type)

    def test_get_all_answers_returns_all_answers_in_linked_list(self, test_client:FlaskClient):
        first_q:Question = generate_question(q_detail="first")
        second_q:Question = generate_question(q_detail="second")
        first_node:Node = generate_node(first_q)
        second_node:Node = generate_node(second_q)
        first_node.answer = "answer 1"
        second_node.answer = "answer 2"
        ll = build_test_ll(test_client, nodes=[first_node, second_node])

        assert get_all_answers(ll) == ["answer 1", "answer 2"]