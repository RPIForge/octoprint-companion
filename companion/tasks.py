#
# Tasks File. This file stores all the tasks that are run on a schedule
#


from utils.utils import get_now_str

def get_end_time(variable):
    #log start of status
    variable.logger_class.logger.debug("Getting Octoprint end time")
    if(variable.status != "printing"):
        variable.logger_class.logger.debug("Skipping getting Octoprint end time")
        return
        
    #get printer status
    octoprint = variable.octoprint_class
    end_time = octoprint.get_end_time()
    if(not end_time):
        variable.logger_class.logger.error("Failed to get End Time")
        return
    
    #update variable dict
    print_data = {
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    }

    variable.print_data.update(print_data)
    variable.logger_class.logger.debug("Updated Print end_time")

def get_temperature(variable):
    #log start of status
    variable.logger_class.logger.debug("Getting Octoprint Temperature Information")
    
    if(variable.status == "offline"):
        variable.logger_class.logger.debug("Skipping getting Octoprint Temperature Information")
        return

    #get printer temperature
    octoprint = variable.octoprint_class
    temperature_information = octoprint.get_temperature()
    if(not temperature_information):
        variable.logger_class.logger.error("Failed to get Temperature Information")
        return
    else:
        variable.logger_class.logger.debug("Retrived Octoprint Temperature Information")
    
    #push data to the buffer
    time_str = get_now_str()
    for tool in temperature_information:
        data_array = [time_str,tool,temperature_information[tool]['actual'],temperature_information[tool]['goal']]
        variable.buffer_class.push_data('temperature_data',data_array)

    variable.logger_class.logger.debug("Added Print Temperature Information")

    


def get_location(variable):
    #log start of status
    variable.logger_class.logger.debug("Getting Octoprint Location Information")
    
    if(variable.status != "printing"):
        variable.logger_class.logger.debug("Skipping getting Octoprint Location Information")
        return

    #get printer location
    octoprint = variable.octoprint_class
    location_information = octoprint.get_location()
    
    if(not location_information):
        variable.logger_class.logger.error("Failed to get Location Information")
        return
    else:
        variable.logger_class.logger.debug("Retrived Octoprint Location Information")
    
    #push data to buffer
    current_height = location_information["current_height"]
    max_height = location_information["max_height"]
    current_layer = location_information["current_layer"]
    max_layer = location_information["max_layer"]

    data_array = [get_now_str(),current_layer,max_layer,current_height,max_height]
    self.buffer_class.push_data('location_data',data_array,width=5)

    variable.logger_class.logger.debug("Added Print Location Information")

    
#get pritn status
def get_status(variable):
    #log start of status
    variable.logger_class.logger.debug("Getting Octoprint Status")
    
    #get printer status
    octoprint = variable.octoprint_class
    status_text = octoprint.get_status_message()
    status = octoprint.get_status(status_text)
    
    
    #if error retreaving status
    if(not status):
        variable.logger_class.logger.error("Failed to get Octoprint Status")
        return
    

    #if new status
    if(status != variable.status):
        variable.logger_class.logger.debug("Status Changed")
        
        #if new print
        if(status == "printing" and variable.status!="paused"):
            variable.logger_class.logger.info("Print Starting")
            file = octoprint.get_file()
            file_id = variable.s3_class.upload_file(file)
            
            machine_dict = {
                'status':status,
                'status_message': status_text
            }

            information_dict = {
                'file_id':file_id
            }       

            if(information_dict):
                variable.print_data.update(information_dict)     
                         
        if(status == "operational" and variable.status == "printing"):
            variable.logger_class.logger.info("Print Finished")
            
            machine_dict = {
                'status':"completed",
                'status_message':status_text
            }
        
        else:
            variable.logger_class.logger.info("Printer is now {}".format(status))

            machine_dict = {
                'status':status,
                'status_message':status_text
            }
        
        variable.machine_data.update(machine_dict)
        
    else:
        variable.logger_class.logger.debug("Status unchanged")
    
    variable.status = status


def update_website(variable):
    #log start of status
    variable.logger_class.logger.info("Updating Website Data")

    response = variable.website_class.send_data(variable.machine_data,variable.print_data,variable.temperature_data,variable.location_data)
    if(not response):
        variable.logger_class.logger.error("Failed to update site with Octoprint data")
        return
    else:
         variable.logger_class.logger.info("Successfully updated site")

    variable.machine_data = {}
    variable.print_data = {}
    variable.temperature_data = []
    variable.location_data = []
    variable.logger_class.logger.debug("Successfully updated site")

    #get updated data from the website
    variable.website_class.update_info()
    

    
