'''
Created on Jul 22, 2013

@author: Mission Liao
'''


import unittest
import funhook


class sample_hook_int(funhook.Hook):
    def __init__(self):
        super(sample_hook_int, self).__init__()

    def before(self, n):
        return (n+2, ), None

@funhook.attach_([sample_hook_int()])
def sample_gfun_int(n):
    return n+1


class sample_hook_string_before(funhook.Hook):
    """
    this hook prepends something to 's'
    parameter.
    """
    def __init__(self):
        super(sample_hook_string_before, self).__init__()
    
    def before(self, s):
        return (s+"_before", ), None

class sample_hook_string_after(funhook.Hook):
    """
    this hook appends something to 's'
    parameter
    """
    def __init__(self):
        super(sample_hook_string_after, self).__init__()
        self.accept_ret = True

    def after(self, ret, s):
        return ret+"_after", (s, ), None

@funhook.attach_([
    sample_hook_string_before(),
    sample_hook_string_after()])
def sample_gfun_string(s):
    return s + "_inner"


class sample_hook_dict_before(funhook.Hook):
    """
    this hook change a keyword-argument
    """
    def __init(self, accept_kwargs):
        super(sample_hook_dict_before, self).__init__()
        
    def before(self, s, additional="qoo."):
        return (s,), {"additional": "mylove."}

@funhook.attach_([sample_hook_dict_before()])
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

    def before(self, s):
        return (s,)

@funhook.attach_([sample_hook_dict_before_nochange()])
def sample_gfun_dict_nochange(s, additional="qoo."):
    return s + additional


class h_no_ret(funhook.Hook):
    def __init__(self):
        super(h_no_ret, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = True
        self.accept_ret = True
        self.accept_self = True

        self.pass_before = False
        self.pass_after = False

    def before(self, inst, s):
        self.pass_before = True
        return (s, ), {}
    
    def after(self, ret, inst, s):
        self.pass_after = True
        return ret, (s, ), {}


def fn_no_ret(s):
    pass

class h_comb_str(funhook.Hook):
    def __init__(self, new_s, new_app):
        self.accept_kwargs = False
        self.accept_pos_args = True
        self.accept_ret = True
        self.accept_self = False
        self.new_s = new_s
        self.new_app = new_app
        
    def before(self, s, app):
        return (self.new_s+s, app, )
    
    def after(self, ret, s, app):
        return ret+self.new_app, (s, app, )

@funhook.attach_([
    h_comb_str('s1', 'app1'),
    h_comb_str('s2', 'app2'),
    h_comb_str('s3', 'app3'),
    h_comb_str('s4', 'app4'),
    h_comb_str('s5', 'app5')])
def fn_comb_str(s, app):
    return s + app

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
        
    def test_no_return(self):
        """
        make sure nothing goes wrong when function returning nothing
        """
        h = h_no_ret()
        wrapped_fn = funhook.attach_([h])(fn_no_ret)
        wrapped_fn(1)
        self.assertEqual(h.pass_after, True)
        self.assertEqual(h.pass_before, True)
        
    def test_hook_ordering(self):
        self.assertEqual(fn_comb_str(' this is ', 'cool '), 's5s4s3s2s1 this is cool app5app4app3app2app1')

