'''
Created on Jul 23, 2013

@author: Mission Liao
'''


import unittest
import funhook


class sample_hook(funhook.Hook):
    def __init__(self):
        super(sample_hook, self).__init__()
        self.accept_kwargs = False

    def before(self, n):
        return (n+1, )

@funhook.in_([sample_hook()])
def test(n):
    return n+1

class sample_hook_accept_self(funhook.Hook):
    def __init__(self):
        super(sample_hook_accept_self, self).__init__()
        self.accept_kwargs = False
        self.accept_self = True
        self.accept_pos_args = True

    def before(self, inst, n):
        inst.chk = False
        return (n+2, )


class sample_class(funhook.Hook):
    def __init__(self):
        self.chk = True

    @funhook.in_([sample_hook()])
    def sample_func(self, n):
        return n + 1
    
    @funhook.in_([sample_hook_accept_self()])
    def sample_func_accept_self(self, n):
        return n + 3


class sample_cls_inhert_parent(object):
    def __init__(self):
        pass
   
    @funhook.in_([sample_hook()]) 
    def func(self, n):
        return n + 1

@funhook.setup
class sample_cls_inhert_child(sample_cls_inhert_parent):
    def __init__(self):
        pass

    def func(self, n):
        return n + 100

class TestClass(unittest.TestCase):
    """
    Test-cases for applying hooks for member-functions
    in a class.
    """
    def test_basic_usage(self):
        sc = sample_class()
        self.assertEqual(sc.sample_func(1), 3)
        self.assertEqual(sc.sample_func(5), 7) # run twice to make sure not state is kept
        
    def test_accept_self(self):
        """
        make sure 'accept_self' option works
        """
        sc = sample_class()
        self.assertEqual(sc.sample_func_accept_self(1), 6)
        self.assertEqual(sc.chk, False)
        
    def test_both_metho_function(self):
        """
        make sure Hook can work on 'method' and 'function'
        as long as its signature is matched.
        """
        self.assertEqual(test(1), 3)

    def _test_basic_inhert(self):
        sc = sample_cls_inhert_child()
        # TODO: not implemented yet
        #self.assertEqual(sc.func(1), 102)