
import sys
import celery
import logging
import redis
import errno
import celery.signals
from celery import states
from celery.exceptions import Ignore, Reject
from celery.utils.log import get_task_logger
from twitter import Twitter

from .database import DatabaseTask
# from twitter import FailWhaleError   # celery version 4.0

from ..celery import app

logger = get_task_logger(__name__)

@app.task(bind=True)
def addition(self, x, y):
    old_outs = sys.stdout, sys.stderr
    rlevel = self.app.conf.worker_redirect_stdouts_level
    try:
        self.app.log.redirect_stdouts_to_logger(logger, rlevel)
        print('Adding {0} + {1}'.format(x, y))
        return x + y
    finally: 
        sys.stdout, sys.stderr = old_outs

# If a specific Celery logger you need is not emitting logs, you should check that 
# the logger is propagating properly. In this example “celery.app.trace” is enabled 
# so that “succeeded in” logs are emitted:
@celery.signals.after_setup_logger.connect
def on_after_setup_logger(**kwargs):
    logger = logging.getLogger('celery')
    logger.setLevel(logging.INFO)
    logger.propagate = True
    logger = logging.getLogger('celery.app.trace')
    logger.propagate = True


# Retrying
# app.Task.retry() can be used to re-execute the task, for example in the event of recoverable errors.
@app.task(bind=True)
def send_twitter_status(self, oauth, tweet):
    try:
        twitter = Twitter(oauth)
        twitter.update_status(tweet)
    except (Twitter.FailWhaleError, Twitter.LoginError) as exc:
        raise self.retry(exc=exc)

# @app.task(autoretry_for=(FailWhaleError,), retry_kwargs={'max_retries': 5})
# def refresh_timeline(user):
#     return twitter.refresh_timeline(user)

@app.task
def refresh_timeline(self, user, oauth):
    try:
        twitter = Twitter(oauth)
        twitter.refresh_timeline(user)
    except Twitter.FailWhaleError as exc:
        raise self.retry(exc=exc, max_retries=5)


### CUstom States
# The name of the state should be unique and usually an uppercase string
@app.task(bind=True)
def upload_files(self, filenames):
    for i, file in enumerate(filenames):
        if not self.request.called_directly:
            self.update_state(
                state='PROGRESS',
                meta={'current': i, 'total': len(filenames)}
            )


### Creating pickleable exceptions
# To make sure that your exceptions are pickleable the exception MUST provide the 
# original arguments it was instantiated with in its .args attribute. The simplest 
# way to ensure this is to have the exception call Exception.__init__.
class HttpError(Exception):
    def __init__(self, status_code, headers=None, body=None):  # (self, *args: object) -> None:
        self.status_code = status_code
        self.headers = headers
        self.body = body
        # Exception.__init__(self, status_code)
        # Exception.__init__(self, *args)
        super(HttpError, self).__init__(status_code, headers, body)


### Semipredicates
### Ignore

# The task may raise Ignore to force the worker to ignore the task. This means that 
# no state will be recorded for the task, but the message is still acknowledged 
# (removed from queue).
# This can be used if you want to implement custom revoke-like functionality, or 
# manually store the result of a task.

# Keeping revoked tasks in a Redis set:
@app.task(bind=True)
def some_task(self):
    if redis.ismember('tasks.revoked', self.request.id):
        raise Ignore()
# Store results manually:
@app.task(bind=True)
def get_tweets(self, user):
    timeline = Twitter.get_timeline(user)
    if not self.request.called_directly:
        self.update_state(state=states.SUCCESS, meta=timeline)
    raise Ignore()


### Reject

# The task may raise Reject to reject the task message using AMQPs basic_reject 
# method. This won’t have any effect unless Task.acks_late is enabled.
# Reject can also be used to re-queue messages, but please be very careful when 
# using this as it can easily result in an infinite message loop.

# Example using reject when a task causes an out of memory condition:
@app.task(bind=True, acks_late=True)
def render_Scene(self, path):
    file = get_file(path)
    try:
        renderer.render_scene(file)

    # if the file is too big to fit in memory
    # we reject it so that it's redelivered to the dead letter exchange
    # and we can manually inspect the situation.
    except MemoryError as exc:
        raise Reject(exc, requeue=False)
    except OSError as exc:
        if exc.errno == errno.ENOMEM:
            raise Reject(exc, requeue=False)
        
    # For any other error we retry after 10 seconds.
    except Exception as exc:
        raise self.retry(exc, countdown=10)

# Example re-queuing the message:
app.task(bind=True, acks_late=True)
def requeues(self):
    if not self.request.delivery_info['redelivered']:
        raise Reject('no reason', requeue=True)
    print('received two times')
    

## Per task usage
# The above can be added to each task like this:

@app.task(base=DatabaseTask, bind=True)
def process_rows(self: task):
    for row in self.db.table.all():
        process_rows(row)

## App-wide usage

## Requests and Custom requests

