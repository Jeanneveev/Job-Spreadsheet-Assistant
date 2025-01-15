# Job-Spreadsheet-Assistant
A small widget to help me save details about jobs I applied to

# Getting Started
## Prerequisites
You'll need:
- Python 3.10.7 or later
- A Google account
- [A Google Cloud project](https://developers.google.com/workspace/guides/create-project)
## Installation
1. Create a credentials JSON file for your Google Cloud project ([steps found here](https://developers.google.com/sheets/api/quickstart/python#authorize_credentials_for_a_desktop_application))
2. Copy its contents into "test_sheets_credentials.json" and rename the file to "sheets_credentials.json"
3. Download the Google client library for Python
    ```sh
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    ```
3. Run the program
    ```sh
    python3 job_spreadsheet_assistant.py
    ```