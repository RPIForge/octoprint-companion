import os

import utils.communication
import json
#Class for syncing variables
class website():
    ip = None
    port = None
    api_key = None
    
    
    variable = None
    logger = None
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        self.logger.info("Initalizing Website Class")
        
        self.ip = os.getenv('SITE_IP',"localhost")
        self.port = os.getenv('SITE_PORT',"8000")
        self.api_key = os.getenv('SITE_KEY',"test_key")
        self.logger.info("Finished initalizing Website Class")

    
    def get_url(self):
        return "http://{}:{}".format(self.ip,self.port)
    
    def make_get_request(self,endpoint, dictionary):
        try:
            headers = {'X-Api-Key':self.api_key}
            return utils.communication.get_json(self.get_url()+endpoint, dictionary, headers)
        except ConnectionError:
            self.logger.error("Unable to reach main site")
            return None
    
    def make_post_request(self,endpoint, paramaters, data):
        try:
            headers = {'X-API-Key':self.api_key} 
            return utils.communication.post_request(self.get_url()+endpoint, paramaters, headers, json.dumps(data))
        except ConnectionError:
            self.logger.error("Unable to reach main site")
            return None
            
            
    #send status with time
    def send_status(self, status):
        response_status = {
            "machine_id": self.variable.printer_id,
            "status": status,
            
        }
        
        return self.make_post_request('/api/machines/status', response_status, None)
    
    #send print_information with time
    ##Send dict as follows:
    ##{
    ##  "completion":completion_time
    ##}
    def send_print_information(self, completion_time, file_id=None):
        response_information = {
            "completion": completion_time,
            "file": file_id
        }
        
        return self.make_post_request('/api/machines/print/information', None, response_information)
        
    #send temperature with time
    ##Send dict as follows:
    ##    [{"tool_name":"name",
    ##        "temperature":temp,
    ##        "goal":temp_goal
    ##      },
    ##    ]
    def send_temperature(self, temperature_information):
        tool_array = []
        for tool in temperature_information:
            information = {}
            information["tool_name"] = tool
            information["temperature"] = temperature_information[tool]["actual"]
            information["goal"] = temperature_information[tool]["target"]
            if(not information["goal"]):
                information["goal"] = 0
                
            tool_array.append(information)
        
        paramaters = {
            "machine_id": self.variable.printer_id
        }
        
        return self.make_post_request('/api/machines/temperature', paramaters,  tool_array)
        
    
    
        
