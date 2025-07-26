"""Blueprints for routes related to CRUD functionality for questions in a question group"""
import logging
from flask import Blueprint, request, session, current_app, jsonify
from app.models import Question, Node, LinkedList
from app.utils.linked_list_handler import get_ll, override_ll
from app.services import get_question_from_form, add_preset, get_reordered_ll, delete_question_or_node

logger = logging.getLogger(__name__)
q_crud_bp = Blueprint("q_crud", __name__)

## CREATE
@q_crud_bp.route("/add_question", methods=["POST"])
def add_question():
    """Add a new question to the question group with the info passed"""
    ll = get_ll(current_app)
    form = request.form
    # logger.info("Form is", form)

    new_question:Question = get_question_from_form(form)
    
    new_node = Node(new_question)
    ll.append(new_node)
    # ll.printLL()

    if new_question.a_type.value == "multiple-choice":
        return {"new_q_a_type": "multiple-choice"}
    else:
        return {"new_q_a_type": "singular"}
    
@q_crud_bp.route("/add_question/addon", methods=["POST"])
def add_addon():
    ll = get_ll(current_app)
    form = request.form
    
    new_question:Question = get_question_from_form(form)
    # get the node of the question this one is adding onto
    base_detail = form["addon_to"]
    base_node = ll.getByDetail(base_detail)
    base_node.addon = new_question
    logger.info(f"Addon \"{new_question.q_detail}\" added to base node \"{base_node.question.q_detail}\"")
    
    if new_question.a_type.value == "multiple-choice":
        return {"new_q_a_type": "multiple-choice"}
    else:
        return {"new_q_a_type": "singular"}
    
@q_crud_bp.route("/add_question/preset", methods=["POST"])
def add_preset_question():
    value:str = request.data.decode("utf-8")
    ll = get_ll(current_app)
    try:
        add_preset(ll, value)
    except ValueError as e:
        return str(e), 409
    
    return f"Preset question: {value} added"

## READ
@q_crud_bp.route("/get_ll_json", methods=["GET"])
def all_to_json():
    """Get every node in the linked list and return them as json"""
    ll:LinkedList = get_ll(current_app)
    # logger.info("Get_ll_json called. Linked list JSON is: ",ll.getAll())
    return jsonify(ll.getAll())

@q_crud_bp.route("/check_if_questions_exists", methods=["GET"])
def check_ll_exists():
    ll:LinkedList = get_ll(current_app)
    if ll.head == None: #if nothing's in the LinkedList
        return "false"
    elif ll.head.question == None:
        return "false"
    else:
        return "true"

## EDIT
@q_crud_bp.route("/reorder_questions", methods=["POST"])
def reorder_questions():
    """Upon being given an ordered list of node details, reorder the linked list to be in that order"""
    ll = get_ll(current_app)
    new_q_detail_order:list = request.get_json()["order"]
    logger.info(f"The new order will be {new_q_detail_order}")
    logger.info(f"Before reordering, the ll looks like: {ll.returnLL()}")
    
    try:
        new_ll = get_reordered_ll(ll, new_q_detail_order)
        ll = override_ll(current_app, new_ll)
        logger.info(f"After reordering, the ll looks like: {ll.returnLL()}")
    except ValueError as e:
        return str(e), 404

    return "Linked List reordered", 200

## DELETE
@q_crud_bp.route("/delete_question", methods=["DELETE"])
def del_node():
    """Given a node's detail, find and delete it"""
    data = request.get_json() # {"deleting_detail": _, "is_addon": true or false}
    del_detail:str = data["deleting_detail"]
    if data["is_addon"] == "true":
        is_addon = True
    else:
        is_addon = False

    ll = get_ll(current_app)
    try:
        msg = delete_question_or_node(ll, del_detail, is_addon)
        return msg, 200
    except ValueError as e:
        return str(e), 404
