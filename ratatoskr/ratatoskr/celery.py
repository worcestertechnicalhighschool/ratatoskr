import os 
from celery import Celery, shared_task
from django.core.mail import send_mail

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ratatoskr.settings')

app = Celery('ratatoskr')

# Using a string here means the worker doesn't have to serialize the conifiguration
# object to child processes. 
#   - namespace='CELERY' means all celery-related configuration keys
#     should have a `CELERY_` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

@app.task(bind=True)
def send_mail_task(*args, **kwargs):
    print("i do it")
    send_mail(
        kwargs['subject'],
        kwargs['message'],
        kwargs['from_email'],
        kwargs['to_email'],
        fail_silently=kwargs['fail_silently'],
    )