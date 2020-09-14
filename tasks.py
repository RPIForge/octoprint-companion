from celery import Celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task



app = Celery('tasks', broker='redis://guest@localhost//')

@periodic_task(run_every=(1.0), name="printing_stuff", ignore_result=True)
def add():
    print(1)