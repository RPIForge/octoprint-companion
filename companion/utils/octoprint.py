#
# Octoprint File. This file holds all the code for connecting to the octoprint instance.
#

#import helper modules
import os
import tempfile
import utils.communication
import hashlib
import time
import datetime

#import exceptions
from  requests.exceptions import ConnectionError

#import current_time
from utils.utils import get_now_time, get_now_str

class octoprint():
    api_key = None
    url = None

    variable = None
    logger = None
    
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        self.logger.info("Initalizing Octoprint Class")
        
        #init variable object
        self.api_key = os.getenv('OCTOPRINT_KEY',"test")
        self.url = os.getenv('OCTOPRINT_URL',"http://octoprint:5000")
        
        
        if(self.get_status_message() is None):
            self.logger.error("Failed to connect to octoprint. Restarting octoprint")
            raise ValueError("Octoprint Config not valid")

        self.logger.info("Finished Initalizing Octoprint Class")

    def __str__(self):
        return f"octoprint at {self.url}"
        
    def get_url(self):
        return self.url
    
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
            return "offline"
            
    
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
            current_time = get_now_time()
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
        if(not job_information or "state" not in job_information):
            return None
        
        status = job_information['state']
        if(status and (status!="Printing from SD" or status!="Printing")):
            return None
        
        status_file_info = job_information["job"]["file"]
        file_info = self.make_get_request("/api/files/{}/{}".format(status_file_info["origin"], status_file_info["name"]),{})
        if(not file_info or 'refs' not in file_info or 'download' not in file_info['refs']):
            return None
            
        file_data = utils.communication.get_file(file_info["refs"]["download"], {}, {"X-Api-Key":self.api_key})
        file_hex = hashlib.md5(file_data).hexdigest()
        
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(file_data)
        temp_file.fileinfo = {'hash': file_hex}
        
        
            
        return temp_file
      

    def get_layer_information(self):
        layer_information = self.make_get_request("/plugin/DisplayLayerProgress/values",{})
        if(not layer_information):
            return None

        layer_information = layer_information["layer"]
        output_information = {
            "time": get_now_str(),
            "current_layer": layer_information["current"],
            "max_layer": layer_information["total"]
        }    

        if(output_information['current_layer'] == '-'):
            output_information['current_layer'] = 0
        if(output_information['max_layer'] == '-'):
            output_information['max_layer'] = 0

        return output_information
    
    def get_printer_height(self):
        height_information = self.make_get_request("/plugin/DisplayLayerProgress/values",{})
        if(not height_information):
            return None

        height_information = height_information["height"]
        output_information = {
            "time": get_now_str(),
            "current_height": height_information["current"],
            "max_height": height_information["total"]
        }     

        if(output_information['current_height'] == '-'):
            output_information['current_height'] = 0
        if(output_information['max_height'] == '-'):
            output_information['max_height'] = 0

        return output_information  

    def get_location_information(self):
        location_information = {}

        layer_information = self.get_layer_information()
        if(not layer_information):
            self.logger.error("Failed to get Octoprint Layer Information")
            return None
        else:
            location_information.update(layer_information)
            self.logger.debug("Retrived Octoprint Layer Information")

        height_information = self.get_printer_height()
        if(not height_information):
            self.logger.error("Failed to get Octoprint Height Information")
            return None
        else:
            location_information.update(height_information)
            self.logger.debug("Retrived Octoprint Height Information")
        
        return location_information
        
        

