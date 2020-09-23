
#import helper modules
import os
import utils.communication

#import exceptions
from  requests.exceptions import ConnectionError
class octoprint():
    api_key = None
    ip = None
    port = None

    variable = None
    logger = None
    
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        self.logger.info("Initalizing Octoprint Class")
        
        #init variable object
        self.api_key = os.getenv('OCTOPRINT_KEY',"")
        self.ip = os.getenv('OCTOPRINT_IP',"127.0.0.1")
        self.port = os.getenv('OCTOPRINT_PORT',"5000")
        
        self.variable.logger_class.logger.info("Finished InitalizingOctoprint Class")
        
        
    
    def __str__(self):
        return f"octoprint at {self.ip}:{self.port}"
        
    def get_url(self):
        return "http://{}:{}".format(self.ip,self.port)
    
    def make_get_request(self,endpoint, dictionary):
        try:
            dictionary['X-Api-Key']=self.api_key
            return utils.communication.get_request(self.get_url()+endpoint, dictionary)
        except ConnectionError:
            self.logger.error("Unable to reach printer")
            return None
    
    def get_status(self):
        return self.make_get_request("/api/job",{})
        
    
    def get_temperature(self):
        return self.make_get_request("/api/printer/chamber",{})
    
    def get_file(self):
        status = self.get_status()
        if(not status and status['state']!="Printing"):
            return None
        
        status_file_info = status["job"]["file"]
        file_info = self.make_get_request("/api/files/{}/{}".format(status_file_info["origin"], status_file_info["name"]),{})
        if(not file_info):
            return None
            
        return utils.communication.get_file(file_info["refs"]["download"], {"X-Api-Key":self.api_key})
        
        
        
        

