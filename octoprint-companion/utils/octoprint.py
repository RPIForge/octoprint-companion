
#import helper modules
import os
import tempfile
import utils.communication
import hashlib

#import exceptions
from  requests.exceptions import ConnectionError

#import current_time
import datetime
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
        
        self.variable.logger_class.logger.info("Finished Initalizing Octoprint Class")
        
    
    def __str__(self):
        return f"octoprint at {self.ip}:{self.port}"
        
    def get_url(self):
        return "http://{}:{}".format(self.ip,self.port)
    
    def make_get_request(self,endpoint, dictionary):
        try:
            headers = {'X-Api-Key':self.api_key}
            return utils.communication.get_json(self.get_url()+endpoint, dictionary, headers)
        except ConnectionError:
            self.logger.error("Unable to reach printer")
            return None
    
    def get_status(self, status=None):
        if(status is None):
            status = self.get_status_message()

        if(status=="Printing from SD" or status=="Printing"):
            return "printing"
        if(status=="Operational"):
            return "operational"
        elif(status=="Paused"):
            return "paused"
        elif(status=="Error"):
            return "error"
        elif(status=="Cancelling"):
            return "cancelling"
        elif(status=="Offline"):
            return "offline"
        else:
            return None
            
    
    def get_status_message(self):
        response = self.make_get_request("/api/job",{})
        if(response and "state" in response):
            return response["state"]
        return None
        
    def get_end_time(self):
        response = self.make_get_request("/api/job",{})
        if(response and "progress" in response):
            if(response["progress"]["printTimeLeft"] is None):
                return None
                
            seconds_remaining = int(response["progress"]["printTimeLeft"])
            current_time = datetime.datetime.now()
            end_time = current_time + datetime.timedelta(seconds=seconds_remaining)
            return end_time
            
        return None
            
        
    def get_temperature(self):
        response = self.make_get_request("/api/printer",{})
        if(response and "temperature" in response and "tool0" in response["temperature"]):
            return response["temperature"]
        
        return None
    
    def get_file(self):
        job_information = self.make_get_request("/api/job",{})
        if(not job_information and "state" not in job_information):
            return None
        
        status = job_information['state']
        if(status and (status!="Printing from SD" and status!="Printing")):
            return None
        
        status_file_info = job_information["job"]["file"]
        file_info = self.make_get_request("/api/files/{}/{}".format(status_file_info["origin"], status_file_info["name"]),{})
        if(not file_info):
            return None
         

        file_data = utils.communication.get_file(file_info["refs"]["download"], {}, {"X-Api-Key":self.api_key})
        file_hex = hashlib.md5(file_data).hexdigest()
        
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(file_data)
        temp_file.fileinfo = {'hash': file_hex}
        
        
            
        return temp_file
        
    def get_layer_information(self):
        layer_iformation = self.make_get_request("/plugin/DisplayLayerProgress/values",{})
        if(not layer_iformation):
            return None

        layer_iformation = layer_iformation["layer"]
        output_information = {
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_layer": layer_iformation["current"],
            "max_layer": layer_iformation["total"]
        }    

        return output_information
    
    def get_printer_height(self):
        layer_iformation = self.make_get_request("/plugin/DisplayLayerProgress/values",{})
        if(not layer_iformation):
            return None

        layer_iformation = layer_iformation["height"]
        output_information = {
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_height": layer_iformation["current"],
            "max_height": layer_iformation["total"]
        }     

        return output_information  

        
        
        

