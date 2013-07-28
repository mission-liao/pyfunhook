'''
Created on Jul 23, 2013

@author: Mission Liao
'''


import unittest
import funhook


"""
    Global Hook for testing
"""

class h_test(funhook.Hook):
    def __init__(self):
        super(h_test, self).__init__()
        self.accept_kwargs = False

    def before(self, n):
        return (n+1, )


"""
    Test Cases
"""

class TestClass(unittest.TestCase):
    """
    Test-cases for applying hooks for member-functions
    in a class.
    """

    def test_basic_usage(self):
        """
        Basic Usage
        """

        class h_accept_bound(funhook.Hook):
            def __init__(self):
                super(h_accept_bound, self).__init__()
                self.accept_kwargs = False
                self.accept_bound = True
                self.accept_pos_args = True

            def before(self, inst, n):
                inst.chk = False
                return (n+2, )
    
        class cls_(object):
            def __init__(self):
                self.chk = True

            @funhook.attach_([h_test()])
            def sample_func(self, n):
                return n + 1
    
            @funhook.attach_([h_accept_bound()])
            def sample_func_accept_bound(self, n):
                return n + 3
                
        sc = cls_()
        self.assertEqual(sc.sample_func(1), 3)
        self.assertEqual(sc.sample_func(5), 7) # run twice to make sure not state is kept
        
        self.assertEqual(sc.sample_func_accept_bound(1), 6)
        self.assertEqual(sc.chk, False)
        
    def test_both_metho_function(self):
        """
        make sure Hook can work on 'method' and 'function'
        as long as its signature is matched.
        """

        @funhook.attach_([h_test()])
        def test(n):
            return n+1

        self.assertEqual(test(1), 3)
        
    def test_no_side_effect(self):
        """
        make sure the class object returned by funhook.setup_
        works properly
        """

        @funhook.setup_([])
        class cls_no_side_effect(object):
            def __init__(self):
                self.to_dump = self.__class__.__name__
        
            def __call__(self):
                return self.to_dump

        c = cls_no_side_effect()
        # TODO: test more aspect
        self.assertEqual(c(), c.__class__.__name__)

    def test_clsh_set_prop(self):
        """
        make sure exception is raised when setting
        property of ClsHook
        """

        class clsh_set_prop(funhook.ClsHook):
            def __init__(self):
                super(clsh_set_prop, self).__init__()
                self.accept_kwargs = False
                self.accept_bound = True
                self.accept_pos_args = True
                self.accept_ret = True

            def before(self, klass):
                return klass

        self.assertRaises(Exception, clsh_set_prop)
        
    def test_clsh_with_after(self):
        """
        make sure exception is raised when 'after'
        callback is defined
        """

        class clsh_with_after(funhook.ClsHook):
            def __init__(self):
                super(clsh_with_after, self).__init__()

            def before(self, klass):
                return klass

            def after(self, klass):
                return klass

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
        
    def test_classmethod(self):
        """
        make sure classmethod works along with our hooks
        """
        class h_clsm(funhook.Hook):
            def __init__(self):
                super(h_clsm, self).__init__()
                self.accept_kwargs = False
                self.accept_pos_args = True
                self.accept_ret = False
                self.accept_bound = False

                self.klass_name = ""

            def before(self, inst, s):
                return (inst, inst.__name__+s, )
            
        class cls_1(object):
            """
            test case for a function decorated by funhook
            and then by classmethod.
            """
            @classmethod
            @funhook.attach_([h_clsm()])
            def ret(klass, s):
                return s + klass.__name__

        self.assertEqual(cls_1.ret(" MyHook "), 'cls_1 MyHook cls_1')
        self.assertEqual(cls_1().ret(" MyHook "), 'cls_1 MyHook cls_1')
        
        class cls_2(object):
            """
            test case for a function decorated by classmethod and then
            by funhook.
            """
            @funhook.attach_([h_clsm()])
            @classmethod
            def ret(klass, s):
                return s + klass.__name__

        self.assertEqual(cls_2.ret(" MyHook "), 'cls_2 MyHook cls_2')
        self.assertEqual(cls_2().ret(" MyHook "), 'cls_2 MyHook cls_2')


    def test_staticmethod(self):
        """
        make sure staticmethod works along with our hooks
        """
        class h_stcm(funhook.Hook):
            def __init__(self):
                super(h_stcm, self).__init__()
                self.accept_kwargs = False
                self.accept_pos_args = True
                self.accept_ret = False
                self.accept_bound = False

                self.klass_name = ""

            def before(self, s):
                s = self.__class__.__name__ + s
                
                return (s, )
            
        class cls_1(object):
            """
            test case for a function decorated by funhook
            and then by staticmethod.
            """
            @staticmethod
            @funhook.attach_([h_stcm()])
            def ret(s):
                return s + "a static m"

        self.assertEqual(cls_1.ret(" MyHook "), 'h_stcm MyHook a static m')
        self.assertEqual(cls_1().ret(" MyHook "), 'h_stcm MyHook a static m')
        
        class cls_2(object):
            """
            test case for a function decorated by staticmethod and then
            by funhook.
            """
            @funhook.attach_([h_stcm()])
            @staticmethod
            def ret(s):
                return s + "a static m"
            
        self.assertEqual(cls_2.ret(" MyHook "), 'h_stcm MyHook a static m')
        self.assertEqual(cls_2().ret(" MyHook "), 'h_stcm MyHook a static m')
