import os
from dotenv import load_dotenv

configdir=os.path.abspath(os.path.dirname(__file__))
basedir=os.path.dirname(configdir)  #backend directory
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    """Sets Flask config variables"""
    #General
    SECRET_KEY=os.environ.get("SECRET_KEY")
    saves="Saves"
    UPLOAD_FOLDER=os.path.normpath(os.path.join(basedir,saves))
    DATABASE = os.path.join(basedir, "/database/database.db")
    #Sessions and Cookies
    SESSION_COOKIE_SAMESITE="None"
    SESSION_COOKIE_SECURE=True
    #CORS
    CORS_HEADERS="Content-Type"
    #Session
    SESSION_PERMANENT=False
    
class TestConfig(Config):
    """Sets test config variables"""
    #General
    SECRET_KEY=os.environ.get("SECRET_KEY")
    #Sessions and Cookies
    SESSION_COOKIE_SAMESITE="None"
    SESSION_COOKIE_SECURE=True
    #CORS
    CORS_HEADERS="Content-Type"
    #Session
    SESSION_PERMANENT=False
    #Testing
    TESTING: True

class DevelopmentConfig(Config):
    ...

def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    if host == "localhost":
        port = 5000
    else:
        port = 80
    return f"http://{host}:{port}"