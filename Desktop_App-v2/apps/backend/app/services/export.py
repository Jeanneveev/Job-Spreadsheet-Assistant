import os
import logging
from urllib.parse import parse_qs, urlparse
from flask import current_app
from werkzeug.datastructures import FileStorage
from app.utils.export_data_handler import get_export_data

logger = logging.getLogger(__name__)

def set_export_method(method:str) -> str:
    if method.lower() not in ["csv", "sheets"]:
        raise ValueError("Invalid method value")
    
    export_data = get_export_data(current_app)
    export_data.method = method
    return export_data.method

def get_service_from_auth_url_str(url_str:str):
    url = urlparse(url_str)
    code = parse_qs(url.query)["code"][0]
    # Use the code to get credentials to write to token.json
    exportData = get_export_data(current_app)
    service = exportData.get_service(code)
    logger.info(f"service is: {service}")
    if type(service) == dict: #it's an error
        logger.info("Error: ", service)  #print that error message
        raise ValueError(service)
    else:
        logger.info("Authentification successful and connection built")

def export_data_to_sheets():
    logger.info("export_data_to_sheets reached")
    exportData = get_export_data(current_app)
    export_result = exportData.export_to_sheets()
    logger.info(f"export_result is {export_result}")
    if type(export_result) is tuple:
        export_result = export_result[0]
    if export_result.get("error", None) is None: # if no errors, update it
        res_msg:str = f"{(export_result.get('updates').get('updatedCells'))} cells appended."
        return res_msg
    else:
        raise Exception(f"{export_result.get('error')}")
    
def set_new_export_csv(form_data:dict):
    """Create a new CSV in the uploads folder with the given filename"""
    name:str = form_data["new_csv_name"]
    filename = name + ".csv"
    folder = current_app.config.get("UPLOAD_FOLDER")
    upload_path = os.path.join(folder, "exports", filename)

    if os.path.exists(upload_path):
        raise FileExistsError(f'CSV {name} already exists')

    with open(upload_path, 'w') as file:
        file.write("")
    
    return upload_path

def set_old_export_csv(file_data:dict[str, FileStorage]):
    """Take an existing CSV file and upload it to the uploads folder"""
    if "file" not in file_data:
        raise FileNotFoundError("ERROR: No file in request")
    file = file_data["file"]
    if file.filename == "":
        raise FileNotFoundError("ERROR: No file selected")
    
    filename = file.filename
    folder = current_app.config.get("UPLOAD_FOLDER")
    path = os.path.join(folder, "exports", filename)
    file.save(path)

    return path