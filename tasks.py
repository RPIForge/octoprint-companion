

def get_end_time(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint end time")
    if(variable.status != "printing"):
        variable.logger_class.logger.info("Skipping getting Octoprint end time")
        return
        
    #get printer status
    octoprint = variable.octoprint_class
    end_time = octoprint.get_end_time()
    if(not end_time):
        variable.logger_class.logger.error("Failed to get End Time")
        return
    
    print_dict = {
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }

    #send website update
    response = variable.website_class.send_data(print_data=print_dict)

    if(not response or response.status_code!=200):
        variable.logger_class.logger.error("Failed to send end time")
    else:
        variable.logger_class.logger.info("Sent end time")

def get_temperature(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint Temperature Information")
    
    if(variable.status!="printing"):
        variable.logger_class.logger.info("Skipping Getting Octoprint Temperature Information")
        return
    
    #get printer status
    octoprint = variable.octoprint_class
    temperature_information = octoprint.get_temperature()
    if(not temperature_information):
        variable.logger_class.logger.error("Failed to get Temperature Information")
        return
    else:
        variable.logger_class.logger.info("Retrived Octoprint Temperature Information")
    

    #send website update
    response = variable.website_class.send_data(temperature_data=temperature_information)
    if(not response or response.status_code!=200):
        variable.logger_class.logger.error("Failed to send Temperature Information")
        return
    else:
        variable.logger_class.logger.info("Sent Temperature Information update")

def get_location(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint Location Information")
    
    if(variable.status!="printing"):
        variable.logger_class.logger.info("Skipping Getting Octoprint Location Information")
        return
    
    #get printer status
    octoprint = variable.octoprint_class
    layer_information = octoprint.get_layer_information()
    if(not layer_information):
        variable.logger_class.logger.error("Failed to get Octoprint Layer Information")
        return
    else:
        variable.logger_class.logger.info("Retrived Octoprint Layer Information")

    height_information = octoprint.get_printer_height()
    if(not layer_information):
        variable.logger_class.logger.error("Failed to get Octoprint Height Information")
        return
    else:
        variable.logger_class.logger.info("Retrived Octoprint Height Information")
    
    height_information.update(layer_information)

    #send website update
    response = variable.website_class.send_data(location_data=height_information)
    if(not response or response.status_code!=200):
        variable.logger_class.logger.error("Failed to send Location Information")
        return
    else:
        variable.logger_class.logger.info("Sent Location update")
    
#get pritn status
def get_status(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint Status")
    
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
        variable.logger_class.logger.info("Status Changed")
        
        #if new print
        if(status == "printing" and variable.status!="paused"):
            variable.logger_class.logger.info("Print Starting, Updating database")
            file = octoprint.get_file()
            file_id = variable.s3_class.upload_file(file)
            
            machine_dict = {
                'status':status,
                'status_message': status_text
            }

            information_dict = {
                'file_id':file_id
            }            

            response = variable.website_class.send_data(machine_data=machine_dict, print_data=information_dict)
            if(not response or response.status_code != 200):
                variable.logger_class.logger.error("Unable to send new print update")
            else:
                variable.logger_class.logger.info("Sent new print update")
            
             
        if(status == "operational" and variable.status == "printing"):
            variable.logger_class.logger.info("Print Finished, Upadting database")
            
            machine_dict = {
                'status':"completed",
                'status_message':status_text
            }
            response = variable.website_class.send_data(machine_data=machine_dict)
            
            if(not response or response.status_code != 200):
                variable.logger_class.logger.error("Unable to send finish print status update")
            else:
                variable.logger_class.logger.info("Sent finish print status update")
        
        else:
            variable.logger_class.logger.info("Printer is now {}".format(status))

            machine_dict = {
                'status':status,
                'status_message':status_text
            }
            response = variable.website_class.send_data(machine_data=machine_dict)
                        
            if(not response or response.status_code != 200):
                variable.logger_class.logger.error("Unable to send status update")
            else:
                variable.logger_class.logger.info("Sent status update")
    else:
        variable.logger_class.logger.info("Status unchanged")
        
    variable.status = status
    