from .question import Question


class Node:
    def __init__(self, question:Question, addon:Question = None):
        self.question = question
        self.addon = addon
        self.answer:str = None
        self.next:Node = None
        self.prev:Node = None

    def __str__(self) -> str:
        s = f"The Node is for the question \"{self.question.q_str}\""
        if self.addon:
            s += f". This Node also has the addon question \"{self.addon.q_str}\""
        return s

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False

        if self.question.q_detail != other.question.q_detail:
            return False
        if self.addon and not other.addon:
            return False
        if other.addon and not self.addon:
            return False
        if self.addon and other.addon:
            if self.addon.q_detail != other.addon.q_detail:
                return False

        return True

    def as_dict(self) -> dict:
        res_dict = {"question": self.question.as_dict()}
        if self.addon:
            res_dict["addon"] = self.addon.as_dict()
        if self.answer:
            res_dict["answer"] = self.answer
        return res_dict