pyfunhook
=========
In short, this library tries to provide these features for #python #decorator
- ease the work for implementing a decortor.
- propagation of decorators to subclasses.

Writing 'Hook' is easier than writing 'Decorator'
---------
"Decorator" is a perfect syntax-sugar in python. However, it's not that easy
to write one for real world library. Imaging to write a decorator to 'patch'
some parameter and check return value of this function:

```python
def fn(s, app, n, is_debug=False, not_done_yet=True, bypass_check=True):
  ...
```
An implementer of a decorator for such function would have to take care of all
arguments, or try to unpack arguments that needed by themselves. Like this:
```python
# one way
def dec(fn):
  def new_fn(s, app, n, is_debug=False, not_done_yet=True, bypass_check=True):
    # ..... do something
    return fn(s, app, .....)
    
  return new_fn
  
# another way
def dec2(fn):
  def new_fn(*a_, **k_):
    # unpack parameters by yourselves
    return fn(*a_, **k_)
    
  return new_fn

```

Yes, we can ease this problem in this way.
```python
class youHook(funhook.Hook):
  def __init__(self):
    super(youHook, self).__init__()
    self.accept_ret = True
    self.accept_kwargs = False
    self.accept_self = False
    self.accept_pos_args = True
    
  def before(self, s, app, n):
    # patch these paramenters in this way
    return (s+'_patched', app, n+1,)
    
  def after(self, ret, s, app, n):
    # patch return value in this way
    return ret+'_patched_return', (s, app, n, )
    
# decorate that function with your hook
@funhook.attach_([youHook()])
def fn(s, app, n, is_debug=False, not_done_yet=True, bypass_check=True):
  ...
```
Some benefit:
- you don't have to declare all arguments, only declare those you need to patched.
- clear and uniform way to implement a decorator.
 
Hooks are inheritable Decorators
--------
This part is not finished and designed yet. Still ongoing!
