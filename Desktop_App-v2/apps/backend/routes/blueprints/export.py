"""Blueprints for routes related to exporting data from the app into
another form
"""
import os
from flask import Blueprint, request, current_app
from ...utils.export_data_handler import get_exportdata
from ..blueprints import answer_form

export_bp = Blueprint("export", __name__)

@export_bp.route("/set_export_method",methods=["POST"])
def set_export_method():
    method:str = request.data.decode("utf-8")
    exportData = get_exportdata(current_app)
    exportData.method=method
    return f"Method {exportData.method} set"
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
    print(f"Answers {exportData.data} added")
    return f"Answers {exportData.data} added"

@export_bp.route("/get_auth_url",methods=["GET"])
def get_auth_url():
    exportData = get_exportdata(current_app)
    url=exportData.get_auth_url()
    if url:
        print("auth_url is ",url)
        return {"auth_url":url}
    else:
        print("Credentials are already validated")
        return {"message": "Credentials are already validated"}, 200

@export_bp.route("/auth_landing_page/",methods=["GET"])
def auth_landing_page():
    """The page the Google Sheets authorization process lands on after
        a successful login. Includes the auth_code in its parameters
    """
    return "You reached the landing page! You can close this window now."

@export_bp.route("/receive_auth_code",methods=["POST"])
def receive_auth_code():
    exportData = get_exportdata(current_app)
    code=request.get_json()["code"]
    service=exportData.get_service(code)
    print(f"service is: {service}")
    if type(service)==dict: #it's an error
        return service  #return that error message
    else:
        return {"success_message":"Authentification successful and connection built"}

@export_bp.route("/export_data/sheets",methods=["POST"])
def export_data_sheets():
    exportData = get_exportdata(current_app)
    export_result=exportData.export_to_sheets()
    print("export_result is",export_result)
    if type(export_result) is tuple:
        error_code=export_result[1]
        export_result=export_result[0]
    if export_result.get("error",None) is None:
        res_msg:str=f"{(export_result.get('updates').get('updatedCells'))} cells appended."
        return res_msg
    else:
        return f"ERROR!!! {export_result.get('error')}",error_code