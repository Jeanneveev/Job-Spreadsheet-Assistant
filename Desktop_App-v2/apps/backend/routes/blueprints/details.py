"""Blueprints for routes related to the set of q_details"""
import json
import logging
from flask import Blueprint, session, current_app, request
from ...utils.linked_list_handler import get_ll
from urllib.parse import unquote

logger = logging.getLogger(__name__)
detail_bp = Blueprint("details", __name__)

@detail_bp.route("/add_detail",methods=["POST"])
def add_detail_to_list():
    """Add a q_detail to a persistent list of q_details"""
    detail:str = request.data.decode("utf-8")
    # Validate that something was passed
    if detail == "":
        return "No detail was given", 404
    # Initialize the list if it doesn't exist
    if 'detail_lst' not in session:
        logger.info("Session variable not found. Initializing...")
        session['detail_lst'] = json.dumps([])
        session.modified = True
    # Append to the list
    detail_lst:list[str]=json.loads(session['detail_lst'])
    # logger.info("Before appending:",detail_lst)
    detail_lst.append(detail)
    # logger.info("After appending:",detail_lst)
    session['detail_lst'] = json.dumps(detail_lst)
    session.modified = True

    return {"result":json.dumps(detail_lst)}

@detail_bp.route("/delete_detail", methods=["DELETE"])
def delete_detail_from_list():
    """Delete a given q_detail from the list of details"""
    detail:str = request.data.decode("utf-8")
    detail_lst=session.get("detail_lst",json.dumps([]))
    detail_lst:list|list[str]=json.loads(detail_lst)
    #if detail_lst hasn't been initialized yet or its empty, return error
    if detail_lst == []:
        return "No details to delete", 404
    #if the given detail isn't in detail_lst
    if detail not in detail_lst:
        return "Detail is not in detail_lst", 400
    #else, remove the given detail
    # logger.info(f"before removal, detail_lst is: {detail_lst}")
    detail_lst.remove(detail)
    # logger.info(f"after removal, detail_lst is: {detail_lst}")
    session['detail_lst'] = json.dumps(detail_lst)
    session.modified = True
    return f"Detail {detail} deleted. Detail_lst is now: {json.dumps(detail_lst)}"

@detail_bp.route("/clear_details", methods=["DELETE"])
def clear_all_details():
    """Clear all details from the list of details"""
    detail_lst=session.get("detail_lst",json.dumps([]))
    detail_lst:list|list[str]=json.loads(detail_lst)
    #reset detail_lst to "[]"
    detail_lst_str:str = json.dumps([])
    session["detail_lst"]=detail_lst_str
    return f"Any if all details deleted. Detail_lst is now: {detail_lst_str}"

# @detail_bp.route("/get_details",methods=["GET"])
# def get_all_details():
#     details:list[str]=session.get("detail_lst",json.dumps([]))
#     return details

@detail_bp.route("/get_base_details", methods=["GET"])
def get_all_base_details():
    """Get the details of all nodes with the q_type 'base'"""
    ll = get_ll(current_app)
    base_list=ll.getByQType("base")
    return json.dumps(base_list)

@detail_bp.route("/check_detail/<detail>", methods=["GET"])
def check_detail(detail:str):
    """Check if the given q_detail exists within the list of
    details
    """
    detail:str = unquote(detail)
    details:list[str]=session.get("detail_lst",[])
    if detail in details:
        return {"result":"True","detail_list":details}
    else:
        return {"result":"False","detail_list":details}

