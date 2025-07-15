"""App Factory. Creates instances of a configured Flask app."""

from flask import Flask, request
from flask_cors import CORS
import logging
## Blueprint Imports
from app.routes.blueprints import q_crud_bp, detail_bp, opt_bp, save_bp, load_bp, answ_bp, export_bp, shutdown_bp, bp
## Util Imports
from app.utils.linked_list_handler import init_ll
from app.utils.export_data_handler import init_exportdata
from app.utils.shutdown_manager import ShutdownManager

logger = logging.getLogger(__name__)

def create_app(config_obj:str, shutdown_manager:ShutdownManager = None)->Flask:
    """App factory

    Parameters:
        shutdown_manager (ShutdownManager): An instance of the
        ShutdownManager class that contains an instance of the 
        multiprocessing.Event class, which's set starus is used
        to track whether or not the app has been called to be shut down
    """
    app = Flask(__name__)

    # Configure App
    app.config.from_object(config_obj)

    # Initialize App Context Objects
    app.shutdown_manager = shutdown_manager

    # Initialize Plugins
    CORS(app,supports_credentials=True)
    init_ll(app)
    init_exportdata(app)

    # Blueprints
    app.register_blueprint(bp)
    app.register_blueprint(q_crud_bp)
    app.register_blueprint(detail_bp)
    app.register_blueprint(opt_bp)
    app.register_blueprint(save_bp)
    app.register_blueprint(load_bp)
    app.register_blueprint(answ_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(shutdown_bp)

    @app.before_request
    def log_endpoint_call():
        logger.info(f"Endpoint {request.endpoint} called")

    if shutdown_manager:    #if not testing
        @app.after_request
        def check_if_shutting_down(response):
            if shutdown_manager.is_shutting_down():
                logger.info("Shutdown event set")

            return response

    return app