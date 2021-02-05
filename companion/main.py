#
# Main File. This file initializes all classes and then starts running tasks
#


#schedule import
import schedule
import time

#enviroment variables import
import os


#inisitalize variable
from utils.variable import variable
variable_instance = variable()

#initialize logging
from utils.logging import logger
logger_instance = logger(variable_instance)
variable_instance.logger_class = logger_instance

#update variables from env file
variable_instance.read_env()

#initialize octoprint companion
from utils.octoprint import octoprint
#try to get octoprint instance
octoprint_instance = octoprint(variable_instance)

variable_instance.octoprint_class = octoprint_instance

#initialize storage companions
from utils.storage import s3
s3_instance = s3(variable_instance)
variable_instance.s3_class = s3_instance

from utils.storage import influx
influx_instance = influx(variable_instance)
variable_instance.influx_class = influx_instance

from utils.storage import disk_storage
buffer_instance = disk_storage(variable_instance)
variable_instance.buffer_class = buffer_instance

#initialize website companion
from utils.website import website
website_instance = website(variable_instance)
variable_instance.website_class = website_instance

#import and schedule generic tasks
import tasks
schedule.every(5).seconds.do(tasks.get_status, variable_instance)
schedule.every(5).seconds.do(tasks.get_end_time, variable_instance)
schedule.every(5).seconds.do(tasks.update_influx, variable_instance)
schedule.every(10).seconds.do(tasks.update_website, variable_instance)

#import and schedule data source specific tasks
from utils.datasources import temperature_data,location_data

#initalize all data sources
temperature = temperature_data(variable_instance)
location = location_data(variable_instance)
variable_instance.datasources = [temperature, location] #used for writing all of the data

schedule.every(2.5).seconds.do(temperature.update_data)
schedule.every(5).seconds.do(location.update_data)


#get status initially
tasks.get_status(variable_instance)

#run tasks
while True:
    schedule.run_pending()
    time.sleep(1)
