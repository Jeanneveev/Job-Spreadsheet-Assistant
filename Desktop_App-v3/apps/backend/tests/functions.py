from ..src.model.question import Question, QuestionType, AnswerType, AnswerPart
from ..src.model.question_set import QuestionSet
from ..src.model.form_session import FormSession

def make_open_onepart_questions(count:int):
    if count == 1:
        return Question(
            0,
            f"example_0",
            QuestionType("open-ended"),
            AnswerType("one-part")
        )
    return [
        Question(
            x,
            f"example_{x}",
            QuestionType("open-ended"),
            AnswerType("one-part")
        )
        for x in range(count)
    ]
def make_open_base_questions(count:int):
    if count == 1:
        return Question(
            0,
            f"example_0",
            QuestionType("open-ended"),
            AnswerType("two-part"),
            AnswerPart("base")
        )
    return [
        Question(
            x,
            f"example_{x}",
            QuestionType("open-ended"),
            AnswerType("two-part"),
            AnswerPart("base")
        )
        for x in range(count)
    ]

def make_question_set(num_questions:int=1):
    if num_questions == 1:
        return QuestionSet([make_open_onepart_questions(num_questions)])
    return QuestionSet(make_open_onepart_questions(num_questions))

def make_form_session(num_questions:int=1):
    return FormSession(make_question_set(num_questions))