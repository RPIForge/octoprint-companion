import os

#Class for syncing variables
class variable():
    #info variables
    name = None
    printer_id = None
    
    #util classes
    octoprint_class = None
    s3_class = None
    logger_class = None
    website_class = None
    
    #print status
    status = "Offline"


    #print data
    temperature_data = []
    location_data = []
    machine_data = {}
    print_data = {}
    
    def __init__(self):
        self.name = os.getenv('PRINTER_NAME',"generic-test")
        self.printer_id = os.getenv('PRINTER_ID',"1")
        
