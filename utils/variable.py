#Class for syncing variables
class variable():
    #info variables
    name = None
    
    #util classes
    octoprint_class = None
    storage_class = None
    logger_class = None
    
    #pritn status
    status = "Offline"
    print_id = ""
    
    def __init__(self, printer_name):
        self.name = printer_name
