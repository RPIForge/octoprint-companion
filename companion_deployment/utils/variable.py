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
        self.name = os.getenv('NAME',"generic-test")
        self.printer_id = os.getenv('ID',"1")
        
    def read_env(self):
        print("Getting Environmental Variables")
        env_file_name = os.getenv('ENV_FILE',"")
        if(not os.path.isfile(env_file_name)):
            print("file {} not found".format(env_file_name))
            return

        env_file = open(env_file_name, 'r')
        for line in env_file.readlines():
            pair = line.split("=")
            key = pair[0]
            value = pair[1]
            print("setting key: {} value: {}".format(key,value))
            os.environ[key] = value.strip()
        return
