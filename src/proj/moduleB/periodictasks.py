from celery.schedules import crontab, solar

from ..celery import app
from . import tasks


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds
    sender.add_periodic_tasks(10.0, tasks.test.s(), name='add every 10')

    # Calls test('hello') every 30 seconds.
    # It uses the same signature of previous task, an explicit name is
    # defined to avoid this task replacing the previous one defined.
    sender.add_periodic_task(30.0, tasks.test.s('hello'), name='add every 30')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, tasks.test.s('world'), expires=10)

    # Executes every Monday morning 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        tasks.test.s('Happy Mondays!')
    )

### Crontab Schedules
# If you want more control over when the task is executed, for example, a particular 
# time of day or day of the week, you can use the crontab schedule type:
app.conf.beat_schedule = {
    # Executes every Monday Morning at 7:30 a.m.
    'add-every-monday-morning': {
        'task': 'tasks.add',
        'schedule': crontab(hour=7, minute=30, day_of_week=1),
        'args': (16, 16),
    }
}

### Solar Schedules
# If you have a task that should be executed according to sunrise, sunset, dawn or dusk, 
# you can use the solar schedule type: solar(event, latitude, longitude)
app.conf.beat_schedule = {
    # Executes at sunset in Melbourne
    'add-at-melbourne-sunset': {
        'task': 'tasks.add',
        'schedule': solar('sunset', -37.81753, 144.96715),
        'args': (16, 16)
    }
}