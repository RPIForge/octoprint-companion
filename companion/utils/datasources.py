#
# DataSources file. This file stores generic information about the data we'll get.
#

#util import
from .utils import get_now_str


#abstract data class
class generic_data():
    #name of the bucket/dataset
    name = ''
    
    fields = ['time']
    
    variable = None
    logger = None
    influx = None
    def __init__(self, variable_class, influx_type=True):
        self.variable = variable_class
        self.logger = variable_class.logger_class.logger
        self.influx = influx_type
    #
    # Data Gathering - functions used that gather data from the source
    #
    #used to pull data from octoprint/datasource 
    def update_data(self):
        raise Exception("update_data must be implemented")
    
    #
    # Data Processing - functions that manipluate data for specific functions
    #

     #used to parse  h5py arrays to generic dictionaries
    def parse_h5py_data(self, array):
        output_dict = {}
        for index in range(len(array)):
            output_dict[self.fields[index]] = array[index].decode()
        return output_dict
    
    #format generic data for influxdb
    def format_influx_data(self,dictionary):
        raise Exception("format_influx_data must be implemented")

    #
    # Data Retrval - functions used that get data
    #
    def get_raw_data(self, count=None):
        return self.variable.buffer_class.get_data(self.name,count)

    #get the data from h5py and format it for influx   
    def get_influx_data(self,count=None):
        data = self.get_raw_data(count)
        
        output_array = []
        for measurement in data:
            #process raw dsata
            parsed_data = self.parse_h5py_data(measurement)

            #format data for influx
            formated_measurement = self.format_influx_data(parsed_data)                    
            if(formated_measurement is None):
                continue

            output_array.append(formated_measurement)
        
        return output_array
    
    #get the data from h5py for website
    def get_website_data(self,count=None):
        data = self.get_raw_data(count)
        
        output_array = []
        for measurement in data:
            #process raw dsata
            parsed_data = self.parse_h5py_data(measurement)

            #format data for website
            output_array.append(parsed_data)

        return output_array
   
    #
    # Data Deletion - functions used to delete data
    #

    def clear_data(self):
        self.variable.buffer_class.clear_data(self.name)

    
class temperature_data(generic_data):
    name = 'temperature_data'

    fields = ['time','tool_name','actual','goal']
    
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

        
    def format_influx_data(self,dictionary):
        name = "{}'s temperature".format(self.variable.name)
        
        time = dictionary['time']

        tags = {
                'tool': dictionary['tool_name']
        }
        
        fields = {
                'actual':float(dictionary['actual']),
                'target':float(dictionary['goal'])
        }
        
        point = self.variable.influx_class.generate_point(name,time,tags,fields)

        return point

class location_data(generic_data):
    name = 'location_data'

    fields = ['time', 'current_layer', 'max_layer', 'current_height', 'max_height']
    
    def update_data(self):
        #log start of status
        self.logger.debug("Getting Octoprint Location Information")

        if(self.variable.status != "printing"):
            self.logger.debug("Skipping getting Octoprint Location Information")
            return

        #get printer location
        octoprint = self.variable.octoprint_class
        location_information = octoprint.get_location_information()

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

    def format_influx_data(self,dictionary):
        name = "{} location".format(self.variable.name)

        time = dictionary['time']

        tags = {}

        fields = {
                'current_layer':float(dictionary['current_layer']),
                'max_layer':float(dictionary['max_layer']),
                'current_height':float(dictionary['current_height']),
                'max_height':float(dictionary['max_height'])
        }

        return self.variable.influx_class.generate_point(name,time,tags,fields)

class status_data(generic_data):
    name = 'status_data'

    fields = ['time', 'status', 'status_message']

    def update_data(self):
        #log start of status
        self.logger.debug("Getting Octoprint Status")

        #get printer status
        octoprint = self.variable.octoprint_class
        status_text = octoprint.get_status_message()
        status = octoprint.get_status(status_text)


        #if error retreaving status
        if(not status):
            self.logger.error("Failed to get Octoprint Status")
            return
        try:
            #if new status
            if(status != self.variable.status):
                self.logger.debug("Status Changed")

                #if new print
                if(status == "printing" and self.variable.status!="paused"):
                    self.logger.info("Print Starting")
                    try:
                        file = octoprint.get_file()
                        file_id = self.variable.s3_class.upload_file(file)
                    except:
                        self.logger.error("failed to get/upload file")

                    machine_dict = {
                        'status':status,
                        'status_message': status_text
                    }

                    information_dict = {
                        'file_id':file_id
                    }

                    self.variable.print_data.update(information_dict)

                if(status == "operational" and self.variable.status == "printing"):
                    self.logger.info("Print Finished")

                    machine_dict = {
                        'status':"completed",
                        'status_message':status_text
                    }

                else:
                    self.logger.info("Printer is now {}".format(status))

                    machine_dict = {
                        'status':status,
                        'status_message':status_text
                    }

                data_array = [get_now_str(),machine_dict['status'],machine_dict['status_message']]
                self.variable.buffer_class.push_data(self.name,data_array,width=3)

            else:
                self.logger.debug("Status unchanged")

        except Exception as e:

            self.logger.error("Failed to run update status scripts")
            self.logger.error(e)

        self.variable.status = status

    def format_influx_data(self,dictionary):
        name = "{} status".format(self.variable.name)

        time = dictionary['time']

        tags = {}

        fields = {
                'status':dictionary['status'],
                'status_message':dictionary['status_message'],
        }

        return self.variable.influx_class.generate_point(name,time,tags,fields)
    
    #override get_website_data to only get the most recent data
    def get_website_data(self,count=None):
        data = self.get_raw_data(-1)
       
        parsed_data = None
        if(len(data) != 0):
            #process raw dsata
            parsed_data = self.parse_h5py_data(data[0])

        return parsed_data

