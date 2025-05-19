import pytest
from ..src.model.question import Question, QuestionType, AnswerType, AnswerPart

def test_question_can_return_its_prompt():
    q = Question(
        id=0,
        text="What is the job title?",
        q_type=QuestionType("open-ended"),
        answ_type=AnswerType("one-part"),
        answ_part=None,
        choices=None,
        base_id=None
    )
    assert q.text == "What is the job title?"

class TestValidAttributeTyping:
    def test_q_type_must_be_of_type_question_type(self):
        q_id=0
        wrong_q_type="smth"
        with pytest.raises(TypeError, match=f'Question {q_id}: invalid q_type: "{wrong_q_type}"'):
            invalid_q_type_q = Question(
                id=q_id,
                text="Select job type:",
                q_type=wrong_q_type,
                answ_type="one-part",
            )
    def test_answ_type_must_be_of_type_answer_type(self):
        q_id=0
        wrong_answ_type=12
        with pytest.raises(TypeError, match=f'Question {q_id}: invalid answ_type: "{wrong_answ_type}"'):
            invalid_answ_type_q = Question(
                id=q_id,
                text="What is the job title?",
                q_type=QuestionType("open-ended"),
                answ_type=wrong_answ_type,
            )
    def test_answ_part_must_be_of_type_answer_part(self):
        q_id=0
        wrong_answ_part=AnswerType("one-part")
        with pytest.raises(TypeError, match=f'Question {q_id}: invalid answ_part: "{wrong_answ_part}"'):
            invalid_answ_part_q = Question(
                id=q_id,
                text="What is the job title?",
                q_type=QuestionType("open-ended"),
                answ_type=AnswerType("one-part"),
                answ_part=wrong_answ_part
            )

class TestAttributeCombinations:
    def test_multiple_choice_question_must_include_choices(self):
        q_id=0
        with pytest.raises(ValueError, match=f"Question {q_id}: multiple-choice questions must include choices."):
            mult_q = Question(
                id=q_id,
                text="Select job type:",
                q_type=QuestionType("multiple-choice"),
                answ_type=AnswerType("one-part"),
                choices=None
            )
    def test_non_multiple_choice_question_cannot_have_choices(self):
        q_id=0
        with pytest.raises(ValueError, match=f"Question {q_id}: only multiple-choice questions can have choices."):
            non_mult_q = Question(
                id=q_id,
                text="Select job type:",
                q_type=QuestionType("open-ended"),
                answ_type=AnswerType("one-part"),
                choices=["Choice 1", "Choice 2"]
            )
    def test_two_part_questions_must_have_answ_type(self):
        q_id=0
        with pytest.raises(ValueError, match=f"Question {q_id}: two-part questions must have a valid answ_part."):
            two_part_q = Question(
                id=q_id,
                text="Select job type:",
                q_type=QuestionType("open-ended"),
                answ_type=AnswerType("two-part"),
                answ_part=None
            )
        two_part_q_2 = Question(
            id=1,
            text="Select job type:",
            q_type=QuestionType("open-ended"),
            answ_type=AnswerType("two-part"),
            answ_part=AnswerPart("base")
        )
        assert two_part_q_2.answ_part == AnswerPart("base")
    def test_one_part_questions_cannot_have_answ_type(self):
        q_id=0
        with pytest.raises(ValueError, match=f"Question {q_id}: one-part questions must not have answ_part."):
            one_part_q = Question(
                id=q_id,
                text="Select job type:",
                q_type=QuestionType("open-ended"),
                answ_type=AnswerType("one-part"),
                answ_part=AnswerPart("base")
            )
    def test_addon_questions_must_have_a_base_id(self):
        q_id=0
        with pytest.raises(ValueError, match=f"Question {q_id}: addon questions must have a base_id."):
            addon_q = Question(
                id=q_id,
                text="Select job type:",
                q_type=QuestionType("open-ended"),
                answ_type=AnswerType("two-part"),
                answ_part=AnswerPart("addon"),
                base_id=None
            )
    def test_non_addon_questions_cannot_have_a_base_id(self):
        q_id=0
        with pytest.raises(ValueError, match=f"Question {q_id}: non-addon questions must not have a base_id."):
            non_addon_q = Question(
                id=q_id,
                text="Select job type:",
                q_type=QuestionType("open-ended"),
                answ_type=AnswerType("two-part"),
                answ_part=AnswerPart("base"),
                base_id=1
            )