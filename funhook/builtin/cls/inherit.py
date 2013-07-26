'''
Created on Jul 26, 2013

@author: Mission Liao
'''

from __future__ import absolute_import

import funhook
import inspect


class adapt_hook_from(funhook.ClsHook):
    def __init__(self, cls=None):
        super(adapt_hook_from, self).__init__()
        self._cls = cls

    def before(self, klass):
        if self._cls == None:
            # TODO: find parent through mro
            raise NotImplementedError()
        
        # find functions defined in both classes
        # TODO: it seems 'isfunction' is precise, right?
        fnS = set(inspect.getmembers(klass, predicate=inspect.isfunction))
        
        for fn_name, _ in fnS:
            wfn = getattr(self._cls, fn_name, None)
            # TODO: this means it a new function in child class, right?
            if not wfn:
                continue

            if type(wfn) is funhook.base._wrapped_fn:
                # generate a new list of hooks
                newH = []
                for h in wfn._hook_mgr._hooks:
                    # TODO: handle init parameters
                    newH.append(h.__class__())
                    
                setattr(klass, fn_name, funhook.attach_(newH)(getattr(klass, fn_name)))

        return (klass, )
