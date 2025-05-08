import configparser
from flask import Blueprint, current_app

bp = Blueprint("bp", __name__)
config = configparser.ConfigParser()

@bp.route("/")
def index():
    print("reached index")
    return "Reached index"

@bp.route("/shutdown", methods=["POST"])
def shutdown():
    """Set the trigger to shut down the Flask app"""
    shutdown_manager = getattr(current_app, "shutdown_manager", None)
    if shutdown_manager:
        shutdown_manager.trigger_shutdown()
    return "Shutdown initiated", 200
