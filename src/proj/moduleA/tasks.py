
from celery import Task
from celery.utils.log import get_task_logger

import debugtask
from ..celery import app
from ..models import User


@app.task(queue='hipri')
def hello(to):
    return 'hello {0}'.format(to)

@app.task(base=debugtask)
def add(x, y):
    return x + y

@app.task(base=debugtask)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(serializer='json')
def create_user(username, password):
    User.objects.create(username=username, password=password)

# Bound tasks
# A task being bound means the first argument to the task will always be the task instance (self), just like Python bound methods:
logger = get_task_logger(__name__)

@app.task(bind=True)
def log_task_start(self, x, y):
    logger.info(self.request.id)

@app.task
def log_task_add(x, y):
    logger.info('Adding {0} + {1}'.format(x, y))
    return x + y

# Task Inheritance
class MyTask(Task):
    def on_failure(self, exc, task_id, einfo, *args, **kwargs):
        print('{0!r} failed: {1!r}'.format(task_id, exc))

@app.task(base=MyTask)
def my_task(x, y):
    raise KeyError()

# An example task accessing information in the context is:
@app.task(bind=True)
def dump_context(self, x, y):
    print('Executing task id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format(self.request))






# result = add.delay(4, 4)
# result.ready()
# result.get(timeout=1)
# result.get(propagate=False)
# result.traceback
# Configure default serializer
# app.conf.task_serializer = 'json'
# app.conf.update(
#     task_serializer='json',
#     accept_content=['json'],  # Ignore other content
#     result_serializer='json',
#     timezone='EAT',
#     enable_utc=True,
# )
# app.config_from_object('celeryconfig')