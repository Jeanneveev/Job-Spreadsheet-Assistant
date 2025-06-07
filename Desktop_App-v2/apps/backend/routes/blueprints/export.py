"""Blueprints for routes related to exporting data from the app into
another form
"""
import os
import logging
from flask import Blueprint, request, current_app, session
from urllib.parse import parse_qs, urlparse
from ...utils.export_data_handler import get_exportdata
from . import answer_form

logger = logging.getLogger(__name__)
export_bp = Blueprint("export", __name__)

@export_bp.route("/set_export_method",methods=["POST"])
def set_export_method():
    current_app.logger.info("API /set_export_method called")

    method:str = request.data.decode("utf-8")
    exportData = get_exportdata(current_app)
    exportData.method=method
    return f"Method: {exportData.method} set"
@export_bp.route("/set_export_loc",methods=["POST"])
def set_export_loc():
    exportData = get_exportdata(current_app)
    upload_folder=current_app.config.get("UPLOAD_FOLDER")
    file_path=os.path.join(upload_folder,"CSV")
    ### TODO: Replace with the passed filename later
    full_file_path=os.path.join(file_path,"example.csv")
    exportData.loc=full_file_path
    return f"Filepath set as {full_file_path}"
@export_bp.route("/get_export_method",methods=["GET"])
def get_export_method():
    exportData = get_exportdata(current_app)
    return f"{exportData.method}"
@export_bp.route("/add_all_answers",methods=["POST"])
def add_all_answers():
    exportData = get_exportdata(current_app)
    answs=answer_form.get_all_answers_handler(by_route=False)
    exportData.data=answs
    logger.info(f"Answers {exportData.data} added")
    return f"Answers {exportData.data} added"

@export_bp.route("/set_sheet_id", methods=["POST"])
def set_sheets_id():
    current_app.logger.info("API /set_sheets_id called")

    sheet_id:str = request.data.decode("utf-8")
    exportData = get_exportdata(current_app)
    try:
        message = exportData.set_sheet_id(sheet_id)
        return message  #"Sheet exists and is accessible"
    except Exception as e:
        return f"{e}", 401

@export_bp.route("/get_auth_url", methods=["GET"])
def get_auth_url():
    current_app.logger.info("API /get_auth_url called")

    exportData = get_exportdata(current_app)
    url=exportData.get_auth_url()
    if url:
        logger.info(f"auth_url is {url}")
        return {"auth_url":url}
    else:
        logger.info("Credentials are already validated")
        return {"message": "Credentials are already validated"}, 200

@export_bp.route("/auth_landing_page/",methods=["GET"])
def auth_landing_page():
    """The page the Google Sheets authorization process lands on after
        a successful login. Includes the auth_code in its parameters.
        This code is then passed to the ExportData instance to generate a token.json file
        if one doesn't already exist.
    """
    current_app.logger.info("API /auth_landing_page called")

    url_str:str = request.url   #get the full url, params included
    url = urlparse(url_str)
    code = parse_qs(url.query)["code"][0]
    # Use the code to get credentials to write to token.json
    exportData = get_exportdata(current_app)
    service=exportData.get_service(code)
    logger.info(f"service is: {service}")
    if type(service)==dict: #it's an error
        logger.info("Error: ",service)  #print that error message
    else:
        logger.info("Authentification successful and connection built")

    return "You reached the landing page! You can close this window now."

@export_bp.route("/export_data/sheets",methods=["POST"])
def export_data_sheets():
    exportData = get_exportdata(current_app)
    export_result=exportData.export_to_sheets()
    logger.info("export_result is",export_result)
    if type(export_result) is tuple:
        error_code=export_result[1]
        export_result=export_result[0]
    if export_result.get("error",None) is None:
        res_msg:str=f"{(export_result.get('updates').get('updatedCells'))} cells appended."
        return res_msg
    else:
        return f"ERROR!!! {export_result.get('error')}",error_code