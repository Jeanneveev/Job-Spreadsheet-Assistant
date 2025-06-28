"""Entry-point file. Runs the Flask app"""

import os
import sys
import logging
import multiprocessing
from waitress import serve
from .app import create_app
from ..utils.shutdown_manager import ShutdownManager

def resource_path(relative_path):
    """Translate relative paths into absolute paths
    for the sake of agreeance with PyInstaller"""
    try:    # prod mode, base is the path of the executable
        base_path = sys._MEIPASS
    except AttributeError:  # dev mode, not using executable, use project root instead
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../")
        )
    return os.path.join(base_path, relative_path)

# Logging Setup
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE =os.path.join(LOG_DIR, "app.log")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_flask_app(shutdown_event):
    shutdown_manager = ShutdownManager(event=shutdown_event)
    config_path = "backend.config.config.Config"
    app = create_app(config_path, shutdown_manager)
        
    serve(app, host="0.0.0.0", port=5000)

if __name__=="__main__":
    try:
        shutdown_event = multiprocessing.Event()
        flask_proc = multiprocessing.Process(target=run_flask_app, args=(shutdown_event,))
        flask_proc.start()
        logger.info("flask_proc started")
        shutdown_event.wait()
        logger.info("Shutdown event triggered")
        flask_proc.terminate()
        flask_proc.join()
        logger.info("Flask app ended")
    except KeyboardInterrupt as exc:
        logger.info(f"Caught KeyboardInterrupt {exc}")
    except Exception as exc:
        logger.info(f"Caught exception {exc.__class__.__name__}: {exc}")

    logger.info("Exiting with code 0")
    sys.exit(0)