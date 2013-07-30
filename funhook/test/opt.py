'''
Created on Jul 25, 2013

@author: Mission Liao
'''


import unittest
import funhook

"""
    'apa' stands for 'accept_pos_args
    'ak' stands for 'accept_kwargs'
    'ar' stands for 'accept_ret'
""" 


class h_none(funhook.Hook):
    def __init__(self):
        super(h_none, self).__init__()
        self.accept_kwargs = False
        self.accept_pos_args = False
        self.accept_ret = False 

    def before(self, inst):
        inst._bonus = self.__class__.__name__

class h_apa(funhook.Hook):
    def __init__(self):
        super(h_apa, self).__init__()
        self.accept_kwargs = False 
        self.accept_pos_args = True
        self.accept_ret = False

    def before(self, inst, ori, app):
        inst._bonus = self.__class__.__name__
        return (ori+self.__class__.__name__, app, )
    
class h_apa_ak_ar(funhook.Hook):
    def __init__(self):
        super(h_apa_ak_ar, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = True
        self.accept_ret = True

        self.is_double = None
        self.ori = ""
        self.app = ""
        
    def after(self, inst, ret, ori, app, is_double=False):
        inst._bonus = self.__class__.__name__

        self.ori = ori
        self.app = app
        self.is_double = is_double
        
        return ret+self.__class__.__name__, (ori, app, ), {"is_double": is_double}

class h_apa_ak(funhook.Hook):
    def __init__(self):
        super(h_apa_ak, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = True
        self.accept_ret = False
        
    def before(self, inst, ori, app, is_double=False):
        inst._bonus = self.__class__.__name__
        return (ori+self.__class__.__name__, app, ), {"is_double": True}
    
class h_apa_ar(funhook.Hook):
    def __init__(self):
        super(h_apa_ar, self).__init__()
        self.accept_kwargs = False
        self.accept_pos_args = True
        self.accept_ret = True
        
        self.ori = ""
        self.app = ""

    def after(self, inst, ret, ori, app):
        inst._bonus = self.__class__.__name__
        
        self.ori = ori
        self.app = app
        return ret+self.__class__.__name__, (ori, app, )
    
class h_ak(funhook.Hook):
    def __init__(self):
        super(h_ak, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = False
        self.accept_ret = False
        
    def before(self, inst, is_double=False):
        inst._bonus = self.__class__.__name__
        return {"is_double": True}
    
class h_ak_ar(funhook.Hook):
    def __init__(self):
        super(h_ak_ar, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = False
        self.accept_ret = True 

        self.is_double = None
        
    def after(self, inst, ret, is_double=False):
        inst._bonus = self.__class__.__name__
        self.is_double = is_double
        
        return ret+self.__class__.__name__, {"is_double": is_double}
    
class h_ar(funhook.Hook):
    def __init__(self):
        super(h_ar, self).__init__()
        self.accept_kwargs = False
        self.accept_pos_args = False
        self.accept_ret = True 

    def after(self, inst, ret):
        inst._bonus = self.__class__.__name__
        return ret+self.__class__.__name__
    
"""    
for simplicity, we didn't decorate this 
function directly, but decorate them
in each test-case.
"""
def fn(ori, app, is_double=False):
    ret = None
    if is_double:
        ret = ori + app + app
    else:
        ret = ori + app
    return ret 

# function with multiple return value
def fn_multi_ret(ori, app, is_double=False):
    ret = fn(ori, app, is_double)
    return ret, len(ret)

"""
for simplicity, we didn't decorate this function here,
but decorate them in each test-case.
"""
class cls(object):
    def __init__(self, bonus):
        self._bonus = bonus
    
    def fn(self, ori, app, is_double=False):
        ret = None
        if is_double:
            ret = ori + app + app
        else:
            ret = ori + app
            
        ret = ret + self._bonus
        return ret 

class TestOption(unittest.TestCase):
    """
    Test cases Hook.opt_* combination

    """

    def test_none(self):
        h = h_none()
        c = cls('my_bonus')

        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is coolh_none')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn
    
    def test_apa_ak_ar(self):
        h = h_apa_ak_ar()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is coolmy_bonush_apa_ak_ar')
            self.assertEqual(c._bonus, h.__class__.__name__)
            self.assertEqual(h.ori, 'this is')
            self.assertEqual(h.app, ' cool')
            self.assertEqual(h.is_double, False)
        finally:
            cls.fn = ori_fn
    
    def test_apa_ak(self):
        h = h_apa_ak()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this ish_apa_ak cool coolh_apa_ak')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn
    
    def test_apa_ar(self):
        h = h_apa_ar()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is coolmy_bonush_apa_ar')
            self.assertEqual(c._bonus, h.__class__.__name__)
            self.assertEqual(h.ori, "this is")
            self.assertEqual(h.app, " cool")
        finally:
            cls.fn = ori_fn
    
    """
    Test cases for turning on 'accept_kwargs'
    """
    def test_ak(self):
        h = h_ak()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is cool coolh_ak')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn
    
    def test_ak_ar(self):
        h = h_ak_ar()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is coolmy_bonush_ak_ar')
            self.assertEqual(c._bonus, h.__class__.__name__)
            self.assertEqual(h.is_double, False)
        finally:
            cls.fn = ori_fn
    
    """
    Test cases for turning on 'accept_ret'
    """
    def test_ar(self):
        h = h_ar()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is coolmy_bonush_ar')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn 