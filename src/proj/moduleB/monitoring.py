from pprint import pformat
from celery import Celery
from celery.events.snapshot import Polaroid


class DumpCam(Polaroid):
    clear_after = True  # clear after flush (incl, state.event_count).

    def on_shutter(self, state):
        if not state.event_count:
            # No new events since last snapshot.
            return
        print('Workers: {0}'.format(pformat(state.workers, indent=4)))
        print('Tasks: {0}'.format(pformat(state.tasks, indent=4)))
        print('Total: {0.event_count} events, {0.task_count} tasks'.format(
            state))
        
def main(app, freq=1.0):
    state = app.events.State()
    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={'*': state.event})
        with DumpCam(state, freq=freq):
            recv.capture(limit=None, timeout=None)


### Real-time processing
# To process events in real-time you need the following
    # An event consumer (this is the Receiver)
    # A set of handlers called when events come in.
        # You can have different handlers for each event type, or a catch-all 
        # handler can be used (‘*’)
    # State (optional)
# app.events.State is a convenient in-memory representation of tasks and workers 
# in the cluster that’s updated as events come in.
# It encapsulates solutions for many common things, like checking if a worker is 
# still alive (by verifying heartbeats), merging event fields together as events 
# come in, making sure time-stamps are in sync, and so on.
def my_monitor(app):
    state = app.events.State()

    def announce_failed_tasks(event):
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event['uuid'])

        print('TASK FAILED: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-failed': announce_failed_tasks,
                '*': state.event,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

# You can listen to specific events by specifying the handlers:
def my_monitor(app):
    state = app.events.State()

    def announce_failed_tasks(event):
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event['uuid'])

        print('TASK FAILED: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-failed': announce_failed_tasks,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)
        

if __name__ == '__main__':
    app = Celery(broker='amqp://guest@localhost//')
    main(app)