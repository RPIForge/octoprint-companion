

#schedule import
import schedule
import time

#enviroment variables import
import os



#inisitalize variable
from utils.variable import variable
variable_instanse = variable(os.getenv('NAME',"generic_test"))

#initialize logging
from utils.logging import logger
logger_instance = logger(variable_instanse)
variable_instanse.logger_class = logger_instance


#initialize octoprint
from utils.octoprint import octoprint
octoprint_instanse = octoprint(variable_instanse)
variable_instanse.octoprint_class = octoprint_instanse

#import tasks
import tasks
schedule.every(1).seconds.do(tasks.get_status, variable_instanse)


while True:
    schedule.run_pending()
    time.sleep(1)