#
# DataSources file. This file stores generic information about the data we'll get.
#

#util import
from .utils import get_now_str

#abstract data class
class generic_data():
    #name of the bucket/dataset
    dataset_name = ''
    
    fields = ['time']
    
    self.variable = None
    logger = None

    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = variable_class.logger_class

    #used to pull data from octoprint/datasource 
    def update_data(self.variable):
        pass
    
    #used to parse h5py arrays to dictionaries
    def parse_data(self, array):
        output_dictionary = {}

        for index in range(len(array)):
            field_name = self.fields[index]
            output_dictionary[field_name] = array[index]

        return output_dictionary


    #get the data from h5py    
    def get_data(self):
        data = self.variable.buffer_class.get_data(self.dataset_name)
        
        output_array = []
        for measurement in data:
            


        return output_array
    
class temperature_data(generic_data):
    dataset_name = 'temperature_data'

    fields = ['time','tool_name','actual','goal']
    
    def update_data(self.variable):
        #log start of status
        self.logger.debug("Getting Octoprint Location Information")

        if(self.variable.status != "printing"):
            self.logger.debug("Skipping getting Octoprint Location Information")
            return

        #get printer location
        octoprint = self.variable.octoprint_class
        location_information = octoprint.get_location()

        if(not location_information):
            self.logger.error("Failed to get Location Information")
            return
        else:
            self.logger.debug("Retrived Octoprint Location Information")

        #push data to buffer
        current_height = location_information["current_height"]
        max_height = location_information["max_height"]
        current_layer = location_information["current_layer"]
        max_layer = location_information["max_layer"]

        data_array = [get_now_str(),current_layer,max_layer,current_height,max_height]
        self.variable.buffer_class.push_data('location_data',data_array,width=5)

        self.logger.debug("Added Print Location Information")
    
class location_data(generic_data):
    name = 'location_data'

    fields = ['time', 'current_layer', 'max_layer', 'current_height', 'max_height']
    
    def update_data(self):
        #log start of status
        self.logger.debug("Getting Octoprint Temperature Information")

        if(self.variable.status == "offline"):
            self.logger.debug("Skipping getting Octoprint Temperature Information")
            return

        #get printer temperature
        octoprint = self.variable.octoprint_class
        temperature_information = octoprint.get_temperature()
        if(not temperature_information):
            self.logger.error("Failed to get Temperature Information")
            return
        else:
            self.logger.debug("Retrived Octoprint Temperature Information")

        #push data to the buffer
        time_str = get_now_str()
        for tool in temperature_information:
            data_array = [time_str,tool,temperature_information[tool]['actual'],temperature_information[tool]['target']]
            self.variable.buffer_class.push_data('temperature_data',data_array)

        self.logger.debug("Added Print Temperature Information")
