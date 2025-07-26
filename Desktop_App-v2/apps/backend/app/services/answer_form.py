import logging
from datetime import date
from flask import jsonify, current_app, session
from ..models import Question, Node, LinkedList
from ..utils.linked_list_handler import get_ll

logger = logging.getLogger(__name__)

def is_first_question(q:Question) -> bool:
    """Checks if the given question is the first question in the linked list"""
    ll:LinkedList = get_ll(current_app)
    return q == ll.head.question

def is_last_question(q:Question) -> bool:
    """Check if the given question is the last question in the linked list"""
    ll:LinkedList = get_ll(current_app)
    if ll.tail.addon is not None:
        last_question = ll.tail.addon
    else:
        last_question = ll.tail.question
    return q == last_question

def get_question_from_dictionary(node:Node, q_dict:dict):
    """Get the Question from its node and its dictionary representation"""
    if node.question.q_detail == q_dict["q_detail"]:
        return node.question
    elif node.addon.q_detail == q_dict["q_detail"]:
        return node.addon
    
def get_first_non_preset_node(ll:LinkedList)->Node|None:
    """Returns the first Node whose question's a_type is not preset, if any"""
    curr:Node=ll.head
    result_node:Node=curr
    a_type_val=curr.question.a_type.value
    if a_type_val!="preset":
        return result_node
    
    while a_type_val=="preset" and curr is not None:
        a_type_val=curr.question.a_type.value
        result_node=curr
        curr=curr.next
    if a_type_val=="preset":    #all questions are preset questions
        return None
    return result_node

# def get_next_non_preset_question(forwards:bool)->Node|None:
#     """Return the first question before or after the current question whose a_type is not preset, if any"""
#     #NOTE: It should be impossible for one to go back into a series of preset questions that start the ll
#     # because the button would be disabled on the frontend, however, it is possible to go forwards into a series of presets that end it

def get_current_node(ll:LinkedList) -> Node:
    if "curr_node" in session:
        curr_node_dict:dict = session["curr_node"]
        curr_node:Node = ll.getByDetail(curr_node_dict["question"]["q_detail"])   #get the current node by the detail
    else:
        curr_node:Node = ll.head
    return curr_node
def get_current_question(ll:LinkedList, curr_node:Node=None) -> Question:
    if not curr_node:   # if curr_node isn't passed, get it from ll
        curr_node = get_current_node(ll)

    if "curr_question" in session:  # get via session variable if possible
        # logger.debug("question session variable found!")
        curr_question_dict:dict = session["curr_question"]
        curr_question:Question = get_question_from_dictionary(curr_node, curr_question_dict)
    else:   # no curr_question has been set, assume this is the first question being called
        if curr_node == ll.head:
            curr_question:Question = curr_node.question
        else:
            raise LookupError("Current question not found")
    logging.debug(f"curr_question is {curr_question}")
    return curr_question
def get_current_node_and_question(ll:LinkedList):
    curr_node:Node = get_current_node(ll)
    curr_question:Question = get_current_question(ll, curr_node)
    return (curr_node, curr_question)


def get_current_question_display_info(curr_node:Node, curr_question:Question):
    """Returns the display info of the given question
        Parameters:
            curr_node: Node - The Node of the current question
            curr_question: Question - The current question
        
        Returns:
        res: dict - A dictionary with the following keys:
            "q_str": str - The q_str of the current question
            "next_question_a_type": str - (optional) The value of the a_type of the next question
            "is_last": str - Whether or not the current question is the last question
            "is_addon": str - Whether or not the current question is an addon question
    """
    res = {"q_str": curr_question.q_str}
    if curr_node.addon:
        if curr_question == curr_node.addon:
            res["is_addon"] = "true"
            next_question = curr_node.next.question if curr_node.next else None
        else:
            res["is_addon"] = "false"
            next_question = curr_node.addon
    else:
        res["is_addon"] = "false"
        next_question = curr_node.next.question if curr_node.next else None
    # logger.debug(f"next question is {next_question}.")

    is_last = is_last_question(curr_question)
    if is_last:
        res["is_last"] = "true"
    else:
        res["is_last"] = "false"
        # logger.debug(f"Next question's a_type is: {next_question.a_type.value}")
        res["next_question_a_type"] = next_question.a_type.value

    return res
    
def get_next_question_display_info(curr_node:Node, curr_question:Question):
    """Returns the display info of the question after the given question
        Parameters:
            curr_node: Node - The Node of the current question
            curr_question: Question - The current question
        
        Returns:
        res: dict - A dictionary with the following keys:
            "q_str": str - The q_str of the next question
            "next_question_a_type": str - (optional) The value of the a_type of the question after the next question
            "is_last": str - Whether or not the next question is the last question
            "is_addon": str - Whether or not the next question is an addon question
    """
    curr_is_addon = False
    if curr_node.addon:
        if curr_question == curr_node.addon:
            curr_is_addon = True

    if curr_is_addon or not curr_node.addon:
        #the next question is the next node's question
        next_node:Node=curr_node.next
        next_question:Question=curr_node.next.question
    else:
        # the current question has an addon, which will be the next question
        next_node:Node=curr_node
        next_question:Question=curr_node.addon

    session["curr_question"] = next_question.as_dict()
    session["curr_node"] = next_node.as_dict()

    return get_current_question_display_info(next_node, next_question)

def get_prev_question_display_info(curr_node:Node, curr_question:Question):
    """Returns the display info of the question before the given question
        Parameters:
            curr_node: Node - The Node of the current question
            curr_question: Question - The current question
        
        Returns:
        res: dict - A dictionary with the following keys:
            "q_str": str - The q_str of the previous question
            "curr_question_a_type: str - The value of the a_type of the previous question
            "next_question_a_type": str - The value of the a_type of the current question
            "is_first": str - Wheter or not the previous question is the first question
            "is_addon": str - Whether or not the previous question is an addon question
    """
    res = {}
    curr_is_addon = False
    
    if curr_node.addon:
        if curr_question == curr_node.addon:
            curr_is_addon = True

    if curr_is_addon:
        prev_node = curr_node
        prev_question = curr_node.question
    else:
        prev_node = curr_node.prev
        if prev_node.addon:
            prev_question = prev_node.addon
        else:
            prev_question = prev_node.question

    res["curr_question_a_type"] = prev_question.a_type.value
    
    if is_first_question(prev_question):
        res["is_first"] = "true"
    else:
        res["is_first"] = "false"
        
    session["curr_question"] = prev_question.as_dict()
    session["curr_node"] = prev_node.as_dict()

    res.update(get_current_question_display_info(prev_node, prev_question))
    del res["is_last"]  # always false, so no need to include
    return res



# ANSWER QUESTIONS
def append_addon_answer(addon_answer:str, curr_node:Node) -> str:
    answer = curr_node.answer
    answer += addon_answer
    curr_node.answer = answer
    logger.info(f"Answer appended to. Answer is now {answer}")
    return answer

## ANSWER PRESETS
def answer_application_date():
    return date.today().strftime("%m/%d/%Y")
def answer_empty():
    return " "
def answer_leading_presets(ll:LinkedList):
    """Loop backwards from the first non-preset node and answer all, if any, preset nodes before it"""
    curr:Node = get_first_non_preset_node()
    if curr != ll.head:
        while curr != ll.head: 
            curr = curr.prev
            #Find what preset question the node contains and answer it
            which_preset:str = curr.question.q_str
            answ = ""
            match which_preset:
                case "appDate":
                    answ = answer_application_date()
                case "empty":
                    answ = answer_empty()
            curr.answer = answ

def answer_preset_node(node:Node, p_type:str):
    answ=""
    match p_type:
        case "appDate":
            answ=answer_application_date()
        case "empty":
            answ=answer_empty()
        case _:
            raise ValueError(f"Unidentified preset type {p_type}")
    node.answer = answ
    return answ
    

def get_all_answers(ll:LinkedList):
    return ll.getAllAnswers()
