'''
Created on Jul 22, 2013

@author: Mission Liao
'''


# TODO: add case for 'inout' trigger
# TODO: write guide to let users know for multiple return values
# TODO: provide options to skip scanning one direction of hooks
#       when all hooks are either IN_ or OUT_
# TODO: add case for multiple default arguments.
# TODO: support passing init-arguments to inherited hooks
# TODO: inspect.ismethod and inspect.isfunction can't find
# our wrapped functions.


class Hook(object):
    """ base implementation of a Hook
    
    Member variable:
    opt_accept_pos_args -- if this hook accept position arguments.
    opt_accept_kwargs -- if this hook accept keyword arguments.
    opt_accept_ret -- if this hook accept return-value for hookee.
        this option only valid for hooks implementing 'after'
        callback.
    opt_accpet_bound -- if this hook accept 'self' when hookee is
        a bounded method, and accept 'klass' when hookee is a
        classmethod.
        
    Callbacks:
    after -- this callback would be called after hookee is called.
        It can be used to monitor/modify return value.
    before -- this callback would be called before hookee is called.
        It can be used to modify input variables.
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
        # or accept 'klass' as first-parameter
        # in classmethod case
        self.opt_accept_bound = False

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
    def accept_bound(self):
        return self.opt_accept_bound
    
    @accept_bound.setter
    def accept_bound(self, v):
        if type(v) != bool:
            raise TypeError(Hook.error_type_not_bool)

        self.opt_accept_bound = v


class ClsHook(Hook):
    """ Hook for class decorator
    
    This hook provide default option-settings for a hook.
    And it prohibits any changes to them.
    
    Default setting for Class-Hook:
    accept-keyword-argument -- No
    accept-keyword-argument -- Yes
    accept-ret -- No
    accept-bound -- No
    
    Besides these, it must not provide 'after' callback.
    We would 'call' nothing in Class-Hook case.
    """
    
    err_msg_op_prohibit = "This action is prohibit."
    err_msg_no_after = "\'after\' member function is not allowed."
    
    def __init__(self):
        super(ClsHook, self).__init__()
        self.opt_accept_kwargs = False
        self.opt_accept_pos_args = True
        self.opt_accept_ret = False
        self.opt_accept_bound = False
        
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
    def accept_bound(self):
        return self.opt_accept_bound

    @accept_bound.setter
    def accept_bound(self, v):
        raise Exception(ClsHook.err_msg_op_prohibit)
 
class HookMgr(object):
    """ base hook-manager implementation
    
    This class keeps the list of hooks provided by users.
    And the real trigger to those hooks is here, too.
    
    Static Members:
    IN_ -- before calling the decorated function.
        Only valid when target is FN_.
    OUT_ -- after calling the decorated function
        Only valid when target is CLASS_.
    
    CLASS_ -- target is a decorated class.
    FN_ -- target is a decorated function.
    """

    # hook context
    IN_ = 1
    OUT_ = 2
    
    # target type
    CLASS_ = 1
    FN_ = 2

    err_msg_wrong_target_type = "invalid target type [{}]"
    
    err_msg_empty_class = "Empty Class Returned, maybe some hook is bad."

    def __init__(self, hooks, tget_type):
        # make sure every hook is subclass from 'Hook'
        for h in hooks:
            if not issubclass(type(h), Hook):
                raise TypeError("Please implement hooks as funhook.Hook class.")

        self._hooks = hooks
        self._tget_type = tget_type

    def __call__(self, obj):
        if self._tget_type == HookMgr.FN_:
            # we need to return a special object to handle
            # the complex bound scenario of functions/methods.
            return _wrapped_fn(obj, self, None, is_clsm=False)
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

            _, a_, _ = HookMgr._inner_call(self, None, (obj, ), {}, None, auto_bound=False, ctx=HookMgr.IN_)
            if a_[0] == None:
                raise RuntimeError(HookMgr.err_msg_empty_class)
            
            return a_[0]
        else:
            raise ValueError(HookMgr.err_msg_wrong_target_type.format(self._tget_type, ))

    def _inner_call(self, ret, args, kwargs, bound_, auto_bound=False, ctx=None):
        """ real trigger for hooks
        
        Position Arguments:
        ret -- return value of hookee, should be None when ctx is IN_.
        args -- positional arguments passed to hookee.
        kwargs -- keyword arguments passed to hookee.
        bound_ -- in method, this one refers to 'self'. And in classmethod,
            this one refers to 'klass'.
            
        Keyword Arguments
        auto_bound -- if we have to prepend 'bound_' parameter to args?
        ctx -- current running context, could be HookMgr.IN_ or HookMgr.OUT_.
        
        Return:
        A tuple contains 3 elements: patched return value, patched positional
        arguments, patched keyword arguments.
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

            """
            special patch for options,
            they are usually warkaround for something.
            """
            
            # 'accept_ret' option only allowed in OUT_ context
            patched_accept_ret = h.opt_accept_ret and ctx == HookMgr.OUT_
            # 'accept_bound' would be aggregated with auto_bound_ option
            patched_accept_bound = h.opt_accept_bound or auto_bound

            try:
                k2_ = None
                """
                handle
                    Hook.accept_ret,
                    Hook.accept_pos_args,
                    Hook.accept_kwargs,
                    Hook.accept_bound,
                options
                """
                # TODO: is there a good way
                # to handle such mass??
                if patched_accept_ret:
                    if h.opt_accept_kwargs:
                        if h.opt_accept_pos_args:
                            if patched_accept_bound:
                                ret, a_, k2_ = fn_(ret, bound_, *a_, **k_)
                            else:
                                ret, a_, k2_ = fn_(ret, *a_, **k_)
                        else:
                            if patched_accept_bound:
                                ret, k2_ = fn_(ret, bound_, **k_)
                            else:
                                ret, k2_ = fn_(ret, **k_)
                    else:
                        if h.opt_accept_pos_args:
                            if patched_accept_bound:
                                ret, a_ = fn_(ret, bound_, *a_)
                            else:
                                ret, a_ = fn_(ret, *a_)
                        else:
                            if patched_accept_bound:
                                ret = fn_(ret, bound_)
                            else:
                                ret = fn_(ret)
                else:
                    if h.opt_accept_kwargs:
                        if h.opt_accept_pos_args:
                            if patched_accept_bound:
                                a_, k2_ = fn_(bound_, *a_, **k_)
                            else:
                                a_, k2_ = fn_(*a_, **k_)
                        else:
                            if patched_accept_bound:
                                k2_ = fn_(bound_, **k_)
                            else:
                                k2_ = fn_(**k_)
                    else:
                        if h.opt_accept_pos_args:
                            if patched_accept_bound:
                                a_ = fn_(bound_, *a_)
                            else:
                                a_ = fn_(*a_)
                        else:
                            if patched_accept_bound:
                                fn_(bound_)
                            else:
                                fn_()

                if k2_:
                    k_.update(k2_)

            except Exception as e:
                # TODO: how to handle error in hooks?
                raise e

        return ret, a_, k_


class _wrapped_fn(object):
    """ The actual function class we return to caller
    
    We resolve the bound behavior in python method in
    this calss' __get__
    """
    def __init__(self, fn, hook_mgr, bound, is_clsm):
        self._fn = fn
        self._hook_mgr = hook_mgr
        self._bound = bound 
        self._cache_funobj = None
        self._is_classmethod = is_clsm

    def __get__(self, obj, obj_type):

        """
        for classmethod and staticmethod
        
        these function-type are actually builtin types, and not callable.
        They are just descriptor, and we need to get actuall callable from
        their __get__.
        """
        if  type(self._fn) is classmethod or \
            type(self._fn) is staticmethod:
            if self._cache_funobj == None:
                new_fn = self._fn.__get__(obj, obj_type)
                if type(self._fn) is classmethod:
                    self._cache_funobj = \
                        self.__class__(new_fn, self._hook_mgr, obj_type, is_clsm=True)
                else:
                    self._cache_funobj = \
                        self.__class__(new_fn, self._hook_mgr, None, is_clsm=False)

            return self._cache_funobj
        
        """
        normal instance method

        refer to
            http://blog.ianbicking.org/2008/10/24/decorators-and-descriptors/
            
        for more information.
        
        In short, this makes our hooks work on both 'bound' methods and
        'unbound' functions.
        """
        if obj == None:
            return self

        if self._cache_funobj == None:
            new_fn = self._fn.__get__(obj, obj_type)
            self._cache_funobj = self.__class__(new_fn, self._hook_mgr, obj, is_clsm=False)

        return self._cache_funobj

    def __call__(self, *args, **kwargs):
        a_ = args
        # workaround for classmethod decorator
        _, a_, k_ = HookMgr._inner_call(self._hook_mgr, None, a_, kwargs, self._bound, auto_bound=self._is_classmethod, ctx=HookMgr.IN_)
        try:
            """
            workaround for classmethod.
            
            the bounded method returned by classmethod's __get__
            is already bound to klass, we don't need to pass it
            """
            if self._is_classmethod:
                a_ = a_[1:]
            ret = self._fn(*a_, **k_)
        except Exception as e:
            # TODO: how to handle exception from
            # wrapped function. Should we hold this
            # exception and raise it after looping hooks.
            raise e

        ret, _, _ = HookMgr._inner_call(self._hook_mgr, ret, a_, k_, self._bound, auto_bound=self._is_classmethod, ctx=HookMgr.OUT_)
        return ret


class attach_(HookMgr):
    """ A decorator to hook 'in' and 'out' of a function
    """
    def __init__(self, hooks):
        super(attach_, self).__init__(hooks, HookMgr.FN_)


class setup_(HookMgr):
    """ A decorator to patch the created class
    """

    err_msg_wrong_type_of_hooks = "this hook should not be a valid class decorator: [{}]"
    
    def __init__(self, hooks):
        for h in hooks:
            if not issubclass(h.__class__, ClsHook):
                raise ValueError(setup_.err_msg_wrong_type_of_hooks.format(h.__class__.__name__))

        super(setup_, self).__init__(hooks, HookMgr.CLASS_)
