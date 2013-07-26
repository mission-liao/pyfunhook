'''
Created on Jul 23, 2013

@author: Mission Liao
'''


import unittest
import funhook

"""
    Hooks for test
"""

class h_test(funhook.Hook):
    def __init__(self):
        super(h_test, self).__init__()
        self.accept_kwargs = False

    def before(self, n):
        return (n+1, )


class h_accept_self(funhook.Hook):
    def __init__(self):
        super(h_accept_self, self).__init__()
        self.accept_kwargs = False
        self.accept_self = True
        self.accept_pos_args = True

    def before(self, inst, n):
        inst.chk = False
        return (n+2, )


class clsh_set_prop(funhook.ClsHook):
    def __init__(self):
        super(clsh_set_prop, self).__init__()
        self.accept_kwargs = False
        self.accept_self = True
        self.accept_pos_args = True

    def before(self, klass):
        return klass


class clsh_with_after(funhook.ClsHook):
    def __init__(self):
        super(clsh_with_after, self).__init__()

    def before(self, klass):
        return klass

    def after(self, klass):
        return klass


"""
    Targets(functions, classes) for testing
"""

@funhook.attach_([h_test()])
def test(n):
    return n+1


class cls_(object):
    def __init__(self):
        self.chk = True

    @funhook.attach_([h_test()])
    def sample_func(self, n):
        return n + 1
    
    @funhook.attach_([h_accept_self()])
    def sample_func_accept_self(self, n):
        return n + 3


@funhook.setup_([])
class cls_no_side_effect(object):
    def __init__(self):
        self.to_dump = self.__class__.__name__
        
    def __call__(self):
        return self.to_dump


@funhook.setup_([])
class cls_inhert_parent(object):
    def __init__(self):
        pass

    @funhook.attach_([h_test()]) 
    def func(self, n):
        return n + 1


@funhook.setup_([])
class cls_inhert_child(cls_inhert_parent):
    def __init__(self):
        pass

    def func(self, n):
        return n + 100


"""
    Test Cases
"""

class TestClass(unittest.TestCase):
    """
    Test-cases for applying hooks for member-functions
    in a class.
    """
    def test_basic_usage(self):
        sc = cls_()
        self.assertEqual(sc.sample_func(1), 3)
        self.assertEqual(sc.sample_func(5), 7) # run twice to make sure not state is kept
        
    def test_accept_self(self):
        """
        make sure 'accept_self' option works
        """
        sc = cls_()
        self.assertEqual(sc.sample_func_accept_self(1), 6)
        self.assertEqual(sc.chk, False)
        
    def test_both_metho_function(self):
        """
        make sure Hook can work on 'method' and 'function'
        as long as its signature is matched.
        """
        self.assertEqual(test(1), 3)
        
    def test_no_side_effect(self):
        """
        make sure the class object returned by funhook.setup_
        works properly
        """
        c = cls_no_side_effect()
        # TODO: test more aspect
        self.assertEqual(c(), c.__class__.__name__)

    def test_clsh_set_prop(self):
        """
        make sure exception is raised when setting
        property of ClsHook
        """
        self.assertRaises(Exception, clsh_set_prop)
        
    def test_clsh_with_after(self):
        """
        make sure exception is raised when 'after'
        callback is defined
        """
        self.assertRaises(Exception, clsh_with_after)
        
    def test_setup_with_wrong_hook_type(self):
        """
        make sure exception is raised when wrong hook type
        is passed to funhook.setup_
        """
        self.assertRaises(ValueError, funhook.setup_, [h_test()])
        
    def test_clsh_add_fn(self):
        """
        add a new function to the decorated class
        """
        class clsh_add_fn(funhook.ClsHook):
            def __init__(self):
                super(clsh_add_fn, self).__init__()
        
            def before(self, klass):
                def do_nothing(inst):
                    return self.__class__.__name__

                klass.do_something = do_nothing
                return (klass, )

        @funhook.setup_([clsh_add_fn()])
        class C(object):
            pass
        
        c = C()
        self.assertEqual(c.do_something(), clsh_add_fn.__name__)
        
    def test_clsh_new_cls(self):
        """
        return another class
        """
        class TmpCls(object):
            pass
        
        class clsh_new_cls(funhook.ClsHook):
            def __init__(self):
                super(clsh_new_cls, self).__init__()

            def before(self, klass):
                # return a new class inherit from TmpCls
                class new_cls(klass, TmpCls):
                    pass
        
                return (new_cls, )
    
        @funhook.setup_([clsh_new_cls()])
        class C(object):
            def do_something(self):
                return "do something!"
       
        self.assertEqual(issubclass(C, TmpCls), True)
        self.assertEqual(C().do_something(), "do something!")

    def _test_basic_inhert(self):
        sc = cls_inhert_child()
        # TODO: not implemented yet
        #self.assertEqual(sc.func(1), 102)