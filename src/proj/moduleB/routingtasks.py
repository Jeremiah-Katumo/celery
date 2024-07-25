
from kombu import Queue, Exchange
from feeds.tasks import import_feed

from ..celery import app


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