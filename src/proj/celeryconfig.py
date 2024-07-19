
# broker_url = 'pyamqp://'
# result_backend = 'rpc://'

task_serializer = 'json'
result_serializer = 'json'
result_expires = 3600
accept_content = ['json']
timezone = 'Europe/Oslo'
enable_utc = True

# To demonstrate the power of configuration files, 
# this is how you’d route a misbehaving task to a dedicated queue:
# task_routes = {
#     'tasks.add': 'low-priority'
# }
# Or instead of routing it you could rate limit the task instead, so that only 10 
# tasks of this type can be processed in a minute (10/m):
# task_annotations = {
#     'tasks.add': {'rate_limit': '10/m'}
# }