import os
import sys
#add the parent directory, "backend" to sys.path to allow for imports from backend/
basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
#NOTE: relative import allowed due to the above, make sure to add above to other entrypoints
from routes.app import create_app

# NOTE: The app has to be created at the top level for Flask to
#recognize it without having the app factory in the file or command
app=create_app("config.config.Config")

if __name__=="__main__":
    app.run(debug=True, use_reloader=False)