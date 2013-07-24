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

    def __call__(self, n):
        return (n+1, )

@funhook.before([sample_hook()])
def test(n):
    return n+1

class sample_hook_accept_self(funhook.Hook):
    def __init__(self):
        super(sample_hook_accept_self, self).__init__()
        self.accept_kwargs = False
        self.accept_self = True
        
    def __call__(self, obj, n):
        obj.chk = False
        return (obj, n+2, )


class sample_class(funhook.Hook):
    def __init__(self):
        self.chk = True

    @funhook.before([sample_hook()])
    def sample_func(self, n):
        return n + 1
    
    @funhook.before([sample_hook_accept_self()])
    def sample_func_accept_self(self, n):
        return n + 3


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
        