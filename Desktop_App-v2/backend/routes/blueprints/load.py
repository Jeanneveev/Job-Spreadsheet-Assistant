"""Blueprints for routes related to loading and uploading
question groups
"""
import os
from jsonschema import validate
from flask import Blueprint, request, current_app, session
from classes import Question, QTypeOptions, ATypeOptions, Node
from utils.linked_list_handler import get_ll
from werkzeug.utils import secure_filename
import json

load_bp = Blueprint("load", __name__)

#double-checking extensions since the "accepts" attribute can be bypassed
def check_allowed_extension(filename):
    ALLOWED_EXTENSIONS=[".json"]
    extension=os.path.splitext(filename)[1]
    # print(f"Extension is: {extension}")
    if extension in ALLOWED_EXTENSIONS:
        print("File's extension allowed")
        return True
    else:
        print("Incorrect file extension")
        return False
    
def validate_upload(file_json):
    """Given JSON of a file, confirm that it's in the right format to be turned into a LinkedList object"""
    schema={
        "type":"array",
        "items": {
            "type":"object",
            "properties": {
                "question": {
                    "type":"object",
                    "properties": {
                        "q_str": {"type":"string"},
                        "q_detail": {"type":"string"},
                        "q_type": {"type":"string"},
                        "a_type": {"type":"string"},
                        "choices": {"type":"array"}
                    },
                    "required":["q_str","q_detail","q_type","a_type"]
                },
                "addon": {
                    "type":"object",
                    "properties": {
                        "q_str": {"type":"string"},
                        "q_detail": {"type":"string"},
                        "q_type": {"type":"string"},
                        "a_type": {"type":"string"},
                        "choices": {"type":"array"}
                    },
                    "required":["q_str","q_detail","q_type","a_type"]
                },
                "answer": {
                    "type":"string"
                },
            },
            "required":["question"]
        }
    }
    try:
        validate(instance=file_json, schema=schema)
    except:
        return False
    print("file validated")
    return True

def load_details_from_file(file_json:list[dict]):
    """Add the details from an uploaded linked list into the
    'detail_lst' session variable
    """
    detail_lst=session.get("detail_lst",json.dumps([]))
    detail_lst:list[str] = json.loads(detail_lst)
    for obj in file_json:
        q_info:dict = obj["question"]
        q_detail:str = q_info["q_detail"]
        print(f"loading q_detail: {q_detail}")
        detail_lst.append(q_detail)
    session['detail_lst'] = json.dumps(detail_lst)
    session.modified = True

def load_ll_from_file(file_json:list[dict]):
    """Load new linked list from a saved file's JSON"""
    ll = get_ll(current_app)
    # clear old linked list
    ll.clear()
    # parse JSON into new linked list
    for node in file_json:
        question=node["question"]
        q_type=QTypeOptions(question["q_type"])
        a_type=ATypeOptions(question["a_type"])
        new_question=None
        if "choices" in question:
            new_question=Question(question["q_str"],question["q_detail"],q_type,a_type,question["choices"])
        else:
            new_question=Question(question["q_str"],question["q_detail"],q_type,a_type)
        new_node=Node(new_question)
        #if there's an addon, make a Question out of it and add it to the new node
        if "addon" in node:
            addon=node["addon"]
            addon_q_type=QTypeOptions(addon["q_type"])
            addon_a_type=ATypeOptions(addon["a_type"])
            new_addon=None
            if "choices" in addon:
                new_addon=Question(addon["q_str"],addon["q_detail"],addon_q_type,addon_a_type,addon["choices"])
            else:
                new_addon=Question(addon["q_str"],addon["q_detail"],addon_q_type,addon_a_type)
            new_node.addon=new_addon
        ll.append(new_node)
    #add the newly appended question's q_details to the session variable
    load_details_from_file(file_json)

@load_bp.route("/upload_file", methods=["GET","POST"])
def upload_file():
    """Upload a file given by the user to the Saves folder"""
    if request.method=="POST":
        if "file" not in request.files:
            return "ERROR: No file in request", 404
        file=request.files["file"]
        if file.filename=="":
            return "ERROR: No selected file", 404
        
        file_json:list[dict]=json.load(file)   #this puts the file stream pointer at the end
        file.seek(0)    #reset file pointer to the start
        # print(f"File is: {file_json}. Filename is: {file.filename}")
        # if the file exists and it's of the right extension in the right format
        if file and check_allowed_extension(file.filename):
            if validate_upload(file_json):
                file.seek(0)    #reset file pointer to the start (validate should have put it at the end again)
                filename = secure_filename(file.filename)
                upload_folder=current_app.config.get("UPLOAD_FOLDER")

                file_path=os.path.join(upload_folder,filename)
                file.save(file_path)    #save as a local file
                load_ll_from_file(file_json)    #save in the linked list
                return "File saved", 201
            else:
                return "Wrong file format", 400
        else:
            return "File exists but wasn't uploaded", 409
