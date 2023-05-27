import os
from celery import Celery
from datetime import timedelta

# copied from managr.py
# set the default Django setting module for the 'celery'app
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
#you change the name here
app = Celery("config")

#read config from Django settings, the CELERY namespace would make celery
app.config_from_object("django.conf:settings", namespace="CELERY")
#load tasks.py in django apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
	"send_new_products-every_day": {
		"task": "main.tasks.send_new_products",
		"schedule": timedelta(days=1)
	}
}