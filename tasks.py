def get_status(variable):
    variable.logger_class.logger.info("Getting Octoprint Status")
    
    octoprint = variable.octoprint_class
    status = octoprint.get_status()
    
    #if error retreaving status
    if(not status):
        return
    
    if(status != variable.status):
        variable.logger_class.logger.info("Status Changed")
        if(status == "Printing"):
            variable.logger_class.logger.info("Print Starting, Updating database")
            file = octoprint.get_file()
            variable.storage.start_print(file)
    
    variable.status = status
    