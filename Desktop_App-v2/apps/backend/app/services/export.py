import os
import logging
from urllib.parse import parse_qs, urlparse
from flask import current_app
from app.utils.export_data_handler import get_export_data

logger = logging.getLogger(__name__)

def set_export_method(method:str) -> str:
    if method.lower() not in ["csv", "sheets"]:
        raise ValueError("Invalid method value")
    
    export_data = get_export_data(current_app)
    export_data.method = method
    return export_data.method

# def set_export_loc(filename):
#     export_data = get_export_data(current_app)
#     upload_folder=current_app.config.get("UPLOAD_FOLDER")
#     file_path=os.path.join(upload_folder,"CSV")
#     ### TODO: Replace with the passed filename later
#     full_file_path=os.path.join(file_path, filename)
#     export_data.loc=full_file_path

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