import os
import re
import json
import sqlite3
import logging
from flask import Blueprint, session, request, current_app
from app.utils.linked_list_handler import get_ll
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

def get_root_filename(filename:str) -> str:
    """Geets the root filename of a question group filename"""
    return filename.removeprefix("qg_").removesuffix(".json")

def get_full_filename(root_name:str) -> str:
    return f"qg_{root_name}.json"

def get_preexisting_filenames() -> list[str]:
    """Gets the root filenames of all pre-existing question group files
    from the upload folder, and database and returns it as a singular list
    """
    logger.info("reached get_preexisting")
    #get from saves folder
    all_filenames:list[str] = []
    save_folder = current_app.config["UPLOAD_FOLDER"]
    logger.info(f"save folder is {save_folder}")
    filenames = os.listdir(save_folder)
    logger.info(f"filenames are {filenames}")
    for filename in filenames:
        # logger.info(f"file is {file}")
        if re.match(r"^qg_.*\.json$", filename):
            # logger.info("matched")
            root_name = get_root_filename(filename)
            all_filenames.append(root_name)
    logger.info(f"all_filenames is {all_filenames}")

    return all_filenames

def is_unique_filename(filename:str):
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
    logger.info("validate_filename reached")
    #get the existing filenames from the session variable or from the get_preexisting function,
    # if this is the first time this validate function is run
    existing_filenames:list[str] = session.get("filenames", get_preexisting_filenames())
    logger.info(f"existing filenames are {existing_filenames}")
    if filename not in existing_filenames:
        existing_filenames.append(filename)
        session["filenames"] = existing_filenames
        session.modified = True
        return True
    else:
        return False
    
def write_ll_to_file(name:str):
    root_filename = secure_filename(name) # convert the given name into a valid filename
    # logger.info(f"secured filename is {filename}")
    ll = get_ll(current_app)
    
    if is_unique_filename(root_filename): # if the filename is unique
        logger.info(f"filename validated")
        full_filename = get_full_filename(root_filename)
        curr_dir = os.path.dirname(__file__)
        path = f"Saves/{full_filename}"
        save_path = os.path.join(curr_dir, os.pardir, os.pardir, os.pardir, path)
        ll_jsonable:list[dict] = ll.getAll()

        with open(save_path, "w+", encoding="utf-8") as file:
            json.dump(ll_jsonable, file, ensure_ascii=False, indent=4)

        return f"Question group saved to {save_path}"
    else:
        raise ValueError("Name already exists")
