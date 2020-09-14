#cron import
import schedule
import time

#inisitalize variable
from utils.variable import variable
variable_instanse = variable()

#initialize octoprint
from utils.octoprint import octoprint
octoprint_instanse = octoprint(variable_instanse)
variable_instanse.octoprint = octoprint_instanse

#import tasks
import tasks
schedule.every(1).seconds.do(tasks.get_status, variable_instanse)


while True:
    schedule.run_pending()
    time.sleep(1)