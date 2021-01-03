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
            'time':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        machine_dict = {
            'machine_id':self.variable.printer_id
        }

        return self.make_post_request("/api/machines/data",machine_dict,data_dict)
        