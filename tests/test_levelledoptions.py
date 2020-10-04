import argparse
import unittest

from parameterized import parameterized, param

from crony import levelledoption

class ManifestTest(unittest.TestCase):

    @parameterized.expand([
        param("no default, no value",   "",      None),
        param("no default, --v",        "--v",   "WARNING"),
        param("no default, --vv",       "--vv",  "INFO"),
        param("no default, --vvv",      "--vvv", "DEBUG"),

        param("default, no value",      "",      None,      default="ERROR"),
        param("default, --v",           "--v",   "WARNING", default="ERROR"),
        param("default, --vv",          "--vv",  "INFO",    default="ERROR"),
        param("default, --vvv",         "--vvv", "DEBUG",   default="ERROR"),
    ])
    def test_levelledoptions(self, _, arg, expected, default=None):
        lo = levelledoption.LevelledOption(
            'v', 
            [ 'WARNING', 'INFO', 'DEBUG' ],
            default=default
        )
        
        parser = argparse.ArgumentParser()
        lo.add_to_parser(parser, "blah {level}")

        pargs = parser.parse_args([ arg ])
        actual = lo.parse(vars(pargs))
        self.assertEquals(expected, actual)
