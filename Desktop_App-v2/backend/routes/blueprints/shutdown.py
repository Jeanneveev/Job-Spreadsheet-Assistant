"""The Blueprint for the shutdown route used to gracefully exit Flask"""
import signal
import os
from flask import Blueprint, current_app

shutdown_bp = Blueprint("shutdown", __name__)

def shutdown_server()->str:
    os.kill(os.getpid(), signal.SIGINT)
    return " Flask server shutdown"
@shutdown_bp.route('/shutdown', methods=['POST'])
def shutdown():
    """Set the trigger to shut down the Flask app"""
    shutdown_manager = getattr(current_app, "shutdown_manager", None)
    if shutdown_manager:
        shutdown_manager.trigger_shutdown()
    return "Shutdown initiated", 200