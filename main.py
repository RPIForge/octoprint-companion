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
schedule.every(30).seconds.do(tasks.get_status, variable_instance)
schedule.every(60).seconds.do(tasks.get_information, variable_instance)
schedule.every(30).seconds.do(tasks.get_temperature, variable_instance)

#run tasks
#while True:
#    schedule.run_pending()
#    time.sleep(1)