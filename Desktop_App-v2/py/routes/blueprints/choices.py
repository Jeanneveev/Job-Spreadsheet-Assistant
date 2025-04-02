"""Blueprints for routes related to the choices of a Question"""
from flask import Blueprint, session, request, jsonify

choice_bp = Blueprint("choices", __name__)

@choice_bp.route("/set_curr_choices", methods=["POST"])
def set_curr_choices():
    """Set the past list of options as the value of curr_opt_lst"""
    options=request.get_json()["choices"]
    # Remove duplicates NOTE: Can't use set because it's unordered
    options=list(dict.fromkeys(options))
    session['curr_opt_lst']=options
    session.modified = True
    return "Current options set",200

@choice_bp.route("/add_choices", methods=["POST"])
def add_choices_to_list():
    """Add any number of passed options to the overall list of options"""
    options=request.get_json()["choices"]
    # print("Options are", options)
    # Initialize the lists if they don't exist
    if 'all_opt_lst' not in session:
        # print("Session variable not found. Initializing...")
        session['all_opt_lst'] = []
        session.modified = True
    # Append to the list
    all_opt_lst:list[str]=session['all_opt_lst']
    # print("Before appending:",all_opt_lst,curr_opt_lst)
    all_opt_lst.extend(options)
    # print("Before setting:",all_opt_lst,curr_opt_lst)
    # Remove duplicates NOTE: Can't use set because it's unordered
    all_opts=list(dict.fromkeys(all_opt_lst))
    # print("After setting:",all_opts,curr_opts)
    # Turn back into lists in order to be serializable
    all_opt_lst=list(all_opts)
    # print("After appending:",all_opt_lst,curr_opt_lst)
    session['all_opt_lst'] = all_opt_lst
    session.modified = True
    return "Options added to all list"

@choice_bp.route("/get_all_choices",methods=["GET"])
def get_all_choices():
    options:list[str]=session.get("all_opt_lst",[])
    return jsonify({"result":options})
@choice_bp.route("/get_current_choices",methods=["GET"])
def get_curr_options():
    options:list[str]=session.get("curr_opt_lst",[])
    return jsonify({"result":options})

@choice_bp.route("/clear_current_choices",methods=["GET"])
def clear_current_choices():
    """Clear the curr_options session variable"""
    if 'curr_opt_lst' in session:
        print("Now clearing curr_opt_lst")
        session['curr_opt_lst'] = []
        session.modified = True
    options:list[str]=session.get("curr_opt_lst")
    return f"Current options cleared. curr_opt_lst is now {options}"
