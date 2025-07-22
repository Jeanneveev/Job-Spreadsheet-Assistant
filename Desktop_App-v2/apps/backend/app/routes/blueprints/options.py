"""Blueprints for routes related to the options of a Question"""
import logging
from flask import Blueprint, session, request, jsonify, current_app
from ...models import LinkedList
from ...utils.linked_list_handler import get_ll
from ...services import get_current_question, add_options_to_question, add_new_options_to_all_options

logger = logging.getLogger(__name__)
opt_bp = Blueprint("options", __name__)

@opt_bp.route("/set_curr_options", methods=["POST"])
def set_curr_options():
    """Adds the given options to the current question"""
    options = request.get_json()["options"]
    ll:LinkedList = get_ll(current_app)
    curr_question = get_current_question(ll)
    curr_options = add_options_to_question(options, curr_question)
    return f"Current options: {curr_options} set"

@opt_bp.route("/add_options", methods=["POST"])
def add_options_to_list():
    """Add any number of passed options to the overall list of options"""
    options = request.get_json()["options"]
    all_options = add_new_options_to_all_options(options)

    return f"Options {options} added to all options list. All options list is now {all_options}"

@opt_bp.route("/get_all_options", methods=["GET"])
def get_all_options():
    options:list[str]=session.get("all_options",[])
    return jsonify({"all_options": options})
@opt_bp.route("/get_current_options", methods=["GET"])
def get_curr_options():
    options:list[str]=session.get("curr_options",[])
    return jsonify({"curr_options": options})

@opt_bp.route("/clear_session_options", methods=["DELETE"])
def clear_current_options():
    """Clear the curr_options session variable"""
    if "curr_options" in session:
        logger.info("Now clearing curr_options")
        session["curr_options"] = []
        session.modified = True
    options:list[str]=session.get("curr_options")
    return jsonify({"curr_options": options})
