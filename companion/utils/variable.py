#
# Variable File. This file holds the variable class which is used for syncing instances/variables accross threads
#

import os
import logging

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
        #get logger and file name
        log = logging.getLogger('general_logger')
        env_file_name = os.getenv('ENV_FILE',None)
        
        #if no file provided then skip
        if(env_file_name is None):
            return
        
        #try to find file
        log.info("Looking for file {}".format(env_file_name))
        if(not os.path.isfile(env_file_name)):
            log.error("ENV file {} not found".format(env_file_name))
            return
        
        #read each line in file
        env_file = open(env_file_name, 'r')
        for line in env_file.readlines():
            pair = line.split("=")
            key = pair[0]
            value = pair[1]
            log.info("setting key: {} value: {}".format(key,value))
            os.environ[key] = value.strip()
        return
