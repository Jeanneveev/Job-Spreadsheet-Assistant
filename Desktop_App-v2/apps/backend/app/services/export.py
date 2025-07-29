import os
import pandas
import logging
from urllib.parse import parse_qs, urlparse
from flask import current_app
from werkzeug.datastructures import FileStorage
from app.utils.export_data_handler import get_export_data
from app.utils.linked_list_handler import get_ll

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
    # logger.info(f"service is: {service}")
    if type(service) == dict: #it's an error
        logger.info("Error: ", service)  #print that error message
        raise ValueError(service)
    else:
        logger.info("Authentification successful and connection built")

def export_data_to_sheets():
    # logger.info("export_data_to_sheets reached")
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

def check_allowed_extension_csv(filename:str) -> bool:
    ALLOWED_EXTENSIONS = [".csv"]
    extension = os.path.splitext(filename)[1]
    # logger.info(f"Extension is: {extension}")
    if extension in ALLOWED_EXTENSIONS:
        # logger.info("Correct file extension")
        return True
    else:
        logger.error("Incorrect file extension")
        return False
    
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
    if file and check_allowed_extension_csv(filename):
        folder = current_app.config.get("UPLOAD_FOLDER")
        path = os.path.join(folder, "exports", filename)
        file.save(path)

    return path

def make_csv_headers():
    ll = get_ll(current_app)
    headers = ll.getAllQuestionDetails()
    return headers

def get_csv_headers(df:pandas.DataFrame):
    """Get the column headers of the CSV file, or get all q_details if the former doesn't exist"""
    logger.info("Reached get_csv_headers")
    headers = df.columns.to_list()
    if not headers: # the CSV is empty
        print("no headers found. Making headers")
        headers = make_csv_headers()

    return headers

def export_data_to_csv():
    """Export all answers to the set CSV"""
    logger.info("Reached export_data_to_csv")
    exportData = get_export_data(current_app)
    data = exportData.data
    logger.info("Got export data")
    if os.path.exists(exportData.loc) and os.path.getsize(exportData.loc) == 0:
        logger.info("CSV is empty. Creating new dataframe with data only.")
        headers = make_csv_headers()
        df = pandas.DataFrame([data], columns=headers)
        df.to_csv(exportData.loc, index=False)
        return f"{len(df.columns)} cells appended"
    
    df = pandas.read_csv(exportData.loc, index_col=False)
    headers = get_csv_headers(df)
    # if data is shorter than the number of columns, pad it
    padded_data = data + [""] * (len(headers) - len(data))
    # If data is longer than the number of columns, truncate it
    logger.warning(f"Data too long, truncating {len(data) - len(headers)} columns")
    padded_data = padded_data[:len(headers)]

    new_df = pandas.DataFrame([padded_data], columns=headers)
    df = pandas.concat([df, new_df], ignore_index=True)

    df.to_csv(exportData.loc, index=False)

    return f"{len(df.columns)} cells appended"
    

    