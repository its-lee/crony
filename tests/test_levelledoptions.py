import argparse
import unittest

from parameterized import parameterized, param

from crony import levelledoption

class ManifestTest(unittest.TestCase):

    @parameterized.expand([
        param("no default, no value",   None,    None),
        param("no default, --v",        "--v",   "WARNING"),
        param("no default, --vv",       "--vv",  "INFO"),
        param("no default, --vvv",      "--vvv", "DEBUG"),

        param("default, no value",      None,    None,      default="ERROR"),
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
        # We need a dummy argument to be able to supply so that we can test passing
        # no arg linked to the levelled option to see what the default value would be
        #   If we don't have this, we'd end up passing no args, which would cause
        # argparse to exit immediately with a help message.
        parser.add_argument('--dummy', action='store_true')
        lo.add_to_parser(parser, "blah {level}")

        args = [ '--dummy' ]
        if arg is not None:
            args.append(arg)

        pargs = parser.parse_args(args)
        actual = lo.parse(vars(pargs))
        self.assertEqual(expected, actual)
