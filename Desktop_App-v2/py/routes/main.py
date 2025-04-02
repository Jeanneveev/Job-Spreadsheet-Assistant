import os
import sys
#add the parent directory, "py" to sys.path to allow for imports from py/
basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
## Routes Imports
from flask import Flask
from flask_cors import CORS
## Blueprint Imports
from routes.blueprints import q_crud_bp, detail_bp, choice_bp, save_bp, load_bp, answ_bp, export_bp

## Util Imports
from utils.linked_list_handler import init_ll
from utils.export_data_handler import init_exportdata

app = Flask(__name__)
app.config.from_object("config.config.Config")

# Initialize Plugins
CORS(app,supports_credentials=True)
init_ll(app)
init_exportdata(app)

# Blueprints
app.register_blueprint(q_crud_bp)
app.register_blueprint(detail_bp)
app.register_blueprint(choice_bp)
app.register_blueprint(save_bp)
app.register_blueprint(load_bp)
app.register_blueprint(answ_bp)
app.register_blueprint(export_bp)

@app.route("/", methods=["GET","POST"])
def check():
    """Check that the server's running and connected"""
    # print("Working directory path is",os.getcwd(),". Current directory path is",os.path.dirname(os.path.abspath(sys.argv[0])))
    return {"result":"Server active!"}

import signal
def shutdown_server()->str:
    os.kill(os.getpid(), signal.SIGINT)
    return " Flask server shutdown"
@app.route('/shutdown', methods=['POST'])
def shutdown():
    res=""
    try:
        res+=shutdown_server()
    except Exception as e:
        res+=" Shutdown error"
    return res

# print(app.url_map)
# import sys
# print("Executing in",sys.executable)
# if "jsonschema" in sys.modules:
#     print("JSONSchema is in the modules")
# else:
#     print("jsonschema isn't in the modules")

if __name__ == "__main__":
    print("Flask server running") # Flask ready flag for main.js
    app.run(debug=True, use_reloader=False)
    # app.run(debug=True)