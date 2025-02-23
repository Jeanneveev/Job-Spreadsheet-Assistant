from os import environ, path
import os
from dotenv import load_dotenv

basedir=path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

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
    