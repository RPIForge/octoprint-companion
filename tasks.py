from datetime import datetime

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
    
    #update variable dict
    print_data = {
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }

    variable.print_data.update(print_data)
    variable.logger_class.logger.info("Updated Print end_time")

def get_temperature(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint Temperature Information")
    
    if(variable.status == "offline"):
        variable.logger_class.logger.info("Skipping getting Octoprint Temperature Information")
        return

    #get printer status
    octoprint = variable.octoprint_class
    temperature_information = octoprint.get_temperature()
    if(not temperature_information):
        variable.logger_class.logger.error("Failed to get Temperature Information")
        return
    else:
        variable.logger_class.logger.info("Retrived Octoprint Temperature Information")
    

    if(variable.status!="printing"):
        variable.logger_class.logger.info("Skipping setting print Temperature Information")
        return


    temperature_data = {
        'data':temperature_information,
        'time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    variable.temperature_data.append(temperature_data)
    variable.logger_class.logger.info("Added Print Temperature Information")


def get_location(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint Location Information")
    
    if(variable.status == "offline"):
        variable.logger_class.logger.info("Skipping getting Octoprint Location Information")
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

    #updated
    if(variable.status!="printing"):
        variable.logger_class.logger.info("Skipping Getting Octoprint Location Information")
        return
    
    location_data = {
        'data':height_information,
        'time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    variable.location_data.append(location_data)
    variable.logger_class.logger.info("Added Print Location Information")

    
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
        variable.logger_class.logger.info("Status unchanged")
        
    variable.status = status


def update_website(variable):
    #log start of status
    variable.logger_class.logger.info("Updating Website Data")

    response_list = variable.website_class.send_data(variable.machine_data,variable.print_data,variable.temperature_data,variable.location_data)
    for response in response_list:
        if(not response):
            variable.logger_class.logger.error("Failed to update site with Octoprint data")
            return
        else:
            variable.logger_class.logger.info("Successfully updated site")

    variable.machine_data = {}
    variable.print_data = {}
    variable.temperature_data = []
    variable.location_data = []
    

    