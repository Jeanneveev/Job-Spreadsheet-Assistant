"""
Guides user to fill out a list of job details that is then appended to a specified Google Sheet

Functions:
- getService(): Connects to the Google Sheets API
- getDetail(detail): Prompts user to copy some detail to clipboard, which it gets and returns
- saveToSheets(service,details,range_name): Appends the list of details as a new row of a Google Sheets spreadsheet
- main(): Saves and confirms job details and formats them as a list to be exported
"""
import pyperclip
from datetime import date
from typing import Any
##GOOGLE SHEETS STUFF
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config
# If modifying these scopes, delete the file token.json.
SCOPES=["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID=config.SPREADSHEET_ID
def getService()->Any|HttpError:
    """Connects to the Google Sheets API
    Returns:
        service (Any): the connection to the API
        error (HttError): an HttpError
    """
    creds=None
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "sheets_credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        #try and return the build
        try:
            service = build("sheets", "v4", credentials=creds)
            return service
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error


def getDetail(detail:str)->str:
    """Prompts user to copy some detail to clipboard, which it gets and returns
    Args:
        detail (str): The detail that is being prompted for (e.g. name, salary, etc.)
    Returns:
        clipped_text (str): The text user copied to the clipboard, stripped of leading and trailing space
        "": An empty string
    """
    while True:
        exists=input(f"Is there a {detail}? (y/n): ")
        if exists.lower()=="y" or exists.lower()=="":
            print(f"Please get the {detail}")
            #TODO: If the user presses enter, skip and return "" instead
            pyperclip.copy("")
            clipped_text=pyperclip.waitForNewPaste().strip()
            while True:
                response=input(f"Is \"{clipped_text}\" the correct {detail}? (y/n): ")
                match response.lower():
                    case "y"|"1"|"":
                        return clipped_text
                    case "n"|"2":
                        break
                    case _:
                        print("That's not a valid answer, please type \"y\" or \"n\"")
        else:
            return ""

def saveToSheets(service,details:list[str],range_name:str)->Any|HttpError:
    """Appends the list of details as a new row of a Google Sheets spreadsheet
    Args:
        service (Any): The connection to the Google Sheets API
        details (list[str]): A list of all the job details given and confirmed by the user
        range_name (str): The range of rows & columns that will be appended (if the row is already filled, it'll append to the first unfilled row of the same range of columns)
    Returns:
        result (Any): The confirmation that the cells were appended
        error (HttpError): An HttpError
    """
    try:
        values=[details]
        body={"values": values}
        result=(
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error
    

def main():
    """Saves and confirms job details and formats them as a list to be exported"""
    print("Let's get the job details!")
    name=getDetail("JOB NAME")
    employer=getDetail("EMPLOYER'S NAME")
    job_type=getDetail("JOB TYPE (e.g.: contract, full-time, part-time)")
    location=getDetail("JOB LOCATION")
    while True:
        location_type=input("Please note if this job is HYBRID, ON-SITE, REMOTE, or N/A: ")
        match location_type.lower():
            case "hybrid"|"1":
                location+=" (Hybrid)"
                break
            case "on-site" | "onsite"|"2":
                location+=" (On-Site)"
                break
            case "remote"|"3":
                break
            case "n/a"|"na"|"4"|"":
                break
            case _:
                print("That's not a valid answer, please type \"HYBRID\",\"ON-SITE\", \"REMOTE\" or \"N/A\"")
    source=getDetail("NAME OF THE SITE THE JOB WAS FOUND ON")
    link=getDetail("LINK TO WHERE THE JOB WAS FOUND")
    date_applied=date.today().strftime("%m/%d/%Y")
    date_emailed=""
    responded_back=""
    salary=getDetail("SALARY")
    while True:
        salary_type=input("Please note if this is YEARLY, MONTHLY, HOURLY, or N/A: ")
        match salary_type.lower():
                case "yearly"|"1":
                    salary+=" (yearly)"
                    break
                case "monthly"|"2":
                    salary+=" (monthly)"
                    break
                case "hourly"|"3":
                    salary+=" (hourly)"
                    break
                case "n/a"|"na"|"4"|"":
                    break
                case _:
                    print("That's not a valid answer, please type \"YEARLY\",\"MONTHLY\", \"HOURLY\" or \"N/A\"")


    print("\n\nOkay! So, in review, the job details are:")
    print(f"Name: {name}")
    print(f"Employer: {employer}")
    print(f"Type: {job_type}")
    print(f"Location: {location}")
    print(f"Source Name: {source}")
    print(f"Source Link: {link}")
    print(f"Salary: {salary}")
    check=input("Correct? (y/n): ")
    match check:
        case "y"|"":
            service=getService()
            # job_details={"name":name,"employer":employer,"type":job_type,
            #              "loc":location,"source":source,"link":link,"salary":salary,
            #              "applied":date_applied,"emailed":date_emailed,"responded":responded_back}
            job_details=[name,employer,job_type,location,salary,
                         date_applied,date_emailed,responded_back,source,link]
            print("Great! Saving job details to file, please wait")
            print(".\n.\n.")
            saveToSheets(service,job_details,"A2:K2")
        case "n":
            print("Then please run again with the correct information")

if __name__=="__main__":
    main()