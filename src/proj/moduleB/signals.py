
from celery.signals import after_task_publish, celeryd_after_setup


### Task Signals
@after_task_publish.connect(sender='tasks.add')
def task_sent_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    info = headers if 'task' in headers else body
    print("after_task_publish for task id {info[id]}".format(
        info=info,
    ))


### Worker Signals
@celeryd_after_setup.connect()