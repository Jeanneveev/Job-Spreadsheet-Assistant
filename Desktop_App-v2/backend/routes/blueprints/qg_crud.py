"""Blueprints for routes related to CRUD functionality for question groups (qg(s))"""
import json
from flask import Blueprint, request, session, current_app
from classes import Question, QTypeOptions, ATypeOptions, Node, LinkedList
from utils.linked_list_handler import init_ll, get_ll, override_ll

qg_crud_bp = Blueprint("qg_crud", __name__)

##READ
@qg_crud_bp.route("/get_created_qg", methods=["GET"])
def get_created_qg_display_data():
    """Get the display data of a qg created in the 'viewQuestions' page"""
    qg:LinkedList = get_ll(current_app)
    qg_name:str = "Working QG"
    qg_date:str = "Not Saved"
    num_q:int = qg.getQNum()
    return {"result":json.dumps([qg_name,qg_date,num_q])}

# def get_uploaded_qg_display_data():
#     qg:LinkedList = 