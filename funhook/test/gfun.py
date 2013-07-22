'''
Created on Jul 22, 2013

@author: Mission Liao
'''


import unittest
import funhook.base


def sample_hook_int(n):
    return (n+2, ), None

@funhook.base.before([sample_hook_int])
def sample_gfun_int(n):
    return n+1


def sample_hook_string_before(s):
    return (s+"_before", ), None

def sample_hook_string_after(ret, s):
    return ret+"_after"

@funhook.base.before([sample_hook_string_before])
@funhook.base.after([sample_hook_string_after])
def sample_gfun_string(s):
    return s + "_inner"


class TestGlobalFunction(unittest.TestCase):

    def test_before(self):
        self.assertEqual(sample_gfun_int(1), 4)
        
    def test_before_after(self):
        self.assertEqual(sample_gfun_string("funhook"), "funhook_before_inner_after")