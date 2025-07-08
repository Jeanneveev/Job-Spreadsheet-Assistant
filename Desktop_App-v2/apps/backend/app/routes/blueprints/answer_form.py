"""Blueprints for routes related to the 'Answer Questions' form"""
import logging
from ...models import Question, Node
from flask import Blueprint, request, session, jsonify, current_app
from ...utils.linked_list_handler import get_ll
from ...service.service import (
    get_first_non_preset_node, answer_leading_presets,
    is_last_question, answer_application_date, get_all_answers_handler, answer_empty,

    get_question, get_current_question_display_info, get_next_question_display_info,
    get_prev_question_display_info
)

logger = logging.getLogger(__name__)
answ_bp = Blueprint("answer", __name__)

@answ_bp.route("/get_first_a_type")
def get_first_a_type():
    head:Node|None=get_first_non_preset_node()
    if head is None:    #all questions are preset questions
        return "Please add at least one non-preset question", 202
    else:
        a_type_val=head.question.a_type.value
        return a_type_val
    
## DISPLAY INFO
@answ_bp.route("/get_first_question")
def get_first_question_display_info()->dict:
    """Get the display info of the first non-preset Question in the LinkedList
    
    Returns:
        A dictionary with the following keys:
            "q_str": str - The q_str of the requested question
            "next_question_a_type": str - (optional) The value of the a_type of the next question
            "is_last": str - Whether or not the requested question is the last question
    """
    first_valid:Node=get_first_non_preset_node()
    answer_leading_presets()    # answer any leading preset questions
    res = get_current_question_display_info(first_valid, first_valid.question)
    del res["is_addon"] #it's impossible to be anything but "false", so just remove it
    return jsonify(res)

@answ_bp.route("/get_next_question")
def get_next_question()->dict:
    """Get the display info of the next question

    Returns:
        res: dict - A dictionary with the following keys:
            "q_str": str - The q_str of the next question
            "next_question_a_type": str - (optional) The value of the a_type of the question after the next question
            "is_last": str - Whether or not the next question is the last question
            "is_addon": str - Whether or not the next question is an addon question
    """
    ll = get_ll(current_app)
    #Get the current node and question
    curr_node_dict:dict = session["curr_node"]
    curr_node:Node = ll.getByDetail(curr_node_dict["question"]["q_detail"])   #get the current node by the detail
    curr_question_dict:dict = session["curr_question"]
    curr_question = get_question(curr_node, curr_question_dict)

    return jsonify(get_next_question_display_info(curr_node, curr_question))
    
@answ_bp.route("/get_prev_question")
def get_prev_question():
    """Get the display info of the previous question
    
     Returns:
        A dictionary with the following keys:
            "q_str": str - The q_str of the previous question
            "next_question_a_type": str - The value of the a_type of the current question
            "is_first": str - Wheter or not the previous question is the first question
            "is_addon": str - Whether or not the previous question is an addon question
    """
    ll = get_ll(current_app)
    #Get the current node and question
    curr_node_dict:dict=session["curr_node"]
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])   #get the current node by the detail
    curr_question_dict:dict=session["curr_question"]
    curr_question = get_question(curr_node, curr_question_dict)

    return jsonify(get_prev_question_display_info(curr_node, curr_question))
    

@answ_bp.route("/add_answer",methods=["POST"])
def add_answer():
    answ:str = request.data.decode("utf-8")
    ll = get_ll(current_app)
    curr_node_dict:dict=session["curr_node"]
    #get the node from the detail
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])
    curr_node.answer=answ
    logger.info(f"Answer {answ} set")
    return f"Answer {answ} set"
@answ_bp.route("/add_addon_answer",methods=["POST"])
def add_addon_answer():
    answ:str = request.data.decode("utf-8")
    ll = get_ll(current_app)
    answer=f" ({answ.lower()})"
    curr_node_dict:dict=session["curr_node"]
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])
    curr_node_answ=curr_node.answer
    logger.info(f"curr_node_anw is {curr_node_answ}")
    curr_node_answ+=answer
    curr_node.answer=curr_node_answ
    logger.info(f"Answer appended to. Answer is now {curr_node_answ}")
    return f"Answer appended to. Answer is now {curr_node_answ}"


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

@answ_bp.route("/get_all_answers",methods=["GET"])
def get_all_answers():
    """A route to get the jsonified list of all the answers
        NOTE: Only used for printing to console currently
    """
    return get_all_answers_handler(by_route=True)
