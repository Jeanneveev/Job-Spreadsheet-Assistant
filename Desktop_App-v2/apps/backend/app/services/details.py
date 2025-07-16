import logging
from flask import session
from app.models import Question, Node, LinkedList
from app.services.answer_form import get_current_question

logger = logging.getLogger(__name__)

def add_detail_to_all_details(new_detail:str) -> list[str]:
    if new_detail == "":
        raise ValueError("Empty detail was passed")
    existing_details = session.get("all_details", [])
    if new_detail in existing_details:
        raise ValueError("This detail already exists")
    
    all_details = existing_details
    all_details.append(new_detail)
    session["all_details"] = all_details
    session.modified = True

    return all_details

def remove_detail_from_all_details(old_detail:str) -> list[str]:
    if old_detail == "":
        raise ValueError("Empty detail was passed")
    existing_details = session.get("all_details", [])
    if old_detail not in existing_details:
        raise ValueError("This detail does not exist")
    
    existing_details.remove(old_detail)
    session["all_details"] = existing_details
    session.modified = True

    return existing_details
