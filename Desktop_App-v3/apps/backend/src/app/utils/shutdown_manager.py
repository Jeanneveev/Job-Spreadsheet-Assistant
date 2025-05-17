class ShutdownManager:
    """
    A manager class for the shutting down of the Flask
    process.
    Expected to take in a multiprocessing.Event
    """
    def __init__(self, event=None):
        self.event = event
    
    def set_event(self, event):
        self.event = event
    
    def trigger_shutdown(self):
        if self.event:
            self.event.set()
    
    def is_shutting_down(self):
        return self.event.is_set()
