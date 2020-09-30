#schedule import
import schedule
import time

#enviroment variables import
import os


#inisitalize variable
from utils.variable import variable
variable_instanse = variable()

#initialize logging
from utils.logging import logger
logger_instance = logger(variable_instanse)
variable_instanse.logger_class = logger_instance


#initialize octoprint companion
from utils.octoprint import octoprint
octoprint_instanse = octoprint(variable_instanse)
variable_instanse.octoprint_class = octoprint_instanse

#initialize storage companion
from utils.storage import s3
s3_instanse = s3(variable_instanse)
variable_instanse.s3_class = s3_instanse

#import tasks and schedule tasks
import tasks
schedule.every(1).seconds.do(tasks.get_status, variable_instanse)

#run tasks
#while True:
#    schedule.run_pending()
#    time.sleep(1)