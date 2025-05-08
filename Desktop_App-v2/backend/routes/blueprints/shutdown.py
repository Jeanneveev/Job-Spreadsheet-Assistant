"""The Blueprint for the shutdown route used to gracefully exit Flask"""
import signal
import os
from flask import Blueprint

shutdown_bp = Blueprint("shutdown", __name__)

def shutdown_server()->str:
    os.kill(os.getpid(), signal.SIGINT)
    return " Flask server shutdown"
@shutdown_bp.route('/shutdown', methods=['POST'])
def shutdown():
    res=""
    try:
        res+=shutdown_server()
    except Exception as e:
        res+=" Shutdown error"
    return res