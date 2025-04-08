"""Blueprints for routes related to the 'Answer Questions' form"""
from datetime import date
from classes import Question, Node
from flask import Blueprint, request, session, jsonify, current_app
from utils.linked_list_handler import get_ll

answ_bp = Blueprint("answer", __name__)

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
def get_next_non_preset_question(forwards:bool)->Node|None:
    """Return the first question before or after the current question whose a_type is not preset, if any"""
    #NOTE: It should be impossible for one to go back into a series of preset questions that start the ll
    # because the button would be disabled on the frontend, however, it is possible to go forwards into a series of presets that end it
    
def answer_starter_presets():
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

def get_last_question()->Question:
    """Return the last Question in the linked list"""
    ll = get_ll(current_app)
    if ll.tail.addon is not None:
        return ll.tail.addon
    else:
        return ll.tail.question

@answ_bp.route("/get_first_a_type")
def get_first_a_type():
    head:Node|None=get_first_non_preset_node()
    if head is None:    #all questions are preset questions
        return "Please add at least one non-preset question", 202
    else:
        a_type_val=head.question.a_type.value
        return a_type_val
    
@answ_bp.route("/get_first_question")
def get_first_question_display_info()->dict:
    """Get the display info of the first non-preset Question in the LinkedList
    
    Returns:
        A dictionary with the following keys:
            "q_str": str - The q_str of the requested question
            "next_question_a_type": str - The value of the a_type of the next question
            "is_last": str - Whether or not the requested question is the last question
    """
    first_valid:Node=get_first_non_preset_node()
    last_q:Question=get_last_question()
    answer_starter_presets()
    # Set session variables
    session["curr_node"]=first_valid.as_dict()
    session["curr_question"]=first_valid.question.as_dict()

    if first_valid.question==last_q:
        fv_display_info:dict=first_valid.display_info(False,True)
    else:
        fv_display_info:dict=first_valid.display_info(False,False)
    return fv_display_info

@answ_bp.route("/get_next_question")
def get_next_question_display_info()->dict:
    """Get the display info of the next question

    Returns:
        res: dict - A dictionary with the following keys:
            "q_str": str - The q_str of the next question
            "next_question_a_type": str - The value of the a_type of the question after the next question
            "is_last": str - Whether or not the next question is the last question
            "is_addon": str - Whether or not the next question is an addon question
    """
    ll = get_ll(current_app)
    #Get the current node and question
    curr_node_dict:dict=session["curr_node"]
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])   #get the current node by the detail
    curr_question_dict:dict=session["curr_question"]
    on_addon=False
    next_is_addon=False
    if not curr_question_dict==curr_node.question.as_dict():    #the current question is the node's addon question
        on_addon=True

    #Get the next question
    if (on_addon==True) or (curr_node.addon is None):   #the current question is an addon or doesn't have an addon
        #the next question is the next node's question
        next_question:Question=curr_node.next.question
        next_node:Node=curr_node.next
    else:   #the current question has an addon, which will be the next question
        next_question:Question=curr_node.addon
        next_node:Node=curr_node
        next_is_addon=True
    session["curr_question"]=next_question.as_dict()
    session["curr_node"]=next_node.as_dict()

    last_q:Question=get_last_question()
    if next_question==last_q:
        res=next_node.display_info(next_is_addon,True)
    else:
        res=next_node.display_info(next_is_addon,False)
    #append "is_addon" to the dictionary if the next question is one
    if next_is_addon:
        res["is_addon"]="true"
    return res
    
@answ_bp.route("/get_prev_question")
def get_prev_question():
    """Get the display info of the previous question
    
     Returns:
        A dictionary with the following keys:
            "q_str": str - The q_str of the previous question
            "next_question_a_type": str - The value of the a_type of the current question
            "is_last": str - Whether or not the previous question is the last question (should always be false)
            "is_first": str - Wheter or not the previous question is the first question
            "is_addon": str - Whether or not the next question is an addon question
    """
    ll = get_ll(current_app)
    #Get the current node and question
    curr_node_dict:dict=session["curr_node"]
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])   #get the current node by the detail
    curr_question_dict:dict=session["curr_question"]
    on_addon=False
    prev_is_addon=False
    if not curr_question_dict==curr_node.question.as_dict():    #the current question is the node's addon question
        on_addon=True

    #Get the previous question
    if on_addon:    #the current question is an addon and the previous question is its base
        prev_node:Node=curr_node
        prev_question:Question=curr_node.question
    else:   #the previous question is in the previous node
        prev_node:Node=curr_node.prev
        if prev_node.addon is not None:
            prev_question:Question=prev_node.addon
            prev_is_addon=True
        else:
            prev_question:Question=prev_node.question
    session["curr_question"]=prev_question.as_dict()
    session["curr_node"]=prev_node.as_dict()
    
    res=prev_node.display_info(prev_is_addon,False)
    first_q:Question=ll.head.question
    if prev_question==first_q:
        res["is_first"]="true"
    if prev_is_addon:
        res["is_addon"]="true"
    return res

@answ_bp.route("/add_answer",methods=["POST"])
def add_answer():
    answ:str = request.data.decode("utf-8")
    ll = get_ll(current_app)
    curr_node_dict:dict=session["curr_node"]
    #get the node from the detail
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])
    curr_node.answer=answ
    print(f"Answer {answ} set")
    return f"Answer {answ} set"
@answ_bp.route("/add_addon_answer",methods=["POST"])
def add_addon_answer():
    answ:str = request.data.decode("utf-8")
    ll = get_ll(current_app)
    answer=f" ({answ.lower()})"
    curr_node_dict:dict=session["curr_node"]
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])
    curr_node_answ=curr_node.answer
    print(f"curr_node_anw is {curr_node_answ}")
    curr_node_answ+=answer
    curr_node.answer=curr_node_answ
    print(f"Answer appended to. Answer is now {curr_node_answ}")
    return f"Answer appended to. Answer is now {curr_node_answ}"

## PRESETS
def answer_application_date():
    return date.today().strftime("%m/%d/%Y")
def answer_empty():
    return " "
@answ_bp.route("/add_preset_answer",methods=["POST"])
def add_preset_answer():
    ll = get_ll(current_app)
    curr_node_dict:dict=session["curr_node"]
    #get the node from the detail
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])
    which_preset:str=request.get_json()["preset"]
    answ=""
    code=200
    match which_preset:
        case "appDate":
            answ=answer_application_date()
        case "empty":
            answ=answer_empty()
            code=201
    curr_node.answer=answ
    return f"Preset answer {answ} set", code

@answ_bp.route("/get_answer_options", methods=["GET"])
def get_answer_options():
    ll = get_ll(current_app)
    if "curr_node" in session:
        curr_node_dict:dict=session["curr_node"]
        curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])   #get the node from the detail
    else:
        curr_node:Node=ll.head
    if "curr_question" in session:
        curr_question_dict:dict=session["curr_question"]
        if curr_question_dict==curr_node.question.as_dict():
            curr_question:Question=curr_node.question
        else:
            curr_question:Question=curr_node.addon
    else:
        curr_question:Question=ll.head.question
    return jsonify({"options":curr_question.choices})

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

@answ_bp.route("/get_all_answers",methods=["GET"])
def get_all_answers():
    """A route to get the jsonified list of all the answers
        NOTE: Only used for printing to console currently
    """
    return get_all_answers_handler(by_route=True)
