
from celery import Celery

import celeryconfig

# app = Celery('proj',
#              broker='pyamqp://',
#              backend='rpc://',
#              include=['proj.tasks'])

class MyCelery(Celery):
    def gen_task_name(self, name, module):
        if module.endswith('.tasks'):
            module = module[:-6]
        return super().gen_task_name(name, module)
    
app = MyCelery('main')

# Optional configuration
app.config_from_object(celeryconfig)

if __name__ == '__main__':
    app.start()