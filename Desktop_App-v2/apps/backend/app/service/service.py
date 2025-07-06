from datetime import date
from flask import jsonify, current_app, session
from ..models import Question, Node, LinkedList
from ..utils.linked_list_handler import get_ll

## NAVIGATE PRESETS
def get_first_non_preset_node()->Node|None:
    """Returns the first Node whose question's a_type is not preset, if any"""
    ll = get_ll(current_app)
    head:Node=ll.head
    result_node:Node=head
    a_type_val=head.question.a_type.value
    if a_type_val!="preset":
        return result_node
    
    while a_type_val=="preset" and head is not None:
        a_type_val=head.question.a_type.value
        result_node=head
        head=head.next
    if a_type_val=="preset":    #all questions are preset questions
        return None
    return result_node

# def get_next_non_preset_question(forwards:bool)->Node|None:
#     """Return the first question before or after the current question whose a_type is not preset, if any"""
#     #NOTE: It should be impossible for one to go back into a series of preset questions that start the ll
#     # because the button would be disabled on the frontend, however, it is possible to go forwards into a series of presets that end it
    
# ANSWER QUESTIONS
## ANSWER PRESETS
def answer_application_date():
    return date.today().strftime("%m/%d/%Y")
def answer_empty():
    return " "
def answer_leading_presets():
    """Loop backwards from the first non-preset node and answer all, if any, preset nodes before it"""
    ll = get_ll(current_app)
    curr:Node=get_first_non_preset_node()
    if curr!=ll.head:
        while curr!=ll.head: 
            curr=curr.prev
            #Find what preset question the node contains and answer it
            which_preset:str=curr.question.q_str
            answ=""
            match which_preset:
                case "appDate":
                    answ=answer_application_date()
                case "empty":
                    answ=answer_empty()
            curr.answer=answ

def get_all_answers_handler(by_route:bool):
    """
    A handler function for get_all_answers

    Description: This function gets and returns all of the answers set in
    the linked list and returns it as a list.
    Depending on the value of the by_route parameter, it will return a
    jsonified response or a regular list, to be used by routes and Python
    functions respectively.
    """
    ll = get_ll(current_app)
    all_nodes_dict=ll.getAll()
    res=[]
    for node_dict in all_nodes_dict:
        if "answer" in node_dict:
            res.append(node_dict["answer"])
    
    if by_route==True:
        return jsonify(res)
    else:
        return res
    

def get_next_node_and_question(curr_node:Node, curr_question_dict:dict):
    on_addon=False
    next_is_addon=False
    if curr_node.addon:
        if curr_question_dict==curr_node.addon.as_dict():    #the current question is the node's addon question
            on_addon=True

    if (on_addon==True) or (curr_node.addon is None):   #the current question is an addon or doesn't have an addon
        #the next question is the next node's question
        next_question:Question=curr_node.next.question
        next_node:Node=curr_node.next
    else:   #the current question has an addon, which will be the next question
        next_question:Question=curr_node.addon
        next_node:Node=curr_node
        next_is_addon=True
    return (next_node, next_question, next_is_addon)

# def get_last_question()->Question:
#     """Return the last Question in the linked list"""
#     ll = get_ll(current_app)
#     if ll.tail.addon is not None:
#         return ll.tail.addon
#     else:
#         return ll.tail.question
    
def is_last_question(q:Question)->bool:
    """Check if the given question is the last question in the linked list"""
    ll = get_ll(current_app)
    if ll.tail.addon is not None:
        last_question = ll.tail.addon
    else:
        last_question = ll.tail.question
    return q == last_question



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
    # print(f"next question is {next_question}.")

    is_last = is_last_question(curr_question)
    if is_last:
        res["is_last"] = "true"
    else:
        res["is_last"] = "false"
        # print(f"Next question's a_type is: {next_question.a_type.value}")
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
            "next_question_a_type": str - The value of the a_type of the current question
            "is_addon": str - Whether or not the next question is an addon question
    """
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
        
    session["curr_question"] = prev_question.as_dict()
    session["curr_node"] = prev_node.as_dict()

    res = get_current_question_display_info(prev_node, prev_question)
    del res["is_last"]  # always false, so no need to include
    return res

