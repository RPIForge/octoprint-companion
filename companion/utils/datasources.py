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

    #
    # Data Gathering - functions used that gather data from the source
    #
    #used to pull data from octoprint/datasource 
    def update_data(self.variable):
        raise Exception("update_data must be implemented")
    
    #
    # Data Processing - functions that manipluate data for specific functions
    #

     #used to parse  h5py arrays to generic dictionaries
    def parse_h5py_data(self, array):
        output_dict = {}
        for index in range(len(array)):
            output_dict[self.fields[index]] = array[index]
        return output_dict
    
    #format generic data for influxdb
    def format_influx_data(self,dictionary):
        raise Exception("format_influx_data must be implemented")

    def format_website_data(self, dictionary)
        raise Exception("format_website_data must be implemented")
    #
    # Data Retrval - functions used that get data
    #
    def get_raw_data(self):
        return self.variable.buffer_class.get_data(self.dataset_name)

    #get the data from h5py and format it for influx   
    def get_influx_data(self):
        data = self.get_raw_data()
        
        output_array = []
        for measurement in data:
            #process raw dsata
            parsed_data = self.parse_h5py_data(measurement)

            #format data for influx
            formated_measurement = self.format_influx_data(parsed_data)                    
            output_array.append(formated_measurement)

        return output_array
    
    #get the data from h5py for website
    def get_website_data(self):
        data = self.get_raw_data()
        
        output_array = []
        for measurement in data:
            #process raw dsata
            parsed_data = self.parse_h5py_data(measurement)

            #format data for website
            formated_measurement = self.format_website_data(parsed_data)
            output_array.append(parsed_data)

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
    
    def parse_data(self,array):
        influx_dict = {
                'time':None,
                'tags':{},
                'fields':{}
        }

        influx_dict['time'] = array[0]

        influx_dict['tags']['tool'] = array[1]

        influx_dict['fields']['temperature'] = array[2]
        influx_dict['fields']['temperature_data'] = array[3]

        
        



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
