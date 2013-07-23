'''
Created on Jul 22, 2013

@author: Mission Liao
'''


class setup(object):

    def __init__(self):
        pass
    
    def __call__(self):
        pass


class Hook(object):
    """
    base hook implementation
    ------------------------
    Guide for writing hooks

    1. For writing hooks to be attached before a function
       is called.

       ex.
       class myhook(funhook.Hook):
           def __init__(self ...):
               super...
               
           def __call__(self, a, b, c, isDebug=False):
               ... do something
               return (a, b, c,), {"isDebug": isDebug}

       @funhook.before([myhook(...)])
       def myfunc(a, b, c, isDebug=False):
           pass

       You can pass options to your hook in __init__.
       
       ex.
       class myhook(funhook.Hook):
           def __init__(self, allow_rethrow=True):
               ...
               
       @funhook.before([myhook(allow_rethrow=False)])
       def myfunc(...)
       
       If the function to be wrapped coming with a massive
       amount of keyword-arguments, and you don't want to
       overwrite any one of them, you can skip them in your
       hook by turning off 'accept_kwargs' option in __init__.
       And, please note that don't return packed kwargs as {}
       in this case.

       ex.
       class myhook(funhook.Hook):
           def __init__(self ...):
               super...
               self.accept_kwargs = False
               
           def __call__(self, a, b, c, isDebug=False):
               ... do something
               return (a, b, c,)
        
       
    2. The prototype for hooking "after" the function is almost
       identical to original function and prepend a "return" value.

       ex.
       class myhook(funhook.Hook):
           ...
           def __call__(self, ret, a, b, c, isDebug=False):
               ... do something
               return ret, (a, b, c,), {"isDebug": isDebug}

       @funhook.after([myhook])
       def myfunc(a, b, c, isDebug=Fales):
           pass
    """
  
    # standard error message for wrong type with option 
    error_type_not_bool = "Please assign options with bool." 

    def __init__(self):
        # accept kwargs defaultly
        self.opt_accept_kwargs = True 
        # hooks are "before" type by default
        self.opt_accept_ret = False

    @property
    def accept_ret(self):
        return self.opt_accept_ret
    
    @accept_ret.setter
    def accept_ret(self, v):
        if type(v) != bool:
            raise TypeError(Hook.error_type_not_bool)
        
        self.opt_accept_ret = v
        
    @property
    def accept_kwargs(self):
        return self.opt_accept_kwargs
    
    @accept_kwargs.setter
    def accept_kwargs(self, v):
        if type(v) != bool:
            raise TypeError(Hook.error_type_not_bool)
        
        self.opt_accept_kwargs = v

 
class HookManager(object):
    """
    base hook-mamanger implementation
    """
    def __init__(self, hooks, accept_ret):
        # make sure every hook is subclass from 'Hook'
        for h in hooks:
            if not issubclass(type(h), Hook):
                raise TypeError("Please implement hooks as funhook.Hook class.")

            h.accept_ret = accept_ret

        self.hooks = hooks

    @staticmethod 
    def _inner_call(hooks, ret, args, kwargs):
        """
        loop through hooks
        """
        a_ = args
        k_ = kwargs
        for h in hooks:
            try:
                k2_ = None
                if h.opt_accept_ret == True:
                    if h.opt_accept_kwargs == True:
                        ret, a_, k2_ = h(ret, *a_, **k_)
                    else:
                        ret, a_ = h(ret, *a_)
                else:
                    if h.opt_accept_kwargs == True:
                        a_, k2_ = h(*a_, **k_)
                    else:
                        a_ = h(*a_)

                if k2_:
                    k_.update(k2_)
                    
            except Exception as e:
                # TODO: how to handle error in hooks?
                raise e

        return ret, a_, k_


class before(HookManager):
    """
    A decorator to hook "before" call into a function.
    
    """
    def __init__(self, hooks):
        super(before, self).__init__(hooks, False)

    def __call__(self, fn):
        def new_fn(*args, **kwargs):
            _, a_, k_ = HookManager._inner_call(self.hooks, None, args, kwargs)
            return fn(*a_, **k_)

        return new_fn


class after(HookManager):
    """
    A decorator to hook "after" call into a function.
    
    """
    def __init__(self, hooks):
        super(after, self).__init__(hooks, True)

    def __call__(self, fn):
        def new_fn(*args, **kwargs):

            """
            for functions without value, ret here would
            receive None. It's up to hooks to handle such case
            """
            try:
                ret = fn(*args, **kwargs)
            except Exception as e:
                # TODO: how to handle exception from
                # wrapped function. Should we hold this
                # exception and raise it after looping hooks.
                raise e
           
            ret, _, _ = HookManager._inner_call(self.hooks, ret, args, kwargs)
            return ret

        return new_fn
