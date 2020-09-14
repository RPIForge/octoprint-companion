
#import helper modules
import os

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

