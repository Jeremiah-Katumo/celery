
from celery.signals import after_task_publish, celeryd_after_setup, celeryd_init
from celery import Celery
from celery import signals
from celery.bin.base import Option

from ..celery import app

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
@celeryd_after_setup.connect
def setupp_direct_queue(sender, instance, **kwargs):
    queue_name = '{0}.dq'.format(sender)  # sender is the nodename of the worker
    instance.app.amqp.queues.select_Add(queue_name)

@celeryd_init.connect(sender='worker@mail.com')
def configure_workers(sender=None, conf=None, **kwargs):
    conf.task_default_rate_limit = '10/m'

    # Example: configure the number of workers based on the number of CPU cores
    num_workers = len(conf.CELERY_WORKER_CONCURRENCY_LIMIT)
    conf.CELERY_WORKER_CONCURRENCY = num_workers


@celeryd_init.connect
def configure_workers(sender=None, conf=None, **kwargs):
    if sender in ('worker1@mail.com', 'worker2@mail.com'):
        conf.task_default_rate_limit = '5/m'
    if sender == 'worker4@mail.com':
        conf.worker_prefetch_multiplier = 0


### Command Signals
app.user_options['preload'].add(Option(
    '--monitoring', action='store_true',
    help='Enable our external monitoring utility, blahblah',
))

@signals.user_preload_options.connect
def handle_preload_options(options, **kwargs):
    if options['monitoring']:
        enable_monitoring()