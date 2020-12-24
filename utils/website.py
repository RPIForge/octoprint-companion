#octoprint imports
import utils.communication

#general imports
import os
import json
import datetime

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
        except ConnectionError as ex:
            self.logger.error("Unable to reach main site")
            self.logger.error(ex)
            return None
    
    def make_post_request(self,endpoint, paramaters, data):
        try:
            headers = {'X-API-Key':self.api_key} 
            return utils.communication.post_request(self.get_url()+endpoint, paramaters, headers, json.dumps(data))
        except ConnectionError as ex:
            self.logger.error("Unable to reach main site")
            self.logger.error(ex)
            return None
            
    def send_data(self,machine_data=None,print_data=None,temperature_data=None,location_data=None):
        data_dict = {
            'time':datetime.datetime.now()
        }
        
        data = {}
        if(machine_data):
            data['machine'] = machine_data

        if(print_data):
            data['print'] = print_data

        if(temperature_data):
            data['temperature'] = temperature_data

        if(location_data):
            data['location'] = location_data
        
        data_dict["data"] = data
        self.make_post_request("/api/machines/data",{},data_dict)




    #send status with time
    def send_status(self, status, status_text):
        response_status = {
            "machine_id": self.variable.printer_id,
            "status": status,
            "status_text": status_text
        }
        
        return self.make_post_request('/api/machines/status', response_status, None)
    
    #send print_information with time
    ##Send dict as follows:
    ##{
    ##  "end_time":completion_time,
    ##  "file_id":file_id
    ##}
    def send_print_information(self, completion_time=None, file_id=None):
        response_information = {
            "machine_id": self.variable.printer_id,
            "end_time": completion_time,
            "file_id": file_id
        }
        
        return self.make_post_request('/api/machines/print/information', response_information, None)
        
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
        
        return self.make_post_request('/api/machines/print/temperature', paramaters,  tool_array)
        
    
    
        
