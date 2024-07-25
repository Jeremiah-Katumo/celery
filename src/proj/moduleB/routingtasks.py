
from kombu import Queue, Exchange, binding
from kombu.common import Broadcast
from celery.schedules import crontab
from feeds.tasks import import_feed

from ..celery import app
from . import tasks


### Automatic Routing
app.conf.task_routes = {'feed.tasks.*': {'queue': 'feeds'}}

task_routes = ([
    ('feed.tasks.*', {'queue': 'feeds'}),
    ('web.tasks.*', {'queue': 'web'}),
    (re.compile(r'(video|image)\.tasks\..*'), {'queue': 'media'}),
],)

app.conf.task_default_queue = 'default'

# A queue named “video” will be created with the following settings:
{'exchange': 'video',
 'exchange_type': 'direct',
 'routing_key': 'video'}

### Manual Routing
app.conf.task_default_queue = 'default'
app.conf.task_queues = (
    Queue('default', routing_key='task.#'),
    Queue('feed_tasks', routing_key='feed.#'),
)
app.conf.task_default_exchange = 'tasks'
app.conf.task_default_exchange_type = 'topic'
app.conf.task_default_routing_key = 'task.default'

# To route a task to the feed_tasks queue, you can add an entry in the task_routes setting:
task_routes = {
    'feeds.tasks.import_feed': {
        'queue': 'feed_tasks',
        'routing_key': 'feed.import',
    }
}

# You can also override this using the routing_key argument to Task.apply_async(), or send_task():
import_feed.apply_async(args=['http://cnn.com/rss'],
                        queue='feed_tasks',
                        routing_key='feed.import')

# If you have another queue but on another exchange you want to add, just specify 
# a custom exchange and exchange type:
app.conf.task_queues = (
    Queue('feed_tasks', routing_key='task.#'),
    Queue('regular_tasks', routing_key='feed.#'),
    # Queue('custom_queue', exchange='custom_exchange', exchange_type='direct'),
    Queue(
        'image_tasks', 
        exchange=Exchange('mediatasks', type='direct'),
        roouting_key='image.compress'
    ),
)


### AMQP Primer
## Exchanges, queues, and routing keys
# The steps required to send and receive messages are:
    # Create an exchange
    # Create a queue
    # Bind the queue to the exchange.
# Celery automatically creates the entities necessary for the queues in task_queues 
# to work (except if the queue’s auto_declare setting is set to False).
app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('videos', Exchange('media'), routing_key='media.video'),
    Queue('images', Exchange('media'), routing_key='media.image'),
)
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'default'


### Defining Queues
# In Celery available queues are defined by the task_queues setting.
default_exchange = Exchange('default', type='direct')
media_exchange = Exchange('media', type='direct')

app.conf.task_queues = (
    Queue('default', default_exchange, routing_key='default'),
    Queue('videos', media_exchange, routing_key='media.video'),
    Queue('images', media_exchange, routing_key='media.image'),
)
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# Multiple bindings to a single queue are also supported. Here’s an example of 
# two routing keys that are both bound to the same queue:
media_exchange = Exchange('media', type='direct')

CELERY_QUEUES = (
    Queue('media', [
        binding(media_exchange, routing_key='media.video'),
        binding(media_exchange, routing_key='media.image'),
    ])
)


### Routers
# A router is a function that decides the routing options for a task.
# All you need to define a new router is to define a function with the signature 
# (name, args, kwargs, options, task=None, **kw): 
def route_task(name, args, kwargs, options, task=None, **kw):
    if name == 'myapp.tasks.compress_video':
        return {'exchange': 'video',
                'exchange_type': 'topic',
                'routing_key': 'video.compress'}
    
# For simple task name -> route mappings like the router example above, you can 
# simply drop a dict into task_routes to get the same behavior:
task_routes = {
    'myapp.tasks.compress_video': {
        'queue': 'video',
        'routing_key': 'video.compress',
    },
}

# You can also have multiple routers defined in a sequence:
task_routes = [
    route_task,
    {
        'myapp.tasks.compress_video': {
            'queue': 'video',
            'routing_key': 'video.compress',
        },
    },
]

# If you're using Redis or RabbitMQ you can also specify the queue's default priority in the route.
task_routes = {
    'myapp.tasks.compress_video': {
        'queue': 'video',
        'routing_key': 'video.compress',
        'priority': 10,
    },
}
# Similarly, calling apply_async on a task will override that default priority.
tasks.add.apply_async(priority=0)


### Broadcast
# Now the tasks.reload_cache task will be sent to every worker consuming from this queue.
app.conf.task_queues = (Broadcast('broadcast_tasks'),)
app.conf.task_routes = {
    'tasks.reload_cache': {
        'queue': 'broadcast_tasks',
        'exchange': 'broadcast_tasks'
    }
}

# Here is another example of broadcast routing, this time with a celery beat schedule:
app.conf.task_queues = (Broadcast('broadcast_tasks'),)

app.conf.beat_schedule = {
    'test-task': {
        'task': 'tasks.reload_cache',
        'schedule': crontab(minute='*/15'),  # Run every 15 minutes
        'options': {'queue': 'broadcast_tasks'},  # Use the broadcast_tasks queue
    }
}