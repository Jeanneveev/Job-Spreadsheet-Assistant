"""Flask app factory"""

from flask import Flask
from flask_cors import CORS
from .blueprints.routes import bp
from .utils.shutdown_manager import ShutdownManager

def create_app(shutdown_manager:ShutdownManager = None)->Flask:
    """App factory

    Parameters:
        shutdown_manager (ShutdownManager): An instance of the
        ShutdownManager class that contains an instance of the 
        multiprocessing.Event class, which's set starus is used
        to track whether or not the app has been called to be shut down
    """
    app = Flask(__name__)

    # Initialize App Context Objects
    app.shutdown_manager = shutdown_manager

    # Initialize Plugins
    CORS(app, supports_credentials=True)

    #Blueprints
    app.register_blueprint(bp)
    # app.register_blueprint(bp, url_prefix="api")
    @app.after_request
    def check_if_shutting_down(response):
        if shutdown_manager.is_shutting_down():
            print("Shutdown event set")

        return response

    return app