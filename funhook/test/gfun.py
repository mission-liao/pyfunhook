'''
Created on Jul 22, 2013

@author: Mission Liao
'''


import unittest
import funhook


class sample_hook_int(funhook.Hook):
    def __init(self):
        super(sample_hook_int, self).__init__()

    def __call__(self, n):
        return (n+2, ), None

@funhook.before([sample_hook_int()])
def sample_gfun_int(n):
    return n+1


class sample_hook_string_before(funhook.Hook):
    """
    this hook prepends something to 's'
    parameter.
    """
    def __init__(self):
        super(sample_hook_string_before, self).__init__()
    
    def __call__(self, s):
        return (s+"_before", ), None

class sample_hook_string_after(funhook.Hook):
    """
    this hook appends something to 's'
    parameter
    """
    def __init__(self):
        super(sample_hook_string_after, self).__init__()

    def __call__(self, ret, s):
        return ret+"_after", (s, ), None

@funhook.before([sample_hook_string_before()])
@funhook.after([sample_hook_string_after()])
def sample_gfun_string(s):
    return s + "_inner"


class sample_hook_dict_before(funhook.Hook):
    """
    this hook change a keyword-argument
    """
    def __init(self, accept_kwargs):
        super(sample_hook_dict_before, self).__init__()
        
    def __call__(self, s, additional="qoo."):
        return (s,), {"additional": "mylove."}

@funhook.before([sample_hook_dict_before()])
def sample_gfun_dict(s, additional="qoo."):
    return s + additional


class sample_hook_dict_before_nochange(funhook.Hook):
    """
    this hook changes nothing.
    we just want to make sure we can pack/unpack correctly.
    """
    def __init__(self):
        super(sample_hook_dict_before_nochange, self).__init__()
        self.accept_kwargs = False

    def __call__(self, s):
        return (s,)

@funhook.before([sample_hook_dict_before_nochange()])
def sample_gfun_dict_nochange(s, additional="qoo."):
    return s + additional


class TestGlobalFunction(unittest.TestCase):
    """
    Test-cases for applying hooks to global functions
    """
    def test_int_before(self):
        """
        make sure 'before' hook can work
        """
        self.assertEqual(sample_gfun_int(1), 4)
        
    def test_string_before_after(self):
        """
        make sure both 'after' and 'before' hook can work
        """
        self.assertEqual(sample_gfun_string("funhook"), "funhook_before_inner_after")

    def test_string_dict_before(self):
        """
        basic kwargs case.
        """
        self.assertEqual(sample_gfun_dict("You are "), "You are mylove.")
        
    def test_string_dict_before_default_arg(self):
        """
        make sure if we can handle default-argument correctly
        """
        self.assertEqual(sample_gfun_dict_nochange("You are "), "You are qoo.")
        self.assertEqual(sample_gfun_dict_nochange("You are ", additional="Cool Mission."), "You are Cool Mission.")
        
        # TODO: add case for multiple default arguments.
