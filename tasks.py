#get pritn status
def get_status(variable):
    #log start of status
    variable.logger_class.logger.info("Getting Octoprint Status")
    
    #get printer status
    octoprint = variable.octoprint_class
    status = octoprint.get_status()
    
    #if error retreaving status
    if(not status):
        return
    
    #if new status
    if(status != variable.status):
        variable.logger_class.logger.info("Status Changed")
        
        #if new print
        if(status == "Printing" and variable.status!="Paused"):
            variable.logger_class.logger.info("Print Starting, Updating database")
            file = octoprint.get_file()
            file_id = variable.s3.upload_file(file)
            
    
    variable.status = status
    