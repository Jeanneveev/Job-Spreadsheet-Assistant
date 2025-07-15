import logging
from flask import session
from app.models import Question, Node, LinkedList
from app.services.answer_form import get_current_question

logger = logging.getLogger(__name__)

def add_options_to_question(options:list[str], question:Question=None) -> list[str]:
    if not question:
        question:Question = get_current_question()
        
    curr_question_options:list[str] = question.options
    curr_question_options.extend(options)
    curr_question_options = list(dict.fromkeys(curr_question_options))  #remove duplicates
    question.options = curr_question_options
    session["curr_options"] = curr_question_options
    session.modified = True
    return curr_question_options

def add_new_options_to_all_options(new_options:list[str]) -> list[str]:
    all_options = session.get("all_options", [])
    logger.debug(f"pre-existing options are: {all_options}")
    all_options.extend(new_options)
    all_options = list(dict.fromkeys(all_options))    #remove duplicates
    session["all_options"] = all_options
    session.modified = True
    return all_options


