"""Blueprints for routes related to the 'Answer Questions' form"""
import logging
from ...models import Question, Node, LinkedList
from flask import Blueprint, request, session, jsonify, current_app
from ...utils.linked_list_handler import get_ll
from ...services.answer_form import (
    get_first_non_preset_node, answer_leading_presets, get_all_answers, get_current_node,
    get_current_node_and_question, get_current_question_display_info,
    get_next_question_display_info,  get_prev_question_display_info,
    append_addon_answer, answer_preset_node
)

logger = logging.getLogger(__name__)
answ_bp = Blueprint("answer", __name__)

@answ_bp.route("/get_first_a_type")
def get_first_a_type():
    ll:LinkedList = get_ll(current_app)
    head:Node|None=get_first_non_preset_node(ll)
    if head is None:    #all questions are preset questions
        return "Please add at least one non-preset question", 404
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
    ll:LinkedList = get_ll(current_app)
    first_valid:Node = get_first_non_preset_node(ll)
    answer_leading_presets(ll)    # answer any leading preset questions
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
    ll:LinkedList = get_ll(current_app)
    (curr_node, curr_question) = get_current_node_and_question(ll)

    return jsonify(get_next_question_display_info(curr_node, curr_question))
    
@answ_bp.route("/get_prev_question")
def get_prev_question():
    """Get the display info of the previous question
    
     Returns:
        A dictionary with the following keys:
            "q_str": str - The q_str of the previous question
            "curr_question_a_type: str - The value of the a_type of the previous question
            "next_question_a_type": str - The value of the a_type of the current question
            "is_first": str - Wheter or not the previous question is the first question
            "is_addon": str - Whether or not the previous question is an addon question
    """
    ll:LinkedList = get_ll(current_app)
    (curr_node, curr_question) = get_current_node_and_question(ll)

    return jsonify(get_prev_question_display_info(curr_node, curr_question))
    

@answ_bp.route("/set_answer", methods=["POST"])
def add_answer():
    answ:str = request.data.decode("utf-8")
    ll:LinkedList = get_ll(current_app)
    curr_node:Node = get_current_node(ll)
    curr_node.answer = answ
    logger.info(f"Answer {answ} set")
    return f"Answer {answ} set"
@answ_bp.route("/add_addon_answer", methods=["POST"])
def add_addon_answer():
    answ:str = request.data.decode("utf-8")
    answer=f" ({answ.lower()})"
    ll:LinkedList = get_ll(current_app)
    curr_node:Node = get_current_node(ll)
    full_answer:str = append_addon_answer(answer, curr_node)
    return f'Answer appended to. Answer is now "{full_answer}"'

@answ_bp.route("/set_preset_answer", methods=["POST"])
def add_preset_answer():
    ll:LinkedList = get_ll(current_app)
    curr_node:Node = get_current_node(ll)
    preset_type:str = request.data.decode("utf-8")
    try:
        answ = answer_preset_node(curr_node, preset_type)
        return f"Preset answer {answ} set", 200
    except ValueError:
        return f'Preset type "{preset_type}" does not exist', 404
    

@answ_bp.route("/get_answer_options", methods=["GET"])
def get_answer_options():
    ll:LinkedList = get_ll(current_app)
    (_, curr_question) = get_current_node_and_question(ll)
    return jsonify(curr_question.options)

@answ_bp.route("/get_all_answers", methods=["GET"])
def get_all_answers_endpoint():
    """A route to get the jsonified list of all the answers
        NOTE: Only used for printing to console currently
    """
    ll:LinkedList = get_ll(current_app)
    return jsonify(get_all_answers(ll))

@answ_bp.route("/reset_answer_form", methods=["DELETE"])
def reset_answer_form():
    session.pop("curr_node")
    session.pop("curr_question")

    return "Reset current node and question"