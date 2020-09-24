#Class for syncing variables
class variable():
    #info variables
    name = None
    
    #util classes
    octoprint_class = None
    storage_class = None
    logger_class = None
    
    #print status
    status = "Offline"
    job_id = None
    
    def __init__(self, printer_name):
        self.name = printer_name
