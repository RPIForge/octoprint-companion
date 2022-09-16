#
# Tasks File. This file stores all the tasks that are run on a schedule
#


from utils.utils import get_now_str
from utils.datasources import temperature_data
from func_timeout import func_timeout, FunctionTimedOut
from utils.graphql2smip import graphql2smip

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

def update_graphql_dataset(variable):
    #acquire 
    variable.buffer_class.acquire_lock("update_influx")

    #for each datasource
    for source in variable.datasources:
        #get all of the raw datapoints
        raw_h5py_data = source.get_raw_data()
        
        #for meassurement 
        for measurement in raw_h5py_data:
            raw_data = source.parse_h5py_data(measurement)

     


    variable.buffer_class.release_lock("update_influx")
    return True
    
def update_source_database(variable, source):
    # source:  utils.datasources.temperature_data
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
    influx_response = variable.influx_class.write_points(source.name,influx_data)


    # get graphql_data
    ##### ! TODO UPDATE .get_graphql_data (located in utils/datasources.py)
    ##### ! This is a class specific function that parses the raw tool data into a graphql standard
    if isinstance(source, temperature_data):
        graphql_data = source.get_graphql_data()
        graphql_data = graphql_data.astype(str)
        variable.logger_class.logger.info("************ pandas file is {}".format(graphql_data.to_string()))
        #### ! Code push to graphql here and get result as bool (true for success | false for failure)
        graphql_response=variable.data_uploader.write_smip(graphql_data, variable.logger_class.logger)
        variable.logger_class.logger.info("************ smip upload is {}".format(graphql_response.to_string()))
    

    #if data was succesfully uploaded clear out the dataset
    if(influx_response and graphql_response):
        source.clear_data()
        success = True
    else:
        success = False

    variable.buffer_class.release_lock("update_influx")
    return success

def update_databases(variable):
    #log start of status
    variable.logger_class.logger.info("Pushing Data to Influx")

    time_data = {}
    all_uploaded = []
    error = False
    for source in variable.datasources:  # utils.datasources.temperature_data
       
        if(not source.influx):
            continue 
        try:
            #attempt to push data to influx with 30 second timeout
            outcome = func_timeout(30,update_source_database, args=(variable,source))

        except FunctionTimedOut:
            outcome = False
            if(variable.buffer_class.lock_name != ''):
                variable.logger_class.logger.error("{} has db lock".format(variable.buffer_class.lock_name))
 
        except Exception as e:
            variable.logger_class.logger.error("Failed to update influxdb {}".format(source.name))
            variable.logger_class.logger.error(e)

            if(variable.buffer_class.lock_name != ''):
                variable.logger_class.logger.error("{} has db lock".format(variable.buffer_class.lock_name))
            
            outcome = None
                    
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
    else:
         variable.logger_class.logger.info("Successfully updated site")

    #get updated data from the website
    variable.website_class.update_info()
    

    
