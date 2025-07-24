from typing import Generator, Any
import os
import json
import logging
import time
from datetime import datetime
from jsonschema import validate
from flask import session, current_app
from app.models import Question, QTypeOptions, ATypeOptions, Node, LinkedList
from app.services import get_preexisting_filenames, get_root_filename

logger = logging.getLogger(__name__)

def check_allowed_extension(filename:str) -> bool:
    ALLOWED_EXTENSIONS = [".json"]
    extension = os.path.splitext(filename)[1]
    # logger.info(f"Extension is: {extension}")
    if extension in ALLOWED_EXTENSIONS:
        logger.info("Correct file extension")
        return True
    else:
        logger.info("Incorrect file extension")
        return False
    
def validate_upload(loaded_json):
    """Given JSON of a file, confirm that it's in the right format to be turned into a LinkedList object"""
    schema = {
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
                        "options": {"type":"array"}
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
                        "options": {"type":"array"}
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
        validate(instance=loaded_json, schema=schema)
    except:
        return False
    logger.info("file validated")
    return True

def load_details(loaded_json:list[dict]):
    """Add the details from an uploaded linked list into the
    "all_details" session variable
    """
    session["all_details"] = []  #set/reset session variable
    
    details:list[str] = []
    for obj in loaded_json:
        for key in obj.keys():
            if key == "question":
                q_info:dict = obj["question"]
            if key == "addon":
                q_info:dict = obj["addon"]
            q_detail:str = q_info["q_detail"]
            logger.info(f"loading q_detail: {q_detail}")
            details.append(q_detail)
    session["all_details"] = details
    session.modified = True

    return details

def load_ll(ll:LinkedList, loaded_json:list[dict]):
    """Load new linked list from a saved file's loaded JSON"""
    ll.clear()  # clear old linked list
    # parse loaded JSON into new linked list
    for node in loaded_json:
        question=node["question"]
        q_type=QTypeOptions(question["q_type"])
        a_type=ATypeOptions(question["a_type"])
        new_question=None
        if "options" in question:
            new_question=Question(question["q_str"],question["q_detail"],q_type,a_type,question["options"])
        else:
            new_question=Question(question["q_str"],question["q_detail"],q_type,a_type)
        new_node=Node(new_question)
        #if there's an addon, make a Question out of it and add it to the new node
        if "addon" in node:
            addon=node["addon"]
            addon_q_type=QTypeOptions(addon["q_type"])
            addon_a_type=ATypeOptions(addon["a_type"])
            new_addon=None
            if "options" in addon:
                new_addon=Question(addon["q_str"],addon["q_detail"],addon_q_type,addon_a_type,addon["options"])
            else:
                new_addon=Question(addon["q_str"],addon["q_detail"],addon_q_type,addon_a_type)
            new_node.addon=new_addon
        ll.append(new_node)
    return ll

def load_ll_and_details(old_ll:LinkedList, loaded_json:list[dict]):
    _ = load_ll(old_ll, loaded_json)
    details = load_details(loaded_json)

    return f"Loaded questions: {details}"
    
def get_working_qg_info(qg:LinkedList):
    qg_name:str = "Working QG"
    qg_date:str = datetime.today().strftime("%m/%d/%Y")
    num_q:int = qg.getQNum()
    return [qg_name, qg_date, num_q]

def get_all_valid_file_paths()->list[str]:
    """Get the file paths of all JSON files with unique names and valid formatting in the upload folder

    Returns:
        valid_files (list[str]): a list of all the valid file paths
    """

    # get the names of all files in the UPLOAD_FOLDER with the right naming convention
    existing_root_filenames:list[str] = get_preexisting_filenames()
    valid_files = []
    # read and validate each filename's JSON
    for root_filename in existing_root_filenames:
        filename = "qg_" + root_filename + ".json"
        upload_folder = current_app.config.get("UPLOAD_FOLDER")
        path = os.path.join(upload_folder, filename)
        with open(path, "r") as f:
            file_json = json.load(f)
            f.seek(0)
            if validate_upload(file_json):
                valid_files.append(path)
    return list(set(valid_files))

def get_loaded_num_questions(loaded_json:list[dict]):
    """Get the number of questions in a loaded JSON file of a question group

    Parameters:
        loaded_json (list[dict]): The loaded JSON from a valid file
    Returns:
        num_questions (int): The number of Questions in loaded_json
    """
    num_questions = 0
    for obj in loaded_json:
        for key in obj.keys():
            if key == "question":
                num_questions += 1
            if key == "addon":
                num_questions += 1
    return num_questions

def get_files_display_info() -> Generator[list,Any,None]:
    """Gets the display info of all valid files in the upload folder
    
    Returns:
        A Generator of a list of each valid file's display info
    """
    valid_file_paths = get_all_valid_file_paths()
    for path in valid_file_paths:
        filename:str = os.path.basename(path)
        name:str = get_root_filename(filename)
        last_edited:str = time.strftime("%m/%d/%Y", time.gmtime(os.path.getmtime(path)))
        with open(path, "r") as f:
            file_json:list[dict] = json.load(f)
            f.seek(0)
            num_q:int = get_loaded_num_questions(file_json)
            yield [name, last_edited, num_q]