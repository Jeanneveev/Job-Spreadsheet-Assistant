import pytest
from ..src.model.question import Question, QuestionType, AnswerType, AnswerPart
from ..src.model.question_set import QuestionSet

def make_open_onepart_questions(count:int):
    if count == 1:
        return Question(0, f"example_0", QuestionType("open-ended"), AnswerType("one-part"))
    return [Question(x, f"example_{x}", QuestionType("open-ended"), AnswerType("one-part"))
            for x in range(count)]
def make_open_twopart_questions(count:int):
    if count == 1:
        return Question(0, f"example_0", QuestionType("open-ended"), AnswerType("two-part"))
    return [Question(x, f"example_{x}", QuestionType("open-ended"), AnswerType("two-part"))
            for x in range(count)]


class TestCRUD:
    def test_can_create_question_set_with_one_questions(self):
        q1 = make_open_onepart_questions(1)
        qset = QuestionSet([q1])
        assert qset.questions[0].text == "example_0"

    def test_can_create_question_set_with_multiple_questions(self):
        q1, q2 = make_open_onepart_questions(2)
        qset = QuestionSet([q1, q2])
        assert qset.questions[0].text == "example_0"

    def test_can_create_question_set_with_no_questions(self):
        qset = QuestionSet()
        assert qset is not None
        
    def test_can_add_questions_to_existing_question_set(self):
        q1, q2, q3 = make_open_onepart_questions(3)
        qset = QuestionSet()
        qset.append([q1, q2])
        assert qset.questions[1].text == "example_1"
        qset.append(q3)
        assert qset.questions[2].text == "example_2"

    def test_adding_questions_is_idempotent(self):
        q1 = make_open_onepart_questions(1)
        q1_copy = make_open_onepart_questions(1)
        qset = QuestionSet()
        qset.append(q1)
        qset.append(q1_copy)
        assert len(qset.questions) == 1

    def test_get_question_by_id(self):
        q1, q2 = make_open_onepart_questions(2)
        qset = QuestionSet([q1, q2])
        first_q:Question = qset.get_question_by_id(0)
        assert first_q.text == "example_0"

    def test_can_get_questions_by_required_attribute(self):
        q1, q2 = make_open_onepart_questions(2)
        q3 = Question(
            id=3,
            text="example_3",
            q_type=QuestionType("open-ended"),
            answ_type=AnswerType("two-part"),
            answ_part=AnswerPart("base")
        )
        q4 = Question(
            id=4,
            text="example_4",
            q_type=QuestionType("open-ended"),
            answ_type=AnswerType("one-part")
        )
        qset = QuestionSet([q1, q2, q3, q4])
        results:list[Question] = qset.get_questions_by("answ_type", "one-part")
        assert results[2].id == 4

    def test_can_get_questions_by_optional_attribute(self):
        q1 = make_open_onepart_questions(1)
        q2 = Question(
            id=2,
            text="example_2",
            q_type=QuestionType("open-ended"),
            answ_type=AnswerType("two-part"),
            answ_part=AnswerPart("base")
        )
        q3 = Question(
            id=3,
            text="example_3",
            q_type=QuestionType("open-ended"),
            answ_type=AnswerType("two-part"),
            answ_part=AnswerPart("base")
        )
        q4 = Question(
            id=4,
            text="example_4",
            q_type=QuestionType("open-ended"),
            answ_type=AnswerType("one-part")
        )
        qset = QuestionSet([q1, q2, q3, q4])
        results:list[Question] = qset.get_questions_by("answ_part", "base")
        assert results[1].id == 3

    def test_can_only_delete_existing_question(self):
        q1, q2, q3 = make_open_onepart_questions(3)
        qset = QuestionSet([q1, q2, q3])
        assert qset.questions[1].id == 1
        qset.delete(id=1)
        assert qset.questions[1].id == 2
        with pytest.raises(ValueError, match=f'No question found with id 1'):
            qset.delete(id=1)


def test_addon_questions_must_reference_existing_base_question():
    base_q = Question(
        id=0,
        text="base_q",
        q_type=QuestionType("open-ended"),
        answ_type=AnswerType("two-part"),
        answ_part=AnswerPart("base")
    )
    addon_q = Question(
        id=1,
        text="Yes or no:",
        q_type=QuestionType("multiple-choice"),
        answ_type=AnswerType("two-part"),
        answ_part=AnswerPart("addon"),
        choices=["Yes", "No"],
        base_id=999
    )
    with pytest.raises(ValueError, match=f"Addon question 1: refers to nonexistent base_id"):
        QuestionSet([base_q, addon_q])

