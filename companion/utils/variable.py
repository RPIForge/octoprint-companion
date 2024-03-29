#
# Variable File. This file holds the variable class which is used for syncing instances/variables accross threads
#

import os
from datetime import datetime
import logging

#Class for syncing variables
class variable():
    #info variables
    name = None
    printer_id = None
    type = None
    
    #flask application
    flask_app = None

    #mtconnect
    mtconnect = None

    #opcua
    opcua = None
    opcua_ref= None

    #util classes
    octoprint_class = None
    s3_class = None
    influx_class = None
    buffer_class = None
    logger_class = None
    website_class = None
    
    #print status
    status = "Offline"
    job = None
    material = None

    # graphql data uploader
    data_uploader=None
    
    #buffered data
    datasources = []

    #data to be sent next print
    machine_data = {}
    print_data = {}
    
    #last time influx was updated
    last_update = None

    def __init__(self):
        self.name = os.getenv('NAME',"generic-test")
        self.type = os.getenv('TYPE',"printer")
        self.printer_id = os.getenv('ID',"1")
        
        self.last_update = datetime.now()

    def read_env(self):
        #get logger and file name
        if(self.logger_class is None):
            log = logging.getLogger('general_logger')
        else:
            log = self.logger_class.logger

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
        
variable_instance = variable()
