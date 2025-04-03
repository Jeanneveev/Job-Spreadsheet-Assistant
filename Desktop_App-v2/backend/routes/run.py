import os
import sys
#add the parent directory, "backend" to sys.path to allow for imports from backend/
basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
#NOTE: relative import allowed due to the above, make sure to add above to other entrypoints
from routes.app import create_app

app=create_app("config.config.Config")
app.run(debug=True, use_reloader=False)