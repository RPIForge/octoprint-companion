

def get_information(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint Information")
    
    #get printer status
    octoprint = variable.octoprint_class
    end_time = octoprint.get_end_time()
    if(not end_time):
        variable.logger_class.logger.error("Failed to get End Time")
        return
    
    #send website update
    variable.website_class.send_print_information(completion_time=end_time)

def get_temperature(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint Temperature Information")
    
    #get printer status
    octoprint = variable.octoprint_class
    temperature_information = octoprint.get_temperature()
    if(not temperature_information):
        variable.logger_class.logger.error("Failed to get Temperature Information")
        return
    
    #send website update
    response = variable.website_class.send_temperature(temperature_information)
    if(response.status_code!=200):
        variable.logger_class.logger.error("Failed to send Temperature Information")
        return
    
#get pritn status
def get_status(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint Status")
    
    #get printer status
    octoprint = variable.octoprint_class
    status = octoprint.get_status()
    
    #if error retreaving status
    if(not status):
        variable.logger_class.logger.error("Failed to get Octoprint Status")
        return
    
    #if new status
    if(status != variable.status):
        variable.logger_class.logger.info("Status Changed")
        
        #if new print
        if(status == "printing" and variable.status!="paused"):
            variable.logger_class.logger.info("Print Starting, Updating database")
            file = octoprint.get_file()
            file_id = variable.s3.upload_file(file)
            
            response = variable.website_class.send_status(status)
            if(response.status_code != 200):
                variable.logger_class.logger.error("Unable to send new print status update")
            
            response = variable.website_class.send_print_information(file_id=file_id)
            if(response.status_code != 200):
                variable.logger_class.logger.error("Unable to send print information update")
        
        else:
            response = variable.website_class.send_status(status)
            if(response.status_code != 200):
                variable.logger_class.logger.error("Unable to send status update")
    
    variable.status = status
    