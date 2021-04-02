#
# Tasks File. This file stores all the tasks that are run on a schedule
#


from utils.utils import get_now_str
from func_timeout import func_timeout, FunctionTimedOut

from datetime import datetime

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

def update_influx_dataset(variable, source):
    #lock db for reading and writting
    variable.buffer_class.acquire_lock("update_influx")

    #get influx data
    variable.logger_class.logger.debug("gathering data from {}".format(source.name))
    influx_data = source.get_influx_data()
    if(influx_data == []):
        variable.logger_class.logger.debug("No data to upload for source {}".format(source.name))
        variable.buffer_class.release_lock("update_influx")
        return None

    #send data to influx
    variable.logger_class.logger.debug("pushing data to influx for source {}".format(source.name))
    response = variable.influx_class.write_points(source.name,influx_data)

    #if data was succesfully uploaded clear out the dataset
    if(response):
        source.clear_data()
        success = True
    else:
        success = False

    variable.buffer_class.release_lock("update_influx")
    return success

def update_influx(variable):
    #log start of status
    variable.logger_class.logger.info("Pushing Data to Influx")

    time_data = {}
    all_uploaded = []
    error = False
    for source in variable.datasources:
       

        if(not source.influx):
            continue 
        try:
            outcome = func_timeout(30,update_influx_dataset, args=(variable,source))
        except FunctionTimedOut:
            outcome = False
            if(variable.buffer_class.lock_name != ''):
                variable.logger_class.logger.error("{} has db lock".format(variable.buffer_class.lock_name))
 
        except Exception as e:
            variable.logger_class.logger.error("Failed to update influxdb {}".format(source.name))
            variable.logger_class.logger.error(e)

            if(variable.buffer_class.lock_name != ''):
                variable.logger_class.logger.error("{} has db lock".format(variable.buffer_class.lock_name))
        
        if(variable.buffer_class.lock_name == 'update_influx'):
            variable.buffer_class.release_lock('update_influx')            
            
        if(outcome is None):
            continue
        elif(outcome):
            all_uploaded.append(source.name)
        else:
            error = True

    if(error):
        variable.logger_class.logger.error("Unable to upload all data")
    elif(all_uploaded == []):
        variable.logger_class.logger.info("No data to upload")
    else:
        variable.logger_class.logger.info("Successfully Uploaded data to : {}".format(','.join(all_uploaded)))
    
    variable.last_update = datetime.now()

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
    

    
