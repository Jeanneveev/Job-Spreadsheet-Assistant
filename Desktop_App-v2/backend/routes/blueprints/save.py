"""Blueprints for routes related to saving question groups"""
import os
import re
import json
import sqlite3
from flask import Blueprint, session, request, current_app
from utils.linked_list_handler import get_ll
from werkzeug.utils import secure_filename

save_bp = Blueprint("saves", __name__)

## FILE
def get_preexisting_filenames() -> list[str]:
    """Gets the root filename of all pre-existing question group files
    from the upload folder, and database and returns it as a singular list
    """
    print("reached get_preexisting")
    #get from saves folder
    files_filenames:list[str]=[]
    save_folder=current_app.config["UPLOAD_FOLDER"]
    print(f"save folder is {save_folder}")
    files=os.listdir(save_folder)
    print(f"files are {files}")
    for file in files:
        # print(f"file is {file}")
        if re.match(r"^qg_.*\.json$", file):
            # print("matched")
            file_name=file.removeprefix("qg_").removesuffix(".json")
            files_filenames.append(file_name)
    #     else:
    #         print("didn't match")
    # print(f"files_filenames is {files_filenames}")
    #TODO: Get from database
    db_filenames:list[str]=[]
    #make a combined list with no duplicates
    all_filenames:list[str]=list(set(files_filenames + db_filenames))
    # print(f"all filenames are: {all_filenames}")
    return all_filenames
    
def validate_filename(filename:str):
    """Check that the given filename does not exist within the list
    of existing filenames, and append it to that list if so

    Parameters:
        filename: str - the filename to be checked
    Returns:
        True - A flag representing that filename was not in the list
        and was then appended to it

        False - A flag representing that the filename was in the list
        and was thus not appended to it
    """
    print("validate_filename reached")
    #get the existing filenames from the session variable or from the get_preexisting function
    # if this is the first time this validate function is run
    existing_filenames:list[str]=session.get("filenames",get_preexisting_filenames())
    print(f"existing filenames are {existing_filenames}")
    if filename not in existing_filenames:
        existing_filenames.append(filename)
        session["filenames"]=existing_filenames
        session.modified = True
        return True
    else:
        return False

@save_bp.route("/save_file", methods=["POST"])
def write_ll_to_file():
    """Write all nodes of the linked list to a .json file"""
    ll = get_ll(current_app)
    name:str=request.get_json()["name"]
    print(f"passed name is {name}")
    #convert the given name into a valid filename
    filename=secure_filename(name)
    print(f"secured filename is {filename}")
    if validate_filename(filename): #if the filename is unique
        print(f"filename validated")
        ll_jsonable:list[dict]=ll.getAll()
        curr_dir=os.path.dirname(__file__)
        path=f"Saves/qg_{filename}.json"
        save_path=os.path.join(curr_dir, os.pardir, os.pardir, os.pardir, path)

        with open(save_path,"w+", encoding="utf-8") as file:
            json.dump(ll_jsonable,file,ensure_ascii=False,indent=4)

        return f"Question group saved to {save_path}", 200
    else:
        return f"Name already exists", 400
    
## DATABASE
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
def save_to_database():
    pass