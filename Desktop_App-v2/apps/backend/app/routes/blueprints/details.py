"""Blueprints for routes related to the set of q_details"""
import json
import logging
from flask import Blueprint, session, current_app, request, jsonify
from ...utils.linked_list_handler import get_ll
from ...services import (add_detail_to_all_details, remove_detail_from_all_details)
from urllib.parse import unquote

logger = logging.getLogger(__name__)
detail_bp = Blueprint("details", __name__)

@detail_bp.route("/add_detail", methods=["POST"])
def add_detail_to_list():
    """Add a unique q_detail to the all_details session variable"""
    detail:str = request.data.decode("utf-8")
    try:
        all_details = add_detail_to_all_details(detail)
    except ValueError as e:
        if str(e) == "Empty detail was passed":
            return "No detail was given", 404
        elif str(e) == "This detail already exists":
            return str(e), 409
        
    return jsonify({"all_details": all_details})

@detail_bp.route("/delete_detail", methods=["DELETE"])
def delete_detail_from_list():
    """Delete a given q_detail from the all_details session variable"""
    detail:str = request.data.decode("utf-8")
    try:
        all_details = remove_detail_from_all_details(detail)
    except ValueError as e:
        if str(e) == "Empty detail was passed":
            return "No detail was given", 404
        elif str(e) == "This detail does not exist":
            return f"Detail {detail} does not exist", 409
        
    return jsonify({"all_details": all_details})

@detail_bp.route("/clear_details", methods=["DELETE"])
def clear_details():
    """Clear all details from the all_details session variable"""
    session["all_details"] = []
    return f"All, if any, details deleted. all_details is now {session["all_details"]}"

@detail_bp.route("/get_base_details", methods=["GET"])
def get_all_base_details():
    """Get the q_details of all nodes with the q_type 'base'"""
    ll = get_ll(current_app)
    base_list=ll.getByQType("base")
    return jsonify({"base_q_details": base_list})

@detail_bp.route("/check_detail/<detail>", methods=["GET"])
def check_detail(detail:str):
    """Check if the given q_detail exists within the list of
    details
    """
    detail:str = unquote(detail)
    details:list[str] = session.get("all_details", [])
    if detail in details:
        return jsonify({"exists":"true", "all_details":details})
    else:
        return jsonify({"exists":"false", "all_details":details})

