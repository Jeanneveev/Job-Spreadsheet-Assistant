from enum import Enum
from typing import Optional
from dataclasses import dataclass

class QuestionType(str, Enum):
    OPEN_ENDED = "open-ended"
    MULTIPLE_CHOICE = "multiple-choice"
    PRESET = "preset"
    def __contains__(cls, item): 
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True

class AnswerType(str, Enum):
    ONE_PART = "one-part"
    TWO_PART = "two-part"
    def __contains__(cls, item): 
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True

class AnswerPart(str, Enum):
    BASE = "base"
    ADDON = "addon"
    def __contains__(cls, item): 
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True

@dataclass
class Question:
    id : int
    text : str
    q_type : QuestionType
    answ_type : AnswerType
    answ_part : Optional[AnswerPart] = None
    choices : Optional[list[str]] = None
    base_id : Optional[int] = None

    def __post_init__(self):    #Validation
        if not isinstance(self.q_type, QuestionType):
            raise TypeError(f'Question {self.id}: invalid q_type: "{self.q_type}"')
        if not isinstance(self.answ_type, AnswerType):
            raise TypeError(f'Question {self.id}: invalid answ_type: "{self.answ_type}"')
        if self.answ_part and not isinstance(self.answ_part, AnswerPart):
            raise TypeError(f'Question {self.id}: invalid answ_part: "{self.answ_part}"')

        #Multiple-choice questions must have choices
        if self.q_type == QuestionType.MULTIPLE_CHOICE and not self.choices:
            raise ValueError(f"Question {self.id}: multiple-choice questions must include choices.")
        #Non-multiple-choice questions cannot have choices
        if self.q_type != QuestionType.MULTIPLE_CHOICE and self.choices:
            raise ValueError(f"Question {self.id}: only multiple-choice questions can have choices.")
        #Two-part questions must have an answer part
        if self.answ_type == AnswerType.TWO_PART:
            if self.answ_part not in {AnswerPart.BASE, AnswerPart.ADDON}:
                raise ValueError(f"Question {self.id}: two-part questions must have a valid answ_part.")
            #Addon questions must have a base id
            if self.answ_part == AnswerPart.ADDON and not self.base_id:
                raise ValueError(f"Question {self.id}: addon questions must have a base_id.")
        else:
            #One-part questions can't have an answer part
            if self.answ_part is not None:
                raise ValueError(f"Question {self.id}: one-part questions must not have answ_part.")
        #Non-addon questions can't have a base id
        if self.answ_part != AnswerPart.ADDON and self.base_id is not None:
            raise ValueError(f"Question {self.id}: non-addon questions must not have a base_id.")

        