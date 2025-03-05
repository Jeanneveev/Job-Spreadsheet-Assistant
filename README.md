# Job-Spreadsheet-Assistant
A small widget to help me save details about jobs I applied to

# Getting Started
Please note that, currently, the most recent version of the desktop app is within Desktop_App-v2. You can only create open-ended questions and export to Google Sheets.
## Prerequisites
You'll need:
- Python 3.10.7 or later
- A Google account
- [A Google Cloud project](https://developers.google.com/workspace/guides/create-project)
## Installation - Terminal Program
1. Create a credentials JSON file for your Google Cloud project ([steps found here](https://developers.google.com/sheets/api/quickstart/python#authorize_credentials_for_a_desktop_application))
2. Copy its contents into "empty_sheets_credentials.json" file and rename it to "sheets_credentials.json"
3. Download the Google client library for Python
    ```sh
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    ```
4. Create a Google Sheets file [with headings like this one](https://docs.google.com/spreadsheets/d/1fjxxy_qHj--F-DfDXmpkA1py26n-jc2b5pcXQHbOfI4/edit?usp=sharing)
5. Copy the spreadsheet's ID (found in the URL between "/d/" and "/edit") to the "empty_config.py" file and rename it to "config.py"
6. In the terminal, navigate to the folder you downloaded the project into and run the program
    ```sh
    python job_spreadsheet_assistant.py
    ```
