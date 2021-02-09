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
    url = None
    api_key = None
    
    #generic variables
    variable = None
    logger = None
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        self.logger.info("Initalizing Website Class")
        
        #get site url
        url_string = os.getenv('SITE_URL',"http://localhost:8000")
        self.url = url_string.strip()
        
        #get the api key
        self.api_key = os.getenv('SITE_KEY',"test_key")
        self.logger.info("Finished initalizing Website Class")

        #udpate date 
        self.update_info()
        
    #format url    
    def get_url(self):
        return self.url

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
    def get_info(self):
        paramater_dict = {
            'machine_id':self.variable.printer_id
        }

        return self.make_get_request('/api/machine',paramater_dict)
    
    def update_info(self):
        #get updated data from site
        machine_info = self.get_info()
        if(machine_info):
            self.variable.name = machine_info["name"]
            self.variable.type = machine_info["type"]
            self.logger.info("Gathered Data from site")
            return True
        else:
            self.logger.error("Failed to get printer data from site")
            return False


    #push octo data to website       
    def send_data(self,print_data=None,time_data=None):
        data_dict = {
            'time':get_now_str()
        }
        
        data = {}
        if(print_data):
            data['print'] = print_data

        if(time_data):
            data.update(time_data)
        
        data_dict["data"] = data
        machine_dict = {
            'machine_id':self.variable.printer_id
        }

        return self.make_post_request("/data/machines/data",machine_dict,data_dict)
        
