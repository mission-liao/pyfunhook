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
    'as' stands for 'accept_self'
""" 

class h_none(funhook.Hook):
    def __init__(self):
        super(h_none, self).__init__()
        self.accept_kwargs = False
        self.accept_pos_args = False
        self.accept_ret = False
        self.accept_self = False
        
        self.is_called = False

    def before(self):
        self.is_called = True


class h_apa(funhook.Hook):
    def __init__(self):
        super(h_apa, self).__init__()
        self.accept_kwargs = False
        self.accept_pos_args = True 
        self.accept_ret = False
        self.accept_self = False

    def before(self, ori, app):
        return (ori+self.__class__.__name__, app,)
    
class h_ak(funhook.Hook):
    def __init__(self):
        super(h_ak, self).__init__()
        self.accept_kwargs = True 
        self.accept_pos_args = False
        self.accept_ret = False
        self.accept_self = False
        
    def before(self, is_double=False):
        # force to turn off 'is_double' flag
        return {"is_double": False}

class h_ar(funhook.Hook): 
    def __init__(self):
        super(h_ar, self).__init__()
        self.accept_kwargs = False
        self.accept_pos_args = False
        self.accept_ret = True
        self.accept_self = False

    def after(self, ret):
        # do thins bad on return values.
        new_str = ret[0] + ' qoo.'
        new_len = ret[1] - 1
        return (new_str, new_len)

class h_as(funhook.Hook):
    def __init__(self):
        super(h_as, self).__init__()
        self.accept_kwargs = False
        self.accept_pos_args = False
        self.accept_ret = False 
        self.accept_self = True
        
    def before(self, inst):
        inst._bonus = self.__class__.__name__

class h_apa_ak(funhook.Hook):
    def __init__(self):
        super(h_apa_ak, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = True
        self.accept_ret = False 
        self.accept_self = False
        
    def before(self, ori, app, is_double=False):
        return (ori+self.__class__.__name__, app, ), {"is_double": True}
    
class h_apa_ar(funhook.Hook):
    def __init__(self):
        super(h_apa_ar, self).__init__()
        self.accept_kwargs = False 
        self.accept_pos_args = True
        self.accept_ret = True
        self.accept_self = False
        
        self.ori = ""
        self.app = ""
        
    def after(self, ret, ori, app):
        self.ori = ori
        self.app = app
        
        new_str = ret[0] + self.__class__.__name__
        return (new_str, ret[1]), (ori, app, )
    
class h_apa_as(funhook.Hook):
    def __init__(self):
        super(h_apa_as, self).__init__()
        self.accept_kwargs = False 
        self.accept_pos_args = True
        self.accept_ret = False
        self.accept_self = True

    def before(self, inst, ori, app):
        inst._bonus = self.__class__.__name__
        return (ori+self.__class__.__name__, app, )
    
class h_apa_ak_ar(funhook.Hook):
    def __init__(self):
        super(h_apa_ak_ar, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = True
        self.accept_ret = True
        self.accept_self = False
        
        self.ori = ""
        self.app = ""
        self.is_double = None
        
    def after(self, ret, ori, app, is_double=False):
        self.ori = ori
        self.app = app
        self.is_double = is_double
        return ret+self.__class__.__name__, (ori, app, ), {"is_double": is_double}
    
class h_apa_ak_ar_as(funhook.Hook):
    def __init__(self):
        super(h_apa_ak_ar_as, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = True
        self.accept_ret = True
        self.accept_self = True
        
        self.is_double = None
        self.ori = ""
        self.app = ""
        
    def after(self, ret, inst, ori, app, is_double=False):
        inst._bonus = self.__class__.__name__
        
        self.ori = ori
        self.app = app
        self.is_double = is_double
        
        return ret+self.__class__.__name__, (ori, app, ), {"is_double": is_double}

class h_apa_ak_as(funhook.Hook):
    def __init__(self):
        super(h_apa_ak_as, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = True
        self.accept_ret = False
        self.accept_self = True
        
    def before(self, inst, ori, app, is_double=False):
        inst._bonus = self.__class__.__name__
        return (ori+self.__class__.__name__, app, ), {"is_double": True}
    
class h_apa_ar_as(funhook.Hook):
    def __init__(self):
        super(h_apa_ar_as, self).__init__()
        self.accept_kwargs = False
        self.accept_pos_args = True
        self.accept_ret = True
        self.accept_self = True
        
        self.ori = ""
        self.app = ""

    def after(self, ret, inst, ori, app):
        inst._bonus = self.__class__.__name__
        
        self.ori = ori
        self.app = app
        return ret+self.__class__.__name__, (ori, app, )
    
class h_ak_ar(funhook.Hook):
    def __init__(self):
        super(h_ak_ar, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = False
        self.accept_ret = True
        self.accept_self = False
        
        self.is_double = None
    def after(self, ret, is_double=False):
        self.is_double = is_double
        return ret+self.__class__.__name__, {"is_double": is_double}

class h_ak_as(funhook.Hook):
    def __init__(self):
        super(h_ak_as, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = False
        self.accept_ret = False
        self.accept_self = True
        
    def before(self, inst, is_double=False):
        inst._bonus = self.__class__.__name__
        return {"is_double": True}
    
class h_ak_ar_as(funhook.Hook):
    def __init__(self):
        super(h_ak_ar_as, self).__init__()
        self.accept_kwargs = True
        self.accept_pos_args = False
        self.accept_ret = True 
        self.accept_self = True

        self.is_double = None
        
    def after(self, ret, inst, is_double=False):
        inst._bonus = self.__class__.__name__
        self.is_double = is_double
        
        return ret+self.__class__.__name__, {"is_double": is_double}
    
class h_ar_as(funhook.Hook):
    def __init__(self):
        super(h_ar_as, self).__init__()
        self.accept_kwargs = False
        self.accept_pos_args = False
        self.accept_ret = True 
        self.accept_self = True       

    def after(self, ret, inst):
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
        wrapped_fn = funhook.attach_([h])(fn)
        self.assertEqual(wrapped_fn('this is', ' cool'), 'this is cool')
        self.assertEqual(h.is_called, True)
       
        # test kwargs 
        h.is_called = False
        self.assertEqual(wrapped_fn('this is', ' cool', is_double=True), 'this is cool cool')
        self.assertEqual(h.is_called, True)

    """
    Test cases for only one option is turned on.
    """
    def test_apa(self):
        h = h_apa()
        wrapped_fn = funhook.attach_([h])(fn)
        self.assertEqual(wrapped_fn('this is ', ' cool'), 'this is h_apa cool')

        # test kwargs
        self.assertEqual(wrapped_fn('this is ', ' cool', is_double=True), 'this is h_apa cool cool')
    
    def test_ak(self):
        h = h_ak()
        wrapped_fn = funhook.attach_([h])(fn)
        self.assertEqual(wrapped_fn('this is', ' cool', is_double=True), 'this is cool')
        
    def test_ar(self):
        h = h_ar()
        wrapped_fn = funhook.attach_([h])(fn_multi_ret)
        self.assertEqual(wrapped_fn('this is', ' cool', is_double=True), ('this is cool cool qoo.', 16))
    
    def test_as(self):
        h = h_as()
        c = cls('my_bonus')

        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is coolh_as')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn
    
    """
    Test cases for turning on 'accept_pos_args'.
    'apa' stands for 'accept_pos_args'
    
    """
    def test_apa_ak(self):
        h = h_apa_ak()
        wrapped_fn = funhook.attach_([h])(fn)
        self.assertEqual(wrapped_fn('this is ', ' cool'), 'this is h_apa_ak cool cool')
    
    def test_apa_ar(self):
        h = h_apa_ar()
        wrapped_fn = funhook.attach_([h])(fn_multi_ret)
        self.assertEqual(wrapped_fn('this is ', 'cool'), ('this is coolh_apa_ar', 12))
        self.assertEqual(h.ori, "this is ")
        self.assertEqual(h.app, "cool")
    
    def test_apa_as(self):
        h = h_apa_as()
        c = cls('my_bonus')

        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this ish_apa_as coolh_apa_as')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn
                  
    def test_apa_ak_ar(self):
        h = h_apa_ak_ar()
        wrapped_fn = funhook.attach_([h])(fn)
        self.assertEqual(wrapped_fn('this is ', 'cool', is_double=True), 'this is coolcoolh_apa_ak_ar')
        self.assertEqual(h.ori, 'this is ')
        self.assertEqual(h.app, 'cool')
        self.assertEqual(h.is_double, True)
        
    def test_apa_ak_ar_as(self):
        h = h_apa_ak_ar_as()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is coolmy_bonush_apa_ak_ar_as')
            self.assertEqual(c._bonus, h.__class__.__name__)
            self.assertEqual(h.ori, 'this is')
            self.assertEqual(h.app, ' cool')
            self.assertEqual(h.is_double, False)
        finally:
            cls.fn = ori_fn
    
    def test_apa_ak_as(self):
        h = h_apa_ak_as()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this ish_apa_ak_as cool coolh_apa_ak_as')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn
    
    def test_apa_ar_as(self):
        h = h_apa_ar_as()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is coolmy_bonush_apa_ar_as')
            self.assertEqual(c._bonus, h.__class__.__name__)
            self.assertEqual(h.ori, "this is")
            self.assertEqual(h.app, " cool")
        finally:
            cls.fn = ori_fn
    
    """
    Test cases for turning on 'accept_kwargs'
    """
    def test_ak_ar(self):
        h = h_ak_ar()
        wrapped_fn = funhook.attach_([h])(fn)
        self.assertEqual(wrapped_fn('this is ', 'cool'), 'this is coolh_ak_ar')
        self.assertEqual(h.is_double, False)
        
    def test_ak_as(self):
        h = h_ak_as()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is cool coolh_ak_as')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn
    
    def test_ak_ar_as(self):
        h = h_ak_as()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is cool coolh_ak_as')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn
    
    """
    Test cases for turning on 'accept_ret'
    """
    def test_ar_as(self):
        h = h_ar_as()
        c = cls('my_bonus')
        
        ori_fn = cls.fn
        try:
            cls.fn = funhook.attach_([h])(c.fn)
            self.assertEqual(c.fn('this is', ' cool'), 'this is coolmy_bonush_ar_as')
            self.assertEqual(c._bonus, h.__class__.__name__)
        finally:
            cls.fn = ori_fn 