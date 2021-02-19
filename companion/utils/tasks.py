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

def update_influx(variable):
    #log start of status
    variable.logger_class.logger.info("Pushing Data to Influx")

    time_data = {}
    all_uploaded = []
    error = False
    for source in variable.datasources:
        if(not source.influx):
            continue 

        #get influx data
        influx_data = source.get_influx_data()
        if(influx_data == []):
            variable.logger_class.logger.debug("No data to upload for source {}".format(source.name))
            continue

        #send data to influx
        response = variable.influx_class.write_points(source.name,influx_data)

        #if data was succesfully uploaded clear out the dataset
        if(response):
            source.clear_data()
            all_uploaded.append(source.name)
        else:
            error = True

    if(error):
        variable.logger_class.logger.error("Unable to upload all data")
    elif(all_uploaded == []):
        variable.logger_class.logger.info("No data to upload")
    else:
        variable.logger_class.logger.info("Successfully Uploaded data to : {}".format(','.join(all_uploaded)))

def update_website(variable):
    #log start of status
    variable.logger_class.logger.info("Updating Website Data")

    time_data = {}
    for source in variable.datasources:
        time_data[source.name] = source.get_website_data(count=-10)
    
    response = variable.website_class.send_data(variable.print_data, time_data)
    if(not response):
        variable.logger_class.logger.error("Failed to update site with Octoprint data")
        return
    else:
         variable.logger_class.logger.info("Successfully updated site")

    variable.logger_class.logger.debug("Successfully updated site")

    #get updated data from the website
    variable.website_class.update_info()
    

    
