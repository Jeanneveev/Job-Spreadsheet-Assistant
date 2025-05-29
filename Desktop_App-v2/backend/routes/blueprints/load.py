"""Blueprints for routes related to loading and uploading
question groups
"""
from typing import Generator, Any
import os
from jsonschema import validate
from flask import Blueprint, request, current_app, session
from ...classes import Question, QTypeOptions, ATypeOptions, Node, LinkedList
from ..shared_func import get_preexisting_filenames
from ...utils.linked_list_handler import get_ll
from werkzeug.utils import secure_filename
import json
import time
from datetime import datetime

load_bp = Blueprint("load", __name__)

## LOAD INDIVIDUAL
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
    session['detail_lst'] = json.dumps([])  #set/reset session variable
    detail_lst:list[str] = []
    for obj in file_json:
        q_info:dict = obj["question"]
        q_detail:str = q_info["q_detail"]
        print(f"loading q_detail: {q_detail}")
        detail_lst.append(q_detail)
    session['detail_lst'] = json.dumps(detail_lst)
    session.modified = True

def load_ll_from_file_json(file_json:list[dict]):
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

@load_bp.route("/upload_file", methods=["POST"])
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
                load_ll_from_file_json(file_json)    #save in the linked list
                return "File saved", 201
            else:
                return "Wrong file format", 400
        else:
            return "File exists but wasn't uploaded", 409

## LOAD CURRENT
@load_bp.route("/get_created_qg", methods=["GET"])
def get_created_qg_display_data():
    """Get the display data of a qg created in the 'viewQuestions' page"""
    qg:LinkedList = get_ll(current_app)
    qg_name:str = "Working QG"
    qg_date:str = datetime.today().strftime("%m/%d/%Y")
    num_q:int = qg.getQNum()
    return {"result":json.dumps([qg_name,qg_date,num_q])}

## LOAD ALL
def find_valid_files()->list[str]:
    """Locate all uploadable files in the upload folder
    that contain valid JSON and have unique names

    Returns:
        valid_files (list[str]): a list of all the valid file paths
    """

    # get the roots of all files in the UPLOAD_FOLDER with the right naming convention
    existing_root_filenames:list[str] = get_preexisting_filenames()
    valid_files=[]
    # read and validate each filename's JSON
    for root_filename in existing_root_filenames:
        filename:str = "qg_"+root_filename+".json"
        upload_folder=current_app.config.get("UPLOAD_FOLDER")
        path = os.path.join(upload_folder, filename)
        with open(path, "r") as f:
            file_json=json.load(f)
            f.seek(0)
            if validate_upload(file_json):
                valid_files.append(path)
    return list(set(valid_files))

def get_num_questions(file_json:list[dict]):
    """Get the number of questions in a JSON file of a question group

    Parameters:
        file_json (list[dict]): The JSON reprentation of a question group
    Returns:
        num_questions (int): The number of Questions in file_json
    """
    num_questions = 0
    for node in file_json:
        for question, _ in node.items():
            num_questions += 1
    return num_questions

def get_files_display_info()->Generator[list,Any,None]:
    """Gets the display info of all valid files in the upload folder
    
    Returns:
        A Generator of a list of each valid file's display info
    """
    valid_file_paths = find_valid_files()
    for path in valid_file_paths:
        filename:str = os.path.basename(path)
        name:str=filename.removeprefix("qg_").removesuffix(".json")
        last_edited:str = time.strftime("%m/%d/%Y", time.gmtime(os.path.getmtime(path)))
        with open(path, "r") as f:
            file_json:list[dict]=json.load(f)
            f.seek(0)
            num_q:int = get_num_questions(file_json)
            yield [name, last_edited, num_q]

@load_bp.route("/load_all_files", methods=["GET"])
def format_preexisting_qgs_display_info():
    """Format the display of all valid question group file in the
    upload folder"""
    all_results=get_files_display_info()
    formatted=[]
    for result in all_results:
        print(f"qg display details is: {result}")
        formatted.append(result)
    return json.dumps(formatted)

@load_bp.route("/update_selected_qg", methods=["POST"])
def update_selected_qg():
    """Given the name of the selected qg, load its JSON file and update
    the linked list"""
    qg_name:str = request.data.decode("utf-8")
    filename = f"qg_{qg_name}.json"
    upload_folder=current_app.config.get("UPLOAD_FOLDER")
    path = os.path.join(upload_folder, filename)
    with open(path, "r") as f:
        file_json=json.load(f)
        f.seek(0)
        load_ll_from_file_json(file_json)
    return f"Switched qg to {qg_name}"