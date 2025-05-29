"""Entry-point file. Runs the Flask app"""

import sys
import multiprocessing
from .app import create_app
from ..utils.shutdown_manager import ShutdownManager


def run_flask_app(shutdown_event):
    shutdown_manager = ShutdownManager(event=shutdown_event)
    app = create_app(shutdown_manager)
        
    app.run(debug=True, use_reloader=False)

if __name__=="__main__":
    try:
        shutdown_event = multiprocessing.Event()
        flask_proc = multiprocessing.Process(target=run_flask_app, args=(shutdown_event,))
        flask_proc.start()
        print("flask_proc started")
        shutdown_event.wait()
        print("Shutdown event triggered")
        flask_proc.terminate()
        flask_proc.join()
        print("Flask app ended")
    except KeyboardInterrupt as exc:
        print(f"Caught KeyboardInterrupt {exc}")
    except Exception as exc:
        print(f"Caught exception {exc.__class__.__name__}: {exc}")

    print("Exiting with code 0")
    sys.exit(0)