pyfunhook
=========
In short, this library tries to provide these features for #python #decorator
- ease the work for implementing a decorator.
- propagation of decorators to subclasses.

## Contents
- [QuickStart](https://github.com/mission-liao/pyfunhook/edit/master/README.md#quickstart)
- [Motivation](https://github.com/mission-liao/pyfunhook/edit/master/README.md#motivation)
- [Suportability](https://github.com/mission-liao/pyfunhook/edit/master/README.md#supportability)

---------

### QuickStart
Here is a class with a function
```python
class A(object):
  def func(self, n, s, is_debug=True):
    return s + str(n)
```
You can write a hook like this
```python
class H(funhook.Hook):
  def __init__(self, bias):
    super(H, self).__init__(bias)
    self.accept_pos_args = True  # accept positional args
    self.accept_kwargs = True # accept keyword arguments
    self.accept_ret = True # accept return value in 'after' function
    
    self.bias_ = bias
    
  def before(self, bnd, n, s, is_debug=True):
    """
    this callback would be called before the wrapped function
    
    bias 'n' with self.bias_, this biased 'n' would be past to the wrapped function.
    turning on debug by setting 'is_debug' to True.
    """
    return (n+self.bias_, s, ), {"is_debug": True}
    
  def after(self, bnd, ret, n, s, is_debug=True):
    """
    this callback would be called after the wrapped function.
    you can patch the return value here.
    """
    return ret, (n, s, ), {"is_debug": is_debug}
```
and decorate your function in this way
```python
class A(object):
  # it's here!!!!
  @funhook.attach_([H(1000), ])
  def func(self, n, s, is_debug=True):
    return s + str(n)
```

### Motivation
This section describes motivation of this library.
#### Writing 'Hook' is easier than writing 'Decorator'
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
    self.accept_pos_args = True
    
  def before(self, bnd, s, app, n):
    # patch these paramenters in this way
    return (s+'_patched', app, n+1,)
    
  def after(self, bnd, ret, s, app, n):
    # patch return value in this way
    return ret+'_patched_return', (s, app, n, )

# decorate that function with your hook
@funhook.attach_([youHook()])
def fn(s, app, n, is_debug=False, not_done_yet=True, bypass_check=True):
  ...
```
The co-use with classmethod and staticmethod is a more complex scenario. Mainly because they are descriptors but not callables.
Therefore, if you want your decorator compatible with classmethod and staticmethod, you have some additional work to do.

Some benefit:
- you don't have to declare all arguments, only declare those you need to patched.
- we handle the case the co-use you hooks with '@classmethod' and '@staticmethod'
- clear and uniform way to implement a decorator.
 
#### Hooks are inheritable Decorators
Maybe you just implement a decorator to log the enter/exit of functions in one class, like this:
```python
class A(object):
  @log
  def func_1(self):
    pass

  @log
  def func_2(self):
    pass
    
  @log
  def func_3(self):
    pass
    
  ...
...
```
It works well for class A. However, class A is a base class and there are 10 classes subclass class A.
It's painful if you want to log enter/exit of all methods in those subclasses.

Now we can ease this problem with some builtin hooks __adapt_hook_from__ for classes in our library if you implemnt your log decorator with our hooks.
```python
@funhook.setup_([adapt_hook_from()])
class A_sub_1(A):
  def func_1(self):
    pass

@funhook.setup_([adapt_hook_from()])
class A_sub_2(A):
  def func_2(self):
    pass

@funhook.setup_([adapt_hook_from()])
class A_sub_3(A):
  def func_3(self):
    pass
```
*A_sub_1().func_1()*, *A_sub_2().func_2()*, *A_sub_3().func_3()* would be wrapped by your hook to log enter/exit automatically.

### Supportability
We only support python3.3+ upon now.
