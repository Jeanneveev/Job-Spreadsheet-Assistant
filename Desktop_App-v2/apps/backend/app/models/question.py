from enum import Enum

class QTypeOptions(Enum):
    SINGULAR="singular"
    BASE="base"
    ADD_ON="add-on"
class ATypeOptions(Enum):
    MULT="multiple-choice"
    TEXT="open-ended"
    PRESET="preset"
class Question:
    def __init__(self,q_str:str,q_detail:str,q_type:QTypeOptions,a_type:ATypeOptions,options:list[str]=None)->None:
        self.q_str=q_str
        self.q_detail=q_detail
        self.q_type=q_type
        self.a_type=a_type
        self.options=options

    def __str__(self)->str:
        return f"{self.q_detail}"
    
    def __eq__(self, other):
        if not isinstance(other, Question):
            return False
        return self.q_detail == other.q_detail
    
    def as_dict(self)->dict:
        res_d={"q_str":self.q_str,"q_detail":self.q_detail,
                "q_type":self.q_type.value,"a_type":self.a_type.value}
        if self.options:
            res_d["options"]=self.options
        return res_d