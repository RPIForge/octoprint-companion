#schedule import
import schedule
import time

#enviroment variables import
import os


#inisitalize variable
from utils.variable import variable
variable_instance = variable()
variable_instance.read_env()


#initialize logging
from utils.logging import logger
logger_instance = logger(variable_instance)
variable_instance.logger_class = logger_instance

#initialize octoprint companion
from utils.octoprint import octoprint
octoprint_instance = octoprint(variable_instance)
variable_instance.octoprint_class = octoprint_instance

#initialize storage companion
from utils.storage import s3
s3_instance = s3(variable_instance)
variable_instance.s3_class = s3_instance

#initialize website companion
from utils.website import website
website_instance = website(variable_instance)
variable_instance.website_class = website_instance

#import tasks and schedule tasks
import tasks
schedule.every(5).seconds.do(tasks.get_status, variable_instance)
schedule.every(2.5).seconds.do(tasks.get_temperature, variable_instance)
schedule.every(2.5).seconds.do(tasks.get_location, variable_instance)
schedule.every(10).seconds.do(tasks.get_end_time, variable_instance)
schedule.every(10).seconds.do(tasks.update_website, variable_instance)

#get status initially
tasks.get_status(variable_instance)

#run tasks
while True:
    schedule.run_pending()
    time.sleep(1)
