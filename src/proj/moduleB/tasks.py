
import sys
import celery
import logging
import celery.signals
from celery.utils.log import get_task_logger
from twitter import Twitter
# from twitter.exceptions import FailWhaleError   # celery version 4.0

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