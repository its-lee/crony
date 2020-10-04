import argparse
import unittest
import datetime

from parameterized import parameterized, param

from crony import args

class ArgsTest(unittest.TestCase):
    # TODO: More tests here
    # TODO: Test defaults
    @parameterized.expand([
        param("log level",  [ '--vvv' ], { 'log_level': 'DEBUG' }),
        param("begin",      [ '--begin="2020-01-02 01:23:45"' ], { 'begin': datetime.datetime(2020, 1, 2, 1, 23, 45, 0) }),
    ])
    def test_args(self, _, args_, expected):
        actual = args.parse(args_)

        # We're happy to just assert that the expected args are contained
        # in the actual ones.
        subset = { k: v for k, v in actual.items() if k in expected }
        self.assertDictEqual(subset, expected)