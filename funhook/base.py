'''
Created on Jul 22, 2013

@author: Mission Liao
'''


# TODO: add case for 'inout' trigger
# TODO: write guide to let users know for multiple return values
# TODO: provide options to skip scanning one direction of hooks
#       when all hooks are either IN_ or OUT_
# TODO: add case for multiple default arguments.


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

       @funhook.attach_([myhook(...)])
       def myfunc(a, b, c, isDebug=False):
           pass

       You can pass options to your hook in __init__.
       
       ex.
       class myhook(funhook.Hook):
           def __init__(self, allow_rethrow=True):
               ...
               
       @funhook.attach_([myhook(allow_rethrow=False)])
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

       @funhook.attach_([myhook])
       def myfunc(a, b, c, isDebug=Fales):
           pass
    """
  
    # standard error message for wrong type with option.
    error_type_not_bool = "Please assign options with bool."
    # error message for wrong config
    error_wrong_config = "Such configuration is wrong."

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


class ClsHook(Hook):
    """
    Hook for class
    """
    
    err_msg_op_prohibit = "This action is prohibit."
    err_msg_no_after = "\'after\' member function is not allowed."
    
    def __init__(self):
        super(ClsHook, self).__init__()
        self.opt_accept_kwargs = False
        self.opt_accept_pos_args = True
        self.opt_accept_ret = False
        self.opt_accept_self = False
        
        if hasattr(self, 'after'):
            raise Exception(ClsHook.err_msg_no_after)

    """
        Prohibit all properties' modification
    """
    @property
    def accept_kwargs(self):
        return self.opt_accept_kwargs

    @accept_kwargs.setter
    def accept_kwargs(self, v):
        raise Exception(ClsHook.err_msg_op_prohibit)
    
    @property
    def accept_pos_args(self):
        return self.opt_pos_args

    @accept_pos_args.setter
    def accept_pos_args(self, v):
        raise Exception(ClsHook.err_msg_op_prohibit)

    @property
    def accept_ret(self):
        return self.opt_accept_ret

    @accept_ret.setter
    def accept_ret(self, v):
        raise Exception(ClsHook.err_msg_op_prohibit)

    @property
    def accept_self(self):
        return self.opt_accept_self

    @accept_self.setter
    def accept_self(self, v):
        raise Exception(ClsHook.err_msg_op_prohibit)
 
class HookMgr(object):
    """
    base hook-manager implementation
    """
    
    # hook context
    IN_ = 1
    OUT_ = 2
    
    # target type
    CLASS_ = 1
    FN_ = 2

    err_msg_wrong_target_type = "invalid target type [{}]"

    def __init__(self, hooks, tget_type):
        # make sure every hook is subclass from 'Hook'
        for h in hooks:
            if not issubclass(type(h), Hook):
                raise TypeError("Please implement hooks as funhook.Hook class.")

        self._hooks = hooks
        self._tget_type = tget_type

    def __call__(self, obj):
        if self._tget_type == HookMgr.FN_:
            return _wrapped_fn(obj, self, None)
        elif self._tget_type == HookMgr.CLASS_:
            """
            Class Hook, not like functions, we don't have to care about
            'bound' or 'unbound' case.
            """
            
            """
            workaround for empty list of hooks, return input directly.
            """
            if len(self._hooks) == 0:
                return obj

            _, a_, _ = HookMgr._inner_call(self, None, (obj, ), {}, None, HookMgr.IN_)
            return a_[0]
        else:
            raise ValueError(HookMgr.err_msg_wrong_target_type.format(self._tget_type, ))

    def _inner_call(self, ret, args, kwargs, inst, ctx):
        """
        loop through hooks
        """
        a_ = args
        k_ = kwargs
       
        iter_ = None 
        if ctx == HookMgr.IN_:
            iter_ = self._hooks
        elif ctx == HookMgr.OUT_:
            iter_ = reversed(self._hooks)
            
        if iter_ == None:
            raise ValueError("unknown context: " + str(ctx))

        for h in iter_:
            # prepare function pointer
            fn_ = None
            if ctx == HookMgr.IN_ and hasattr(h, 'before'):
                fn_ = h.before
            elif ctx == HookMgr.OUT_ and hasattr(h, 'after'):
                fn_ = h.after
            
            if fn_ == None:
                continue

            # prepare for opt_accept_ret
            tmp_accept_ret = h.opt_accept_ret and ctx == HookMgr.OUT_

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
                if tmp_accept_ret:
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


class _wrapped_fn(object):
    """
    The actual function class we return to caller
    """
    def __init__(self, fn, hook_mgr, inst):
        self._fn = fn
        self._hook_mgr = hook_mgr
        self._inst = inst
        self._cache_bound_funobj = None

    def __get__(self, obj, obj_type):
        """
        refer to
            http://blog.ianbicking.org/2008/10/24/decorators-and-descriptors/
            
        for more information.
        
        In short, this makes our hooks work on both 'bound' methods and
        'unbound' functions.
        """
        if obj == None:
            return self

        if self._cache_bound_funobj == None:
            new_fn = self._fn.__get__(obj, obj_type)
            self._cache_bound_funobj = self.__class__(new_fn, self._hook_mgr, obj)

        return self._cache_bound_funobj

    def __call__(self, *args, **kwargs):
        _, a_, k_ = HookMgr._inner_call(self._hook_mgr, None, args, kwargs, self._inst, HookMgr.IN_)
        try:
            ret = self._fn(*a_, **k_)
        except Exception as e:
            # TODO: how to handle exception from
            # wrapped function. Should we hold this
            # exception and raise it after looping hooks.
            raise e

        ret, _, _ = HookMgr._inner_call(self._hook_mgr, ret, a_, k_, self._inst, HookMgr.OUT_)
        return ret


class attach_(HookMgr):
    """
    A decorator to hook 'in' and 'out' of a function
    """
    def __init__(self, hooks):
        super(attach_, self).__init__(hooks, HookMgr.FN_)


class setup_(HookMgr):
    """
    A decorator to patch the created class
    """

    err_msg_wrong_type_of_hooks = "this hook should not be a valid class decorator: [{}]"
    
    def __init__(self, hooks):
        for h in hooks:
            if not issubclass(h.__class__, ClsHook):
                raise ValueError(setup_.err_msg_wrong_type_of_hooks.format(h.__class__.__name__))

        super(setup_, self).__init__(hooks, HookMgr.CLASS_)