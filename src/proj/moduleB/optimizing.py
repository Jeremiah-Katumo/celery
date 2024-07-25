from kombu import Exchange, Queue

from . import tasks

#### General Settings

### Using Transient Queues
# Queues created by Celery are persistent by default. This means that the broker 
# will write messages to disk to ensure that the tasks will be executed even if 
# the broker is restarted.
# But in some cases it’s fine that the message is lost, so not all tasks require 
# durability. You can create a transient queue for these tasks to improve performance:
task_queues = (
    Queue('celery', routing_key='celery'),
    Queue('transient', Exchange('transient', delivery_mode=1),
          routing_key='transient', durable=False)
)
# or by using task_routes:
task_routes = {
    'proj.task.add': {'queue': 'celery', 'delivery_mode': 'transient'}
}
# The delivery_mode changes how the messages to this queue are delivered. A value
# of one means that the message won’t be written to disk, and a value of two (default) 
# means that the message can be written to disk.
tasks.add.apply_async(args, queue='transient')