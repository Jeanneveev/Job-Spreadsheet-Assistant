import os
from typing import Any
import logging
# Google Sheets Imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# Config
from config.config import basedir

logger = logging.getLogger(__name__)

class ExportDataError(Exception):
    """ A base class for ExportData-related exceptions """

class AuthenticationError(ExportDataError):
    """Exception raised for errors relating to failed authentication attempts"""

class TokenFetchError(ExportDataError):
    """Exception raised for errors fetching a token"""

class ServiceBuildError(ExportDataError):
    """Exception raised for errors building the Google API service"""

class SheetsConnectionError(ExportDataError):
    """Exception raised for errors connecting to a Google Sheets file"""

class ExportData:
    """
    A class that holds the info and methods for data exportation

    Attributes
    ----------
    data : list[str]
        a list of all the answers given
    method : str
        the type of what is being exported to ( e.g. CSV, Google Sheets )
    loc : str
        the location of the export ( currently only planned to be used for the pathstring of the export csv )
    """

    def __init__(self):
        self.data: list[str] = None
        self.method: str = None
        self.service = None
        self.loc = None
        self.sheet_id = None
    
    # CSV
    def export_to_CSV(self):
        if self.loc == None:
            raise FileNotFoundError
        pass

    # GOOGLE SHEETS
    # CONNECTION
    def get_auth_url(self) -> str | None:
        """A function to send the URL of the log-in page for the frontend to open,
            allow for user certification, and send back that certification via another route
        """
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = None
        token_path = os.path.join(basedir, "token.json")
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError as e:  # creds.refresh_token is also expired
                    logger.info(f"Refresh error: {e}; attempting login...")
                    # delete token.json and re-run function so the if statement fails
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    return self.get_auth_url()
            else:
                # redirect_uri is the page Google redirects to after sign-in is complete
                flow = InstalledAppFlow.from_client_secrets_file(
                    "sheets_credentials.json", SCOPES, redirect_uri="http://127.0.0.1:5000/auth_landing_page/"
                )
                # get and return the auth url
                auth_url, _ = flow.authorization_url()
                return auth_url
        return None

    def get_service(self, code=None) -> Any | dict | HttpError:
        """Connects to the Google Sheets API
        Args:
            code: The authentification code gotten from the user login
        Returns:
            service (Any): the connection to the API
            error (dict): a error message
            error (HttError): an HttpError
        """
        # NOTE: If modifying this scope, delete token.json file
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = None  # initialize creds
        # If there is already a token.json, just get the credentials from it
        token_path = os.path.join(basedir, "token.json")
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logger.info(f"Credentials from token.json: {creds}")
        # if there isn't or the credentials aren't valid
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError as e:  # creds.refresh_token is also expired
                    logger.info(f"Refresh error: {e}. Trying again...")
                    # delete token.json and re-run function so the if statement fails
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    return self.get_service()
            elif code:
                creds_path = os.path.join(basedir, "sheets_credentials.json")
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, SCOPES, redirect_uri="http://127.0.0.1:5000/auth_landing_page/"
                )
                # try getting the token of the credentials from the auth code
                try:
                    flow.fetch_token(code=code)
                    creds = flow.credentials
                    with open(token_path, "w") as token:
                        token.write(creds.to_json())
                except Exception as e:
                    logger.info(f"ERROR!! Error fetching token: {e}")
                    raise TokenFetchError(
                        "Error authenticating via code") from e
            else:  # no creds or code
                raise AuthenticationError(
                    "No valid credits or code. User could not be authenticated")

        # try and return the build
        try:
            if creds is None:
                raise AuthenticationError("Credentials are None")
            if not creds.valid:
                raise AuthenticationError("Credentials are invalid")
            # logger.info(f"Credentials are: {creds}")
            self.service = build("sheets", "v4", credentials=creds)
            # logger.info("service gotten")
            return self.service
        except HttpError as error:
            logger.info(f"An error occurred: {error}")
            raise ServiceBuildError(
                f"Some error occured with Google Sheets' API: {error}")
        except AuthenticationError as error:
            logger.info(f"An Authentication error occurred: {error}")
            raise ServiceBuildError(f"Authentication error: {error}")

    def _validate_sheet_id(self, id: str) -> tuple[bool, str]:
        """A function that checks if the given Google Sheets id exists by
        attempting to open it."""
        try:
            service = self.get_service()
            sheet_connection = service.spreadsheets().get(spreadsheetId=id).execute()

            return True, "Sheet exists and is accessible"
        except HttpError as error:
            status_code = error.response.status_code
            if status_code == 403:
                logger.error(
                    "Access denied: User does not have permission to access this sheet")
                return False, "Access denied: User does not have permission to access this sheet"
            elif status_code == 404:
                return False, "Access denied: The given ID does not match to any Google Sheets file"
            else:
                return False, f"Unexpected error: {error}"

    def set_sheet_id(self, id: str) -> str | SheetsConnectionError:
        """Sets the sheet_id variable of the ExportData instance if the id is valid"""
        print("Setting sheet id")
        is_valid, msg = self._validate_sheet_id(id)
        if is_valid:
            self.sheet_id = id
            return msg
        else:
            raise SheetsConnectionError(msg)

    # EXPORTING
    def length_to_col_letter(self, length: int):
        num2char = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E",
                    6: "F", 7: "G", 8: "H", 9: "I", 10: "J",
                    11: "K", 12: "L", 13: "M", 14: "N", 15: "O",
                    16: "P", 17: "Q", 18: "R", 19: "S", 20: "T",
                    21: "U", 22: "V", 23: "W", 24: "X", 25: "Y", 26: "Z"}
        col = ""
        if length > 26:
            len1 = length//26
            len2 = length % 26
            col = num2char[len1]+num2char[len2]
        else:
            col = num2char[length]
        return col

    def export_to_sheets(self) -> Any | dict:
        """Appends the list of details as a new row of a Google Sheets spreadsheet
        Args:
            self: The current instance of ExportData
        Returns:
            result (Any): The confirmation that the cells were appended
            dict: A dictionary with the key "error" and the error message
        """
        try:
            if self.service is None:
                logger.info("Check 1, self.service is None")
                self.get_service()  # ensure self.service is set
            if self.service is None:  # check again
                logger.info("Check 2: self.service is still None")
                raise ServiceBuildError(
                    "Google Sheets service could not be obtained.")
        except AuthenticationError as e:
            logger.info(f"Authentication error: {e}")
            return {"error": f"{e}"}, 400
        except TokenFetchError as e:
            logger.info(f"TokenFetch error: {e}")
            return {"error": f"{e}"}, 404
        except ServiceBuildError as e:
            logger.info(f"ServiceBuild error: {e}")
            return {"error": f"{e}"}, 501
        except Exception as e:
            logger.info(f"An error has occured: {e}")
            return {"error": f"{e}"}, 404
        logger.info("service found")
        data = self.data
        end_col = self.length_to_col_letter(len(data))
        rnge = f"A2:{end_col}2"

        try:
            values = [data]
            body = {"values": values}
            result = (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.sheet_id,
                    range=rnge,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            # logger.info(f"{(result.get('updates').get('updatedCells'))} cells appended.")
            return result
        except HttpError as error:
            logger.info(f"An error occurred: {error}")
            return {"error": f"{error}"}
