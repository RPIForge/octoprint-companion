#octoprint imports
import utils.communication

#general imports
import os
import socket
import json
import datetime

#Class for syncing variables
class website():
    ip_list = None
    port_list = None
    api_key = None
    
    
    variable = None
    logger = None
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        self.logger.info("Initalizing Website Class")
        
        ip_string = os.getenv('SITE_IP',"localhost")

        #get list of ip address
        ip_list = ip_string.split(',')
        valid_ip_list = []

        #validate each ip in list.
        for ip in ip_list:
            try:
                ip = ip.strip()
                if(ip is ''):
                    continue
                new_ip = socket.gethostbyname(ip)
                valid_ip_list.append(new_ip)
            except socket.gaierror:
                self.logger.error("{} is not a valid ip or hostname for website".format(ip))

        self.ip_list = valid_ip_list

        port_string = os.getenv('SITE_PORT',"8000")
        port_list = port_string.split(',')
        valid_port_list = []
        for port in port_list:
            port = port.strip()
            if(port is ''):
                continue
            valid_port_list.append(port)
        
        self.port_list = valid_port_list

        if(len(self.ip_list) != len(self.port_list)):
            for i in range(len(self.port_list)-1,len(self.ip_list)):
                self.logger.error("{} does not have a port. Defaulting to 8000".format(self.ip_list[i]))
                self.port_list.append('8000')

        self.api_key = os.getenv('SITE_KEY',"test_key")
        self.logger.info("Finished initalizing Website Class")

    
    def get_url(self, loc):
        return "http://{}:{}".format(self.ip_list[loc],self.port_list[loc])
    
    def make_get_request(self,endpoint, dictionary):
        output_array = []
        for i in range(len(self.ip_list)):
            ip = self.ip_list[i]
            try:
                headers = {'X-Api-Key':self.api_key}
                output_array.append(utils.communication.get_json(self.get_url(i)+endpoint, dictionary, headers))
            except ConnectionError as ex:
                self.logger.error("Unable to reach {}".format(ip))
                self.logger.error(ex)
                output_array.append(None)
        return output_array
    
    def make_post_request(self,endpoint, paramaters, data):
        output_array = []
        for i in range(len(self.ip_list)):
            ip = self.ip_list[i]
            try:
                headers = {'X-API-Key':self.api_key} 
                output_array.append(utils.communication.post_request(self.get_url(i)+endpoint, paramaters, headers, json.dumps(data)))
            except ConnectionError as ex:
                self.logger.error("Unable to reach {}".format(ip))
                self.logger.error(ex)
                output_array.append(None)
                
        return output_array
            
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

        return self.make_post_request("/data/machines/data",machine_dict,data_dict)
        