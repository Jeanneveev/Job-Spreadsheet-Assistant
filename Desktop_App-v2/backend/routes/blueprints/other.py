from flask import Blueprint

bp = Blueprint("other", __name__)

@bp.route("/", methods=["GET","POST"])
def check():
    """Check that the server's running and connected"""
    # print("Working directory path is",os.getcwd(),". Current directory path is",os.path.dirname(os.path.abspath(sys.argv[0])))
    return {"result":"Server active!"}