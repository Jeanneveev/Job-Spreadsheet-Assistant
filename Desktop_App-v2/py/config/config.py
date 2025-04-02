import os
from dotenv import load_dotenv

configdir=os.path.abspath(os.path.dirname(__file__))
basedir=os.path.dirname(configdir)
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    """Sets Flask config variables"""
    #General
    SECRET_KEY=os.environ.get("SECRET_KEY")
    saves="../Saves"
    UPLOAD_FOLDER=os.path.normpath(os.path.join(basedir,saves))
    #Sessions and Cookies
    SESSION_COOKIE_SAMESITE="None"
    SESSION_COOKIE_SECURE=True
    #CORS
    CORS_HEADERS="Content-Type"
    #Session
    SESSION_PERMANENT=False
    
class sheetsConfig:
    SPREADSHEET_ID=os.environ.get("SPREADSHEET_ID")