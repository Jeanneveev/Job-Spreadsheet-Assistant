# Job-Spreadsheet-Assistant
A small widget to help me save details about jobs I applied to

# Getting Started
Please note that, currently, the most recent version of the desktop app is within Desktop_App-v2 and you can only export to Google Sheets.
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
## Installation - Desktop App (v2)
1. Create a ".env" file within the "py" folder
2. Set `SECRET_KEY="some_secret_key"`, where some_secret_key is your secret key
3. Run `pip install -r requirements.txt`

To export to a Google Sheets spreadsheet, do the following:

4. Create a credentials JSON file for your Google Cloud project ([steps found here](https://developers.google.com/sheets/api/quickstart/python#authorize_credentials_for_a_desktop_application))
5. Copy its contents into "empty_sheets_credentials.json" file and rename it to "sheets_credentials.json"
6. Create a Google Sheets file
7. Copy the spreadsheet's ID (found in the URL between "/d/" and "/edit")
8. Insert that spreadsheet's ID into the ".env" file like:
   ```sh
   SPREADSHEET_ID="<your_spreadsheet_id>"
   ```

In the terminal, navigate to the folder you downloaded Desktop_App-v2 into and run the program with:
   ```sh
   npm start
   ```


