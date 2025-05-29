from .question import Question, QuestionType, AnswerType, AnswerPart
from .question_set import QuestionSet

class FormSession:
    def __init__(self, question_set:QuestionSet):
        self.question_set = question_set
        self._current_question_idx = 0
        self.answers = {}

    @property
    def current_question(self):
        return self.question_set.questions[self._current_question_idx]
    
    def next_question(self):
        if (self._current_question_idx + 1) > (len(self.question_set.questions) - 1):
            raise IndexError("There are no more next questions")
        self._current_question_idx += 1
    def prev_question(self):
        if self._current_question_idx == 0:
            raise IndexError("There are no previous questions")
        self._current_question_idx -= 1

    def on_first_question(self):
        return self.current_question == self.question_set.questions[0]
    def on_last_question(self):
        return self.current_question == self.question_set.questions[-1]
    
    def get_prompt(self):
        return self.current_question.text
    def get_question_type(self):
        return self.current_question.q_type.value
    def get_choices(self):
        if self.get_question_type() == "multiple-choice":
            return self.current_question.choices
        return None
    
    def answer_question(self, id, answer):
        self.answers[id] = answer
    def get_answer(self, id):
        return self.answers[id]
    def all_questions_answered(self):
        return self.answers.keys() == self.question_set._question_ids.keys()
    
    def can_confirm(self):
        return self.on_last_question() and self.all_questions_answered()