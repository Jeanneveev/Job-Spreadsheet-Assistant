import logging
from flask import Blueprint

logger = logging.getLogger(__name__)
bp = Blueprint("other", __name__)

@bp.route("/", methods=["GET", "POST"])
def check():
    """Check that the server's running and connected"""
    # logger.info("Working directory path is",os.getcwd(),". Current directory path is",os.path.dirname(os.path.abspath(sys.argv[0])))
    return {"result":"Server active!"}