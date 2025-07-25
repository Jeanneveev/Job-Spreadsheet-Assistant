import json
import logging
from flask import session, current_app
from app.models import LinkedList, Node, Question, QTypeOptions, ATypeOptions

logger = logging.getLogger(__name__)

def get_question_from_form(form_data:dict):
    q_str:str = form_data["q_str"]
    q_detail:str = form_data["q_detail"]
    if "q_type_2" in form_data:
        q_type = QTypeOptions(form_data["q_type_2"])
    else:
        q_type = QTypeOptions(form_data["q_type"])
    a_type = ATypeOptions(form_data["a_type"])
    # if it's a multiple-choice question, get the options
    if a_type.value == "multiple-choice":
        logger.info("Creating new multiple-choice question")
        options:list[str] = json.loads(form_data["options"])
        # logger.info("options are:",options)
        new_question = Question(q_str, q_detail, q_type, a_type, options)
    else:
        logger.info("Creating new open-ended question")
        new_question = Question(q_str, q_detail, q_type, a_type)
    logger.info("Created question:", new_question.q_str)

    return new_question

def add_application_date(ll:LinkedList):
    """create a Question with an a_type of "preset" where the value is the current date"""
    return Question("appDate", "Application Date", QTypeOptions("singular"), ATypeOptions("preset"))
def add_empty_question(ll:LinkedList, i):
    """create a preset Question with an empty value for empty columns"""
    return Question("empty", f"Empty-{i}", QTypeOptions("singular"), ATypeOptions("preset"))
    
def add_preset(ll:LinkedList, name:str):
    match name:
        case "appDate":
            new_question = add_application_date(ll)
        case "empty":
            empty_idx = session.get("empty_cntr", 0)
            new_question = add_empty_question(ll, empty_idx)
            session["empty_cntr"] = empty_idx + 1
        case _:
            raise ValueError(f'Preset "{name}" not found')
        
    logger.info("New preset node appended")
    new_node = Node(new_question)
    ll.append(new_node)

    return new_question.q_str

def get_reordered_ll(old_ll:LinkedList, new_order:list):
    new_ll = LinkedList()
    reordered_nodes:list[Node] = []

    for q_detail in new_order:
        logger.info("Reordering", q_detail)
        node:Node = old_ll.getByDetail(q_detail)
        if node is None:
            raise ValueError("Node not found")
        reordered_nodes.append(node)
    # add the reordered nodes to the new_ll
    for node in reordered_nodes:
        #NOTE: Clearing the node's pointers here is important, or else it will cause an infinite loop
        node.next = None
        node.prev = None
        new_ll.append(node)
    # logger.info(f"new_ll is now {new_ll.returnLL()}")
    return new_ll

def delete_question_or_node(ll:LinkedList, q_detail:str, is_addon:bool):
    logger.info(f"Deleting {q_detail}")
    if is_addon:
        del_node:Node = ll.getByAddonDetail(q_detail)
        if not del_node:
            raise ValueError("Question not found")
        del_node.addon = None
        return f'Addon question "{q_detail}" deleted'
    else:
        del_node:Node = ll.getByDetail(q_detail)
        if not del_node:
            raise ValueError("Question not found")
        ll.remove(del_node)
        return f'Node "{q_detail}" deleted'