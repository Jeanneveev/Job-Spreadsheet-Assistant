
## Routes Imports
from flask import Flask
from flask_cors import CORS
## Blueprint Imports
from routes.blueprints import q_crud_bp, detail_bp, choice_bp, qg_crud_bp, save_bp, load_bp, answ_bp, export_bp, shutdown_bp, bp

## Util Imports
from utils.linked_list_handler import init_ll
from utils.export_data_handler import init_exportdata

def create_app(config_obj:str)->Flask:
    app = Flask(__name__)
    app.config.from_object(config_obj)

    # Initialize Plugins
    CORS(app,supports_credentials=True)
    init_ll(app)
    init_exportdata(app)

    # Blueprints
    app.register_blueprint(bp)
    app.register_blueprint(q_crud_bp)
    app.register_blueprint(detail_bp)
    app.register_blueprint(choice_bp)
    app.register_blueprint(qg_crud_bp)
    app.register_blueprint(save_bp)
    app.register_blueprint(load_bp)
    app.register_blueprint(answ_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(shutdown_bp)

    return app