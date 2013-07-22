'''
Created on Jul 22, 2013

@author: Mission Liao
'''


class before(object):

    def __init__(self, hooks):
        self.hooks = hooks

    def __call__(self, fn):
        def new_fn(*args, **kwargs):
            a_ = args
            k_ = kwargs
            for h in self.hooks:
                try:
                    a_, k2_ = h(*a_, **k_)
                    k_.update(k2_)
                except Exception:
                    # TODO: how to handle error?
                    pass

            return fn(*a_, **k_)

        return new_fn
    
class after(object):
    
    def __init__(self, hooks):
        self.hooks = hooks
        
    def __call__(self, fn):
        def new_fn(*args, **kwargs):
            
            # TODO: add init-flag for non-ret function
            # TODO: how do hooks handle cases that the
            # wrapped-function throws exceptions

            ret = fn(*args, **kwargs)
            for h in self.hooks:
                ret = h(ret, *args, **kwargs)
            return ret

        return new_fn
