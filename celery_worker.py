from celery import Celery, Task
import sys,os

# sys.path.append(os.getcwd())
from system import create_app
# the app context must be pushed inside the create_app as we are using the create_app to create the celery worker
# celery = Celery(__name__,broker=CELERY_BROKER_BACKEND,backend=CELERY_RESULT_BACKEND)
app = create_app()
celery_app:Celery = app.extensions["celery"]
"""
    celery -A celery_worker.celery_app worker --loglevel INFO -P solo
    here celery_worker is the module name and celery_app is the object
"""