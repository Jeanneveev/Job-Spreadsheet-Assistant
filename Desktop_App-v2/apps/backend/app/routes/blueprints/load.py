"""Blueprints for routes related to loading and uploading
question groups
"""
import os
import logging
from flask import Blueprint, request, current_app, session, jsonify
from ...services import (check_allowed_extension, validate_upload,
    load_ll_and_details, get_working_qg_info, get_files_display_info)
from ...utils.linked_list_handler import get_ll
from werkzeug.utils import secure_filename
import json
import time

logger = logging.getLogger(__name__)
load_bp = Blueprint("load", __name__)

@load_bp.route("/upload_file", methods=["POST"])
def upload_file():
    """Upload a file given by the user to the Saves folder"""
    if "file" not in request.files:
        return "ERROR: No file in request", 404
    file = request.files["file"]
    if file.filename == "":
        return "ERROR: No file selected", 404
    
    # if the file exists and it's of the right extension in the right format
    if file and check_allowed_extension(file.filename):
        file_json:list[dict] = json.load(file)   #this puts the file stream pointer at the end
        file.seek(0)    #reset file pointer to the start
        # logger.info(f"File is: {file_json}. Filename is: {file.filename}")
        
        if validate_upload(file_json):
            file.seek(0)    #reset file pointer to the start (validate should have put it at the end again)
            filename = secure_filename(file.filename)
            upload_folder = current_app.config.get("UPLOAD_FOLDER")

            # save as a local file
            file_path=os.path.join(upload_folder, filename)
            file.save(file_path)

            ll = get_ll(current_app)
            msg = load_ll_and_details(ll, file_json)    #save in the linked list
            return f"File saved. {msg}", 200
        else:
            return "ERROR: Wrong file format", 409
    else:
        return "ERROR: Wrong file type", 409

## LOAD CURRENT
@load_bp.route("/get_working_qg_info", methods=["GET"])
def get_created_qg():
    """Get the info of an unsaved question group created this session"""
    qg = get_ll(current_app)
    display_info:list = get_working_qg_info(qg)
    return jsonify({"display_info": display_info}), 200

## LOAD ALL
@load_bp.route("/load_all_files", methods=["GET"])
def format_preexisting_qgs_display_info():
    """Get the file display info of all valid question group file in the
    upload folder"""
    all_results = get_files_display_info()
    display_infos = []
    for result in all_results:
        logger.info(f"qg display details is: {result}")
        display_infos.append(result)
    return jsonify({"files_display_info": display_infos})

@load_bp.route("/update_selected_qg", methods=["POST"])
def update_selected_qg():
    """Given the name of the selected qg, load its JSON file and update
    the linked list"""
    qg_name:str = request.data.decode("utf-8")
    ll = get_ll(current_app)

    filename = f"qg_{qg_name}.json"
    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    path = os.path.join(upload_folder, filename)
    with open(path, "r") as f:
        file_json = json.load(f)
        f.seek(0)
        _ = load_ll_and_details(ll, file_json)
    return f"Switched qg to {qg_name}"