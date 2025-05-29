import pytest
import re
from ..src.model.question import Question, QuestionType, AnswerType, AnswerPart
from ..src.model.question_set import QuestionSet
from ..src.model.form_session import FormSession
from .functions import make_open_onepart_questions, make_question_set, make_form_session

def test_can_create_form_session_with_question_set():
    qset = make_question_set(2)
    session = FormSession(qset)
    assert session is not None

def test_must_create_form_session_with_question_set():
    with pytest.raises(TypeError, match=re.escape("FormSession.__init__() missing 1 required positional argument: 'question_set'")):
        session = FormSession()

class TestNavigation:
    def test_can_get_current_question(self):
        qset = make_question_set(3)
        session = FormSession(qset)
        assert session.current_question.id == 0

    def test_can_move_to_next_question(self):
        session = make_form_session(2)
        assert session.current_question.id == 0
        session.next_question()
        assert session.current_question.id == 1

    def test_can_move_to_previous_question(self):
        session = make_form_session(2)
        session.next_question()
        assert session.current_question.id == 1
        session.prev_question()
        assert session.current_question.id == 0

    def test_cannot_navigate_after_last_question(self):
        session = make_form_session(2)
        session.next_question()
        with pytest.raises(IndexError, match="There are no more next questions"):
            session.next_question()

    def test_cannot_navigate_before_first_question(self):
        session = make_form_session(2)
        with pytest.raises(IndexError, match="There are no previous questions"):
            session.prev_question()

    def test_can_check_if_current_question_is_first_question(self):
        session = make_form_session(2)
        assert session.on_first_question() == True

    def test_can_check_if_current_question_is_last_question(self):
        session = make_form_session(2)
        session.next_question()
        assert session.on_last_question() == True

class TestDisplayInfo:
    def test_can_get_current_question_prompt(self):
        session = make_form_session()
        prompt = session.get_prompt()
        assert prompt == "example_0"

    def test_can_get_current_question_type(self):
        session = make_form_session()
        q_type = session.get_question_type()
        assert q_type == "open-ended"

    def test_can_get_current_question_choices(self):
        q1 = Question(
            id=0,
            text="example_0",
            q_type=QuestionType("multiple-choice"),
            answ_type=AnswerType("one-part"),
            choices=["Choice 1", "Choice 2"]
        )
        q2 = make_open_onepart_questions(1)
        qset = QuestionSet([q1, q2])
        session = FormSession(qset)
        choices = session.get_choices()
        assert choices == ["Choice 1", "Choice 2"]
        session.next_question()
        choices2 = session.get_choices()
        assert choices2 == None

class TestAnswering:
    def test_can_record_answer_to_question(self):
        session = make_form_session(2)
        current_qid = session.current_question.id
        session.answer_question(id=current_qid, answer="answer_0")
        assert session.answers == {current_qid: "answer_0"}
    def test_can_get_answer_by_question(self):
        session = make_form_session(2)
        current_qid = session.current_question.id
        session.answer_question(id=current_qid, answer="answer_0")
        answer = session.get_answer(id=current_qid)
        assert answer == "answer_0"
    def test_can_change_answer(self):
        session = make_form_session()
        current_qid = session.current_question.id
        session.answer_question(id=current_qid, answer="answer_0")
        session.answer_question(current_qid, "answer_1")
        assert session.get_answer(0) == "answer_1"
    
    def test_can_confirm_only_when_all_questions_answered(self):
        session = make_form_session()
        assert session.can_confirm() == False
        current_qid = session.current_question.id
        session.answer_question(id=current_qid, answer="answer_0")
        assert session.can_confirm() == True
