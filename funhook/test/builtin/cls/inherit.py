'''
Created on Jul 26, 2013

@author: Mission Liao
'''


import unittest
import funhook

from funhook.builtin.cls import adapt_hook_from


class TestClsInherit(unittest.TestCase):
    """
    Test cases for built-in hooks for
    class inheritance
    """

    def test_basic(self):
        """
        Test Basic Usage for inheritance
        """
        class h_test(funhook.Hook):
            def __init__(self):
                super(h_test, self).__init__()
                self.accept_kwargs = False
                self.accept_ret = False

            def before(self, bnd, n):
                return (n+1, )
    
        class cls_p(object):
            @funhook.attach_([h_test()]) 
            def func(self, n):
                return n + 1

        # seek function to wrap with class object
        @funhook.setup_([adapt_hook_from(cls_p)])
        class cls_chd(cls_p):
            def func(self, n):
                return n + 100

        sc = cls_chd()
        self.assertEqual(sc.func(1), 102)

        class cls_p1(cls_p):
            def func_not_this_one(self):
                pass
            
        class cls_p2(cls_p):
            def func_not_found(self):
                pass

        # seek function to wrap with mro
        @funhook.setup_([adapt_hook_from()])
        class cls_chd_1(cls_p1, cls_p2):
            def func(self, n):
                return n + 1000

        sc = cls_chd_1()
        self.assertEqual(sc.func(1), 1002)

        self.assertEqual(issubclass(sc.func.__class__, funhook.base._wrapped_fn), True)
        self.assertEqual(issubclass(sc.func_not_this_one.__class__, funhook.base._wrapped_fn), False)
        self.assertEqual(issubclass(sc.func_not_found.__class__, funhook.base._wrapped_fn), False)
        
    def test_with_hook_init_param(self):
        """
        test cases for hooks with init-parameters
        """
        class h_dup(funhook.Hook):
            def __init__(self, n):
                super(h_dup, self).__init__(n)
                self.accept_kwargs = False
                self.accept_pos_args = True
                self.accept_ret = False

                self._n = n

            def before(self, bnd, n):
                return (n+self._n, )


        class cls_pp(object):
            @funhook.attach_([h_dup(501)])
            def func(self, n):
                return n+1

        class cls_p1(cls_pp):
            pass

        class cls_p2(cls_pp):
            pass

        @funhook.setup_([adapt_hook_from()]) 
        class cls_chd(cls_p1, cls_p2):
            def func(self, n):
                return n-1

        self.assertEqual(cls_pp().func(1), 503)
        self.assertEqual(cls_chd().func(1), 501)