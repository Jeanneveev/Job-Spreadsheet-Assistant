"""Blueprints for routes related to CRUD functionality for questions in a question group"""
import json
from flask import Blueprint, request, session, current_app
from classes import Question, QTypeOptions, ATypeOptions, Node, LinkedList
from utils.linked_list_handler import init_ll, get_ll, override_ll

q_crud_bp = Blueprint("q_crud", __name__)

## CREATE
@q_crud_bp.route("/add_question", methods=["POST"])
def add_question():
    """Add a new question to the question group with the info passed"""
    ll = get_ll(current_app)
    result=request.form
    print("Form is", result)
    #all of the form sections are required, so we don't need to check for NULLs
    # however, we do need to check if base or add-on was selected because they're in their own group
    if "q_type_2" in result:
        q_type=QTypeOptions(result["q_type_2"])
    else:
        q_type=QTypeOptions(result["q_type"])
    a_type=ATypeOptions(result["a_type"])
    #if it's a multiple-choice question, get the choices
    if a_type.value=="multiple-choice":
        print("Creating new multiple-choice question")
        choices:list[str]=json.loads(result["choices"])
        print("Choices are:",choices)
        new_question=Question(result["question"],result["detail"],q_type,a_type,choices)
    elif a_type.value==None:
        return {"response":"A_type not found"}, 404
    else:
        print("Creating new open-ended question")
        new_question=Question(result["question"],result["detail"],q_type,a_type)
    print("Created question:",new_question.q_str)
    new_node=Node(new_question)
    ll.append(new_node)
    ll.printLL()
    if a_type.value=="multiple-choice":
        return {"mult_response": "added question"}
    else:
        return {"response":"added question"}
@q_crud_bp.route("/add_question/addon", methods=["POST"])
def add_addon():
    ll = get_ll(current_app)
    result=request.form
    #make a question from the results
    q_type=QTypeOptions(result["q_type_2"])
    a_type=ATypeOptions(result["a_type"])
    if a_type.value=="multiple-choice":
        print("Creating new multiple-choice question")
        choices:list[str]=json.loads(result["choices"])
        print("Choices are:",choices)
        new_question=Question(result["question"],result["detail"],q_type,a_type,choices)
    else:
        new_question=Question(result["question"],result["detail"],q_type,a_type)
    #get the node of the question this one is adding onto
    base_detail=result["addon_to"]
    base_node=ll.getByDetail(base_detail)
    #set the base's addon value to the addon Question
    base_node.addon=new_question
    print(f"Addon \"{new_question.q_detail}\" added to base node \"{base_node.question.q_detail}\"")
    if a_type.value=="multiple-choice":
        return {"mult_response": "added multiple-choice addon question"}
    else:
        return {"response":"added addon question"}
    
def add_application_date():
    ll = get_ll(current_app)
    # create a Question with an a_type of "preset" where the value is the current date
    new_q=Question("appDate","Application Date",QTypeOptions("singular"),ATypeOptions("preset"))
    new_node=Node(new_q)
    ll.append(new_node)
    print("New preset node appended")
def add_empty_question(i):
    ll = get_ll(current_app)
    #create a preset Question with an empty value for empty columns
    new_q=Question("empty",f"Empty-{i}",QTypeOptions("singular"),ATypeOptions("preset"))
    new_node=Node(new_q)
    ll.append(new_node)
    print("New preset node appended")
@q_crud_bp.route("/add_question/preset", methods=["POST"])
def add_preset():
    value:str=request.get_json()["preset"]
    match value:
        case "appDate":
            add_application_date()
        case "empty":
            empty_cntr=session.get("empty_cntr",0)
            add_empty_question(empty_cntr)
            session["empty_cntr"]=empty_cntr+1
    return f"{value} Question added"

## READ
@q_crud_bp.route("/get_ll_json", methods=["GET"])
def all_to_json():
    """Get every node in the linked list and return them as json"""
    ll:LinkedList = get_ll(current_app)
    # print("Get_ll_json called. Linked list JSON is: ",ll.getAll())
    return {"result":ll.getAll()}

@q_crud_bp.route("/get_questions_exist", methods=["GET"])
def check_ll_exists():
    ll:LinkedList = get_ll(current_app)
    if ll.head == None: #if nothing's in the LinkedList
        return "false"
    else:
        return "true"

## EDIT
@q_crud_bp.route("/reorder_questions", methods=["POST"])
def reorder_nodes():
    """Upon being given an ordered list of node details, reorder the linked list to be in that order"""
    ll = get_ll(current_app)
    ordered_dict:dict=request.get_json()["order"]
    print(f"The ordered dict is {ordered_dict}. It is of type {type(ordered_dict)}")
    print(f"Before reordering, the ll looks like: {ll.returnLL()}")
    new_ll=LinkedList()

    reordered_nodes:list[Node]=[]
    for k,v in ordered_dict.items():
        print("Reordering",v)
        node:Node=ll.getByDetail(v)
        if node is None:
            return "ERROR: Node not found", 404
        reordered_nodes.append(node)
    #append the reordered nodes
    for node in reordered_nodes:
        #NOTE: Clearing the node's pointers here is key, or else it will cause an infinite loop
        node.next=None
        node.prev=None
        new_ll.append(node)
    print(f"new_ll is now {new_ll.returnLL()}")
    # override both local and global ll
    ll=override_ll(current_app, new_ll)
    print(f"After reordering, the ll looks like: {ll.returnLL()}")

    return "Linked List reordered",200

## DELETE
@q_crud_bp.route("/delete_question", methods=["DELETE"])
def del_node():
    """Given a node's detail, find and delete it"""
    ll = get_ll(current_app)
    data=request.get_json()
    if "is_addon" in data:
        is_addon=True
    else:
        is_addon=False
    del_detail:str=request.get_json()["q_detail"]
    print(f"del_detail is {del_detail}")
    if is_addon:
        del_node:Node=ll.getByAddonDetail(del_detail)
    else:
        del_node:Node=ll.getByDetail(del_detail)
    #if the question being deleted is an addon, just delete the addon
    if(del_node.addon):
        if (del_node.addon.q_detail==del_detail):
            del_node.addon=None
            return f"Addon question {del_detail} deleted"
    else:   #otherwise, delete the whole node
        ll.remove(del_node)
        ll.printLL()
        return f"Node {del_detail} deleted"