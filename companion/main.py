#
# Main File. This file initializes all classes and then starts running tasks
#

#inisitalize variable
from utils.variable import variable_instance

#initialize logging
from utils.logging import logger
logger_instance = logger(variable_instance)
variable_instance.logger_class = logger_instance

#update variables from env file
variable_instance.read_env()

#initialize octoprint companion
from utils.octoprint import octoprint
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

#initiazlize mtconnect
from utils.connectors import mtconnect_adapter
variable_instance.mtconnect = mtconnect_adapter(variable_instance)

from utils.connectors import start_opcua_adapter
start_opcua_adapter(variable_instance)

# initialize graphql
from utils.graphql2smip import graphql2smip
variable_instance.data_uploader=graphql2smip()


#initalize flask endpoints
from flask import Flask
from utils.routes import endpoints
app = Flask(__name__)
variable_instance.flask_app = app
variable_instance.flask_app.register_blueprint(endpoints)

#Initalize scheduler
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler(job_defaults={'misfire_grace_time': 1,'coalesce':True})
variable_instance.scheduler = scheduler

#scheduler generic tasks
from utils.tasks import get_end_time, update_databases, update_website
scheduler.add_job(func=lambda: get_end_time(variable_instance), name="get end job",trigger="interval", seconds=10)
scheduler.add_job(func=lambda: update_databases(variable_instance), name="update influxdb job",trigger="interval",  seconds=30)
scheduler.add_job(func=lambda: update_website(variable_instance), name="update website job", trigger="interval", seconds=15)


#initalize data source
from utils.datasources import temperature_data,location_data, status_data
temperature = temperature_data(variable_instance)
status = status_data(variable_instance)
variable_instance.datasources = [temperature, status] #used for writing all of the data

#schedule data sources
scheduler.add_job(func=temperature.run_job, name="temperature job",trigger="interval", seconds=2.5)
scheduler.add_job(func=status.run_job, name="status job", trigger="interval", seconds=5)

#get status initially
status.update_data()

#make sure scheduler stops at exit
atexit.register(lambda: scheduler.shutdown())

#start scheduler
scheduler.start()
