"""Blueprints for routes related to exporting data from the app into
another form
"""
import os
import logging
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from ...utils.export_data_handler import get_export_data
from ...utils.linked_list_handler import get_ll
from ...models import LinkedList
from ...services import (get_all_answers, set_export_method,
    get_service_from_auth_url_str, export_data_to_sheets, set_new_export_csv, set_old_export_csv)

logger = logging.getLogger(__name__)
export_bp = Blueprint("export", __name__)

@export_bp.route("/set_export_method", methods=["POST"])
def set_export_data_method():
    method:str = request.data.decode("utf-8")
    try:
        set_method = set_export_method(method)
    except ValueError as e:
        return str(e), 409
    
    return f"Method: {set_method} set"

@export_bp.route("/set_export_loc", methods=["POST"])
def set_export_loc():
    """Given a form containing the name of the CSV to export and whether it is a new or
    pre-existing CSV, upload it to the UPLOAD_FOLDER, if necessary, and set its path to
    the app's ExportData instance
    """
    form = request.form
    new_or_old = request.form["csvOpt"]

    if "new" in new_or_old:
        try:
            path = set_new_export_csv(form)
        except FileExistsError as e:
            return str(e), 409
    elif "old" in new_or_old:
        try:
            path = set_old_export_csv(request.files)
        except FileNotFoundError as e:
            return str(e), 409
    
    export_data = get_export_data(current_app)
    export_data.loc = path

    return "Export location set"

@export_bp.route("/get_export_method", methods=["GET"])
def get_export_method():
    export_data = get_export_data(current_app)
    return f"{export_data.method}"

@export_bp.route("/set_answers_to_export", methods=["POST"])
def set_answers_to_export():
    exportData = get_export_data(current_app)
    ll:LinkedList = get_ll(current_app)
    answs = get_all_answers(ll)
    exportData.data = answs
    logger.info(f"Answers {exportData.data} added")
    return f"Answers {exportData.data} added"

@export_bp.route("/set_sheet_id", methods=["POST"])
def set_sheets_id():
    sheet_id:str = request.data.decode("utf-8")
    exportData = get_export_data(current_app)
    try:
        message = exportData.set_sheet_id(sheet_id)
        current_app.logger.info(f"sheet id is: {exportData.sheet_id}")
        return message  # "Sheet exists and is accessible"
    except Exception as e:
        print(str(e))
        return str(e), 409

@export_bp.route("/get_auth_url", methods=["GET"])
def get_auth_url():
    exportData = get_export_data(current_app)
    url = exportData.get_auth_url()
    if url:
        logger.info(f"auth_url is {url}")
        return {"auth_url": url}
    else:
        logger.info("Credentials are already validated")
        return {"message": "Credentials are already validated"}, 200

@export_bp.route("/auth_landing_page/", methods=["GET"])
def auth_landing_page():
    """The page the Google Sheets authorization process lands on after
        a successful login. Includes the auth_code in its parameters.
        This code is then passed to the ExportData instance to generate a token.json file
        if one doesn't already exist.
    """
    current_app.logger.info("API /auth_landing_page called")

    url_str:str = request.url   #get the full url, params included
    try:
        get_service_from_auth_url_str(url_str)
    except ValueError as e:
        return "Could not get service from url", 409

    return "You reached the landing page! You can close this window now."

@export_bp.route("/export_data/sheets", methods=["POST"])
def export_sheets():
    try:
        result_msg = export_data_to_sheets()
    except Exception as e:
        return str(e), 401
    
    return result_msg