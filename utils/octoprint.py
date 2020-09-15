
#import helper modules
import os
import utils.communication

class octoprint():
    api_key = None
    ip = None
    port = None

    variable = None
    def __init__(self, variable_class):
        #init variable object
        self.api_key = os.getenv('OCTOPRINT_KEY',"")
        self.ip = os.getenv('OCTOPRINT_IP',"127.0.0.1")
        self.port = os.getenv('OCTOPRINT_PORT',"5000")
        self.variable = variable_class
    
    def __str__(self):
        return f"octoprint at {self.ip}:{self.port}"
        
    def get_url(self):
        return "http://{}:{}".format(self.ip,self.port)
    
    def make_get_request(self,endpoint, dictionary):
        dictionary['X-Api-Key']=self.api_key
        return utils.communication.get_request(self.get_url()+endpoint, dictionary)
    
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
            
        return get_file(file_info["refs"]["download"], {"X-Api-Key":self.api_key})
        
        
        
        

