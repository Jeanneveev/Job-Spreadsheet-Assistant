# Job-Spreadsheet-Assistant
A small widget to help me save details about jobs I applied to

# Getting Started
## Prerequisites
You'll need:
- Python 3.10.7 or later
- A Google account
- [A Google Cloud project](https://developers.google.com/workspace/guides/create-project)
- A Google Sheets file
## Installation - Desktop App (v2)
1. Create a ".env" file within the "backend" folder
2. Set `SECRET_KEY="some_secret_key"`, where some_secret_key is your secret key
3. Run `pip install -r requirements.txt`

To export to a Google Sheets spreadsheet, do the following:

4. Create a credentials JSON file for your Google Cloud project ([steps found here](https://developers.google.com/sheets/api/quickstart/python#authorize_credentials_for_a_desktop_application))

5. In the terminal, navigate to the folder you downloaded Desktop_App-v2 into and run the program with:
   ```sh
   npm start
   ```

## Using the App
1. Create your group of questions using the "Create Question Group" button on the "Select Question Group" page
   a. Or load a previously saved group on the "Select Question Group" page by clicking on it
2. Click "Back" or close the pop-up window to return to the homepage
3. Click "Select Export Source" button
4. Select the "Google Sheets" option
5. Open the Google Sheets file you wish to export to and copy its ID (found in the URL between "/d/" and "/edit")
6. Click the "Back to Home" button to return to the homepage once more
7. Click the "Answer Questions"
8. Answer your created questions until you reach the confirmation popup
9. If you are sure of your answers, click "Yes"
10. The data you entered will be appended to the end of your Google Sheet and you will recieve a confirmation message
11. From here, you can click "Back to Home" and "Answer Questions" again to enter data about a different job, or close the app
