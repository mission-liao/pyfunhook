'''
Created on Jul 22, 2013

@author: Mission Liao
'''

import unittest

TEST_MODULES = [
    'funhook.test.gfun',
    'funhook.test.cls',
    'funhook.test.opt',
    'funhook.test.builtin.cls.inherit'
]

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)
    unittest.TextTestRunner(verbosity=2).run(suite)