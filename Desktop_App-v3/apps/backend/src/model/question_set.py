from .question import Question, QuestionType, AnswerType, AnswerPart

class QuestionSet:
    def __init__(self, questions:list[Question]=None):
        self.questions = questions or []
        #in case any addon questions are initialized, validate them
        self._validate_addon_links()

    @property
    def _question_ids(self) -> dict:
        """A dictionary of question ids for easier searching"""
        qids = {}
        for question in self.questions:
            qids[question.id]=question
        return qids
    
    @property
    def _base_ids(self) -> dict:
        """A dictionary of base question ids for easier searching"""
        base_ids = {}
        for question in self.questions:
            if question.answ_part == AnswerPart.BASE:
                base_ids[question.id] = question
        return base_ids

    def _validate_addon_links(self):
        for question in self.questions:
            if not question.answ_part:
                continue
            if question.answ_part == AnswerPart.ADDON:
                if question.base_id not in self._base_ids:
                    raise ValueError(f"Addon question {question.id}: refers to nonexistent base_id")

    def append(self, questions:Question|list[Question]=None):
        if type(questions) == Question:
            if questions.id not in self._question_ids:
                self.questions.append(questions)
        else:
            for question in questions:
                if question.id not in self._question_ids:
                    self.questions.append(question)
        self._validate_addon_links()

    def get_question_by_id(self, qid):
        try:
            return self._question_ids[qid]
        except KeyError:
            raise ValueError(f"No question found with id {qid}")
    def get_questions_by(self, attr:str, value:str) -> list[Question]:
        #NOTE: Putting (value) here causes the if statement below to run all of them,
        #   so, I added it inside the if statement instead
        parse_attr = {
            "q_type":QuestionType,
            "answ_type":AnswerType,
            "answ_part":AnswerPart
        }
        if attr in parse_attr.keys():
            print("attr is:", attr)
            value = parse_attr[attr](value)
        
        results = []
        for question in self.questions:
            try:
                if getattr(question, attr) == value:
                    results.append(question)
            except AttributeError:  #if the attribut is optional, questions that don't have it will raise one
                continue
        return results
    
    def delete(self, id):
        question = self.get_question_by_id(id)
        self.questions.remove(question)

    