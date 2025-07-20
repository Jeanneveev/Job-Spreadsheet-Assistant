"""Blueprints for routes related to saving question groups"""
import os
import re
import json
import sqlite3
import logging
from flask import Blueprint, session, request, current_app
from ...utils.linked_list_handler import get_ll
from werkzeug.utils import secure_filename
from ...services import is_unique_filename, write_ll_to_file

logger = logging.getLogger(__name__)
save_bp = Blueprint("saves", __name__)

## FILE
@save_bp.route("/save_file", methods=["POST"])
def save_file():
    """Write all nodes of the linked list to a .json file"""
    name:str=request.get_json()["name"]
    logger.info(f"passed name is {name}")
    try:
        confirmation_msg = write_ll_to_file(name)
    except ValueError as e:
        return str(e), 409
    
    return confirmation_msg
    
## DATABASE
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
def save_to_database():
    pass