# Job-Spreadsheet-Assistant
A small widget to help me save details about jobs I applied to

# Getting Started
## Prerequisites
You'll need:
- Python 3.10.7 or later
- A Google account
- [A Google Cloud project](https://developers.google.com/workspace/guides/create-project)
## Installation - Desktop App (v2)
1. Create a ".env" file within the "backend" folder
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
   
9. In the terminal, navigate to the folder you downloaded Desktop_App-v2 into and run the program with:
   ```sh
   npm start
   ```
