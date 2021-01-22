#
# Website File. This file holds all of the code for pushing to the website. It is abstracted so that it is sent a one large json
#

#octoprint imports
import utils.communication

#time imports
from utils.utils import get_now_str


#general imports
import os
import socket
import json

#Class for syncing variables
class website():
    ip = None
    port = None
    api_key = None
    
    #generic variables
    variable = None
    logger = None
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        self.logger.info("Initalizing Website Class")
        
        ip_string = os.getenv('SITE_IP',"localhost")
        ip = ip_string.strip()
        try:
            new_ip = socket.gethostbyname(ip)
            self.ip = new_ip
        except socket.gaierror:
            self.logger.error("{} is not a valid ip or hostname for website".format(ip))

        #get list of port numbers
        port_string = os.getenv('SITE_PORT',"8000")
        self.port = port_string.strip()
        
        
        #get the api key
        self.api_key = os.getenv('SITE_KEY',"test_key")
        self.logger.info("Finished initalizing Website Class")

    #format url    
    def get_url(self):
        return "http://{}:{}".format(self.ip, self.port)
    
    def make_get_request(self,endpoint, dictionary):
        try:
            headers = {'X-Api-Key':self.api_key}
            return utils.communication.get_json(self.get_url()+endpoint, dictionary, headers)
        except ConnectionError as ex:
            self.logger.error("Unable to reach {}".format(ip))
            self.logger.error(ex)
        
            return None
    
    def make_post_request(self,endpoint, paramaters, data):
        try:
            headers = {'X-API-Key':self.api_key} 
            return utils.communication.post_request(self.get_url()+endpoint, paramaters, headers, json.dumps(data))
        except ConnectionError as ex:
            self.logger.error("Unable to reach {}".format(ip))
            self.logger.error(ex)
            return None
    
    #get data about machine_id
    def get_info(self,machine_id):
        paramater_dict = {
            'machine_id':self.variable.printer_id
        }

        return self.make_get_request('/api/machine',paramater_dict)

    #push octo data to website       
    def send_data(self,machine_data=None,print_data=None,temperature_data=None,location_data=None):
        data_dict = {
            'time':get_now_str()
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

        return self.make_post_request("/data/machines/data",machine_dict,data_dict)
        
