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
                self.accept_self = False

            def before(self, n):
                return (n+1, )
    
        class cls_p(object):
            @funhook.attach_([h_test()]) 
            def func(self, n):
                return n + 1

        @funhook.setup_([adapt_hook_from(cls_p)])
        class cls_chd(cls_p):
            def func(self, n):
                return n + 100

        sc = cls_chd()
        self.assertEqual(sc.func(1), 102)