import unittest

import configuration

class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.conf = configuration.Configuration("configuration_test.conf",
                                                cmd_config = "testsection1.cmd_val=cli,DEFAULT.cmd_def=false",
                                                global_config = None,
                                                defaults = None)

    
    def testDefaults(self):
        self.assertEqual(self.conf.get("testsection1", "def_val"), "5")
        self.assertFalse(self.conf.getboolean("testsection2", "cmd_def"))

        
    def testInterpolation(self):
        self.assertEqual(self.conf.get("testsection2", "test1_val"), "eins 5")
        self.assertEqual(self.conf.get("testsection2", "test2_val"), "true true")

        
    def testOptionDict(self):
        option_d =  {'do': True, 'cmd_def': 'false', 'log': 'True', 'test_val': 'true', 'def_val': '5', 'cmd_val': 'cli'} 
        self.assertEqual(self.conf.option_dict("testsection1"),option_d)


if __name__ == '__main__':
    unittest.main()
