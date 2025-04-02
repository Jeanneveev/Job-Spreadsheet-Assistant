"""Blueprints for routes related to the set of q_details"""
import json
from flask import Blueprint, session, current_app
from utils.linked_list_handler import get_ll

detail_bp = Blueprint("details", __name__)

@detail_bp.route("/add_detail/<detail>",methods=["GET","POST"])
def add_detail_to_list(detail):
    """Add a q_detail to a list of q_details"""
    # Initialize the list if it doesn't exist
    if 'detail_lst' not in session:
        print("Session variable not found. Initializing...")
        session['detail_lst'] = json.dumps([])
        session.modified = True
    # Append to the list
    detail_lst:list[str]=json.loads(session['detail_lst'])
    # print("Before appending:",detail_lst)
    detail_lst.append(detail)
    # print("After appending:",detail_lst)
    session['detail_lst'] = json.dumps(detail_lst)
    session.modified = True

    return {"response":f"{detail_lst}"}

@detail_bp.route("/get_all_details",methods=["GET"])
def get_all_details():
    details:list[str]=session.get("detail_lst",[])
    return {"result":details}

@detail_bp.route("/get_all_base_details", methods=["GET"])
def get_all_base_details():
    ll = get_ll(current_app)
    """Get the details of all nodes with the q_type 'base'"""
    base_list=ll.getByQType("base")
    return {"result":base_list}

@detail_bp.route("/check_detail/<detail>")
def check_detail(detail):
    details:list[str]=session.get("detail_lst",[])
    if detail in details:
        return {"result":"True","detail_list":details}
    else:
        return {"result":"False","detail_list":details}

