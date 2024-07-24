# Canvas: Designing Work-flows

from celery import signature, chain, group, chord
from . import tasks

### Signatures
# create a signature for the add task
signature('tasks.addition', args=(2, 2), countdown=10)

# or you can create one using task'ssignature method
tasks.addition.signature((2, 2), countdown=10)

### Partials
# with a signature you can execute the task in a worker
tasks.addition.s(2, 2).delay()
tasks.addition.s(2, 2).apply_async(countdown=1)

# Any arguments added will be prepended to the args in the signature:
partial = tasks.addition.s(2)  # incomplete signature
partial.delay(4)    #  4 + 2
partial.apply_async((4,))   # same

# Any keyword arguments added will be merged with the kwargs in the signature, 
# with the new keyword arguments taking precedence:
s = tasks.addition(2, 3)
s.delay(debug=True)                   # -> tasks.addition(2, 2, debug=True)
s.apply_async(kwargs={'debug': True}) # same

s = tasks.addition.signature((2, 2), countdown=10)
s.apply_async(countdown=1)   # countdown is now 1

s = tasks.addition.s(2)
s.clone(args=(4,), kwargs={'debug': True})

### Immutability
tasks.addition.apply_async((2, 2), link=reset_buffers.signature(immutable=True))
# The .si() shortcut can also be used to create immutable signatures:
tasks.addition.apply_async((2, 2), link=reset_buffers.si())


### Callbacks
# Callbacks can be added to any task using the link argument to apply_async:
tasks.apply_async((2, 2), link=other_task.s())

### Chaining
res = chain(tasks.addition.s(2, 2), tasks.addition.s(4), tasks.addition.s(8))()
res.get()
# also written using pipes
(tasks.addition.s(2, 2) | tasks.addition.s(4) | tasks.addition.s(8))().get()

# Immutable signatures
res.get()
res.parent.get()
res.parent.parent.get()

## Simple group
res = group(tasks.addition(i, i) for i in range(10))()
res.get(timeout=1)

## simple chord
res = chord((tasks.addition.s(i, i) for i in range(10)), tsum.s())()
res.get()