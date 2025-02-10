from os import environ, path
import os
from dotenv import load_dotenv
import redis

basedir=path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

class Config:
    """Sets Flask config variables"""
    #General
    SECRET_KEY=os.environ.get("SECRET_KEY")
    #Sessions and Cookies
    SESSION_COOKIE_SAMESITE="None"
    SESSION_COOKIE_SECURE=True
    #CORS
    CORS_HEADERS="Content-Type"
    #Redis
    SESSION_TYPE="redis"
    SESSION_PERMANENT=False
    SESSION_REDIS=redis.from_url('redis://127.0.0.1:6379')