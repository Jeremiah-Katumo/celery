
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