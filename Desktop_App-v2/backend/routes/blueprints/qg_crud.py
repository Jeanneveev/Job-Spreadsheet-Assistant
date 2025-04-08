"""Blueprints for routes related to CRUD functionality for question groups (qg(s))"""
import json
from flask import Blueprint, request, session, current_app
from classes import Question, QTypeOptions, ATypeOptions, Node, LinkedList
from utils.linked_list_handler import init_ll, get_ll, override_ll

qg_crud_bp = Blueprint("qg_crud", __name__)

##VIEW
def get_created_question_group():
    """Get the display data of a qg created in the 'viewQuestions' page"""
    created_qg:LinkedList = get_ll(current_app)
    # qg_date = 