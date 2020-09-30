import os

#Class for syncing variables
class website():
    self.ip = None
    self.key = None
    
    
    variable = None
    logger = None
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        
        
        self.ip = os.getenv('SITE_IP',"forgedevchannels.eastus.cloudapp.azure.com")
        self.key = os.getenv('SITE_KEY',"test_key")
        
    
    #send status with time
    def send_status(self, status):
        pass
    
    #send print_information with time
    def send_print_information(self, percentage, completion_time):
        pass
        
    #send temperature with time
    def send_temperature(self, temperature):
        pass
        
    
    
        
