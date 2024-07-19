# Instantiation
from celery import Task
from celery.app import task

from ..celery import app

# A task is not instantiated for every request, but is registered in the task 
# registry as a global instance.
# This means that the __init__ constructor will only be called once per process, 
# and that the task class is semantically closer to an Actor.

class NaiveAuthenticateServer(Task):

    def __init__(self):
        self.users = {'george': 'password'}

    def run(self, username, password):
        try:
            return self.users[username] == password
        except KeyError:
            return False
        
# This can also be useful to cache resources, For example, a base Task class that 
# caches a database connection:

class DatabaseTask(Task):
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = Database.connect()
        return self._db
    
