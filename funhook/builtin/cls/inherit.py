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
        cls_2_seek = []
        if self._cls == None:
            # note: we didn't copy mro list here.
            # This means we shouldn't change any thing inside
            cls_2_seek = klass.__mro__[1:]
        else:
            cls_2_seek.append(self._cls)
            
        # find functions defined in both classes
        # TODO: it seems 'isfunction' is precise, right?
        fnS = set(inspect.getmembers(klass, predicate=inspect.isfunction))

        for fn_name, _ in fnS:
            for cls in cls_2_seek:
                wfn = getattr(cls, fn_name, None)
                if  not wfn or \
                    not type(wfn) is funhook.base._wrapped_fn:
                    continue

                # generate a new list of hooks
                newH = []
                for h in wfn._hook_mgr._hooks:
                    newH.append(h.duplicate())
                    
                setattr(klass, fn_name, funhook.attach_(newH)(getattr(klass, fn_name)))
                break

        return (klass, )
