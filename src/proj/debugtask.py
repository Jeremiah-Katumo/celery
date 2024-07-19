
from celery import Task

class DebugTask(Task):
    def on_success(self, retval, task_id, *args, **kwargs):
        print(f'Task {task_id} executed successfully with result: {retval}')
        return self.run(*args, **kwargs)
# Do not use super().run, super().on_success
# class DebugTask(Task):
#     def on_success(self, retval, task_id, *args, **kwargs):
#         print(f'Task {task_id} executed successfully with result: {retval}')
#         return super().on_success(retval, task_id, *args, **kwargs)
