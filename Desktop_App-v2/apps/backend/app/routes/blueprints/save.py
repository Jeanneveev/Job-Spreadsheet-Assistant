"""Blueprints for routes related to saving question groups"""
# import sqlite3
import logging
from flask import Blueprint, session, request, current_app
from ...models import LinkedList
from ...utils.linked_list_handler import get_ll
from ...services import write_ll_to_file

logger = logging.getLogger(__name__)
save_bp = Blueprint("saves", __name__)

## FILE
@save_bp.route("/save_file", methods=["POST"])
def save_file():
    """Write all nodes of the linked list to a .json file"""
    name:str = request.data.decode("utf-8")
    logger.info(f"passed name is {name}")
    ll:LinkedList = get_ll(current_app)
    try:
        confirmation_msg = write_ll_to_file(ll, name)
    except ValueError as e:
        return str(e), 409
    
    return confirmation_msg
    
## DATABASE
# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn
# def save_to_database():
#     pass