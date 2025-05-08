from classes.question import Question

class Node:
    def __init__(self,question):
        self.question:Question=question
        self.addon:Question=None
        self.answer:str=None
        self.next:Node=None
        self.prev:Node=None
    def __str__(self)->str:
        s=f"The Node is for the question \"{self.question.q_str}\""
        if self.addon:
            s+=f". This Node also has the addon question \"{self.addon.q_str}\""
        return s
    def as_dict(self)->dict:
        res_dict={"question":self.question.as_dict()}
        if self.addon:
            res_dict["addon"]=self.addon.as_dict()
        if self.answer:
            res_dict["answer"]=self.answer
        return res_dict
    def display_info(self,requesting_addon:bool,requesting_last:bool)->dict:
        """Return only the necessary information for displaying this Node's Question in the frontend
        Parameters:
            self: Node - The current instance of a Node
            requesting_addon: bool - Whether or not the question of the Node that's being requested is its addon Question
            requesting_last: bool - Whether or not the question that's being asked for is the last Question in the linked list
        
        Returns:
            A dictionary with the following keys:
                "q_str": str - The q_str of the requested question
                "next_question_a_type": str - The value of the a_type of the next question
                "is_last": str - Whether or not the requested question is the last question
        """
        if not requesting_last:
            if requesting_addon:
                requested_question:Question=self.addon
                next_question:Question=self.next.question
            else:
                requested_question:Question=self.question
                #if the current question is a base question with an addon, the next question is its addon,
                # else its the question of the next Node
                if self.addon is not None:
                    next_question:Question=self.addon
                else:
                    next_question:Question=self.next.question
            return {"q_str":requested_question.q_str,"next_question_a_type":next_question.a_type.value,"is_last":"false"}
        else:
            if requesting_addon:
                requested_question:Question=self.addon
            else:
                requested_question:Question=self.question
            return {"q_str":requested_question.q_str,"is_last":"true"}