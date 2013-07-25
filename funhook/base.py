'''
Created on Jul 22, 2013

@author: Mission Liao
'''


# TODO: for 'in_' case, try to handle functions
# without return-value.
# TODO: add case for 'inout' trigger
# TODO: add case for invalid trigger value
# TODO: write guide to let users know for multiple return values
# TODO: add dynamic load/unload hooks in HookManager? it seems a complex
#       problem because of multi-access-control.

class setup(object):

    def __init__(self, klass):
        pass
    
    def __call__(self):
        pass


class Hook(object):
    """
    base hook implementation
    ------------------------
    Guide for writing hooks

    1. For writing hooks to be attached in a function
       is called.

       ex.
       class myhook(funhook.Hook):
           def __init__(self ...):
               super...
               
           def before(self, a, b, c, isDebug=False):
               ... do something
               return (a, b, c,), {"isDebug": isDebug}

       @funhook.in_([myhook(...)])
       def myfunc(a, b, c, isDebug=False):
           pass

       You can pass options to your hook in __init__.
       
       ex.
       class myhook(funhook.Hook):
           def __init__(self, allow_rethrow=True):
               ...
               
       @funhook.in_([myhook(allow_rethrow=False)])
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
               
           def before(self, a, b, c, isDebug=False):
               ... do something
               return (a, b, c,)
        
       
    2. The prototype for hooking "out_" the function is almost
       identical to original function and prepend a "return" value.

       ex.
       class myhook(funhook.Hook):
           ...
           def after(self, ret, a, b, c, isDebug=False):
               ... do something
               return ret, (a, b, c,), {"isDebug": isDebug}

       @funhook.out_([myhook])
       def myfunc(a, b, c, isDebug=Fales):
           pass
    """
  
    # standard error message for wrong type with option.
    error_type_not_bool = "Please assign options with bool."
    # standard error message for wrong trigger option. 
    error_not_a_valid_trigger = "Not a valid trigger option"
    # error message for wrong config
    error_wrong_config = "Such configuration is wrong."

    # value of trigger option
    IN_ = 1
    OUT_ = 2
    INOUT_ = 3

    def __init__(self):
        """
        default hook configuration
        """
        # accept positional arguments
        self.opt_accept_pos_args = True
        # accept kwargs defaultly
        self.opt_accept_kwargs = True 
        # hooks are "in" type by default
        self.opt_accept_ret = False
        # accept 'self' as first-parameter
        # when hooked on a class-method.
        # this parameter would be 'None' for
        # unbounded method
        self.opt_accept_self = False
        # if this hook is called 'in_', 'out_'
        # or 'inout_' of the wrapped function.
        self.opt_trigger = Hook.INOUT_

    @property
    def accept_pos_args(self):
        return self.opt_accept_pos_args
    
    @accept_pos_args.setter
    def accept_pos_args(self, v):
        if type(v) != bool:
            raise TypeError(Hook.error_type_not_bool)

        self.opt_accept_pos_args = v
        
    @property
    def accept_ret(self):
        return self.opt_accept_ret
    
    @accept_ret.setter
    def accept_ret(self, v):
        if type(v) != bool:
            raise TypeError(Hook.error_type_not_bool)

        if self.trigger == Hook.IN_ and v == True:
            raise ValueError(Hook.error_wrong_config)

        self.opt_accept_ret = v

    @property
    def accept_kwargs(self):
        return self.opt_accept_kwargs
    
    @accept_kwargs.setter
    def accept_kwargs(self, v):
        if type(v) != bool:
            raise TypeError(Hook.error_type_not_bool)
        
        self.opt_accept_kwargs = v
        
    @property
    def accept_self(self):
        return self.opt_accept_self
    
    @accept_self.setter
    def accept_self(self, v):
        if type(v) != bool:
            raise TypeError(Hook.error_type_not_bool)

        self.opt_accept_self = v

    @property
    def trigger(self):
        return self.opt_trigger
    
    @trigger.setter
    def trigger(self, v):
        if  v != Hook.OUT_ and  \
            v != Hook.IN_ and \
            v != Hook.INOUT_:
            raise TypeError(Hook.error_not_a_valid_trigger + " " + str(v))
        
        if self.accept_ret and v == Hook.IN_:
            raise ValueError(Hook.error_wrong_config)

        self.opt_trigger = v
 
class HookManager(object):
    """
    base hook-mamanger implementation
    """
    def __init__(self, hooks, trigger):
        # make sure this trigger is valid
        Hook().trigger = trigger

        # make sure every hook is subclass from 'Hook'
        for h in hooks:
            if not issubclass(type(h), Hook):
                raise TypeError("Please implement hooks as funhook.Hook class.")

        self._hooks = hooks
        self._trigger = trigger

    def __call__(self, fn):
        return _wrapper(fn, self._hooks, self._trigger, None)

    @staticmethod 
    def _inner_call(hooks, ret, args, kwargs, inst, ctx):
        """
        loop through hooks
        """
        a_ = args
        k_ = kwargs
        for h in hooks:
            # prepare function pointer
            fn_ = None
            if ctx == Hook.IN_:
                fn_ = h.before
            elif ctx == Hook.OUT_:
                fn_ = h.after

            try:
                k2_ = None
                """
                handle
                    Hook.accept_ret,
                    Hook.accept_pos_args,
                    Hook.accept_kwargs,
                    Hook.accept_self,
                options
                """
                # TODO: is there a good way
                # to handle such mass??
                if h.opt_accept_ret:
                    if h.opt_accept_kwargs:
                        if h.opt_accept_pos_args:
                            if h.opt_accept_self:
                                ret, a_, k2_ = fn_(ret, inst, *a_, **k_)
                            else:
                                ret, a_, k2_ = fn_(ret, *a_, **k_)
                        else:
                            if h.opt_accept_self:
                                ret, k2_ = fn_(ret, inst, **k_)
                            else:
                                ret, k2_ = fn_(ret, **k_)
                    else:
                        if h.opt_accept_pos_args:
                            if h.opt_accept_self:
                                ret, a_ = fn_(ret, inst, *a_)
                            else:
                                ret, a_ = fn_(ret, *a_)
                        else:
                            if h.opt_accept_self:
                                ret = fn_(ret, inst)
                            else:
                                ret = fn_(ret)
                else:
                    if h.opt_accept_kwargs:
                        if h.opt_accept_pos_args:
                            if h.opt_accept_self:
                                a_, k2_ = fn_(inst, *a_, **k_)
                            else:
                                a_, k2_ = fn_(*a_, **k_)
                        else:
                            if h.opt_accept_self:
                                k2_ = fn_(inst, **k_)
                            else:
                                k2_ = fn_(**k_)
                    else:
                        if h.opt_accept_pos_args:
                            if h.opt_accept_self:
                                a_ = fn_(inst, *a_)
                            else:
                                a_ = fn_(*a_)
                        else:
                            if h.opt_accept_self:
                                fn_(inst)
                            else:
                                fn_()

                if k2_:
                    k_.update(k2_)

            except Exception as e:
                # TODO: how to handle error in hooks?
                raise e

        return ret, a_, k_


class _wrapper(object):
    """
    The actual function class we return to user
    """
    def __init__(self, fn, hooks, trigger, inst):
        self._fn = fn
        self._hooks = hooks
        self._trigger = trigger
        self._inst = inst
        self._cache_bound_funobj = None

    def __get__(self, obj, obj_type):
        """
        refer to
            http://blog.ianbicking.org/2008/10/24/decorators-and-descriptors/
            
        for more information
        """
        if obj == None:
            return self

        if self._cache_bound_funobj == None:
            new_fn = self._fn.__get__(obj, obj_type)
            self._cache_bound_funobj = self.__class__(new_fn, self._hooks, self._trigger, obj)

        return self._cache_bound_funobj
    
    def __call__(self, *args, **kwargs):
        if self._trigger == Hook.IN_:
            _, a_, k_ = HookManager._inner_call(self._hooks, None, args, kwargs, self._inst, Hook.IN_)
            return self._fn(*a_, **k_)
        elif self._trigger == Hook.OUT_:
            """
            for functions without value, ret here would
            receive None. It's up to hooks to handle such case
            """
            try:
                ret = self._fn(*args, **kwargs)
            except Exception as e:
                # TODO: how to handle exception from
                # wrapped function. Should we hold this
                # exception and raise it after looping hooks.
                raise e
           
            ret, _, _ = HookManager._inner_call(self._hooks, ret, args, kwargs, self._inst, Hook.OUT_)
            return ret
        elif self._trigger == Hook.INOUT_:
            _, a_, k_ = HookManager._inner_call(self._hooks, None, args, kwargs, self._inst, Hook.IN_)
            try:
                ret = self._fn(*args, **kwargs)
            except Exception as e:
                # TODO: how to handle exception from
                # wrapped function. Should we hold this
                # exception and raise it after looping hooks.
                raise e

            ret, _, _ = HookManager._inner_call(self._hooks, ret, args, kwargs, self._inst, Hook.OUT_)
        else:
            raise ValueError("Invalid Trigger Option: " + str(self._trigger))


class in_(HookManager):
    """
    A decorator to hook "in" call into a function.
    
    """
    def __init__(self, hooks):
        super(in_, self).__init__(hooks, Hook.IN_)


class out_(HookManager):
    """
    A decorator to hook "out" call into a function.
    
    """
    def __init__(self, hooks):
        super(out_, self).__init__(hooks, Hook.OUT_)


class inout_(HookManager):
    """
    A decorator to hook "in" and "out" call into a function
    """
    def __init__(self, hooks):
        super(inout_, self).__init__(hooks, Hook.INOUT_)
