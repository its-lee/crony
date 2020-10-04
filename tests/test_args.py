import argparse
import unittest

from parameterized import parameterized, param

from crony import args

class ArgsTest(unittest.TestCase):
    # TODO: More tests here
    @parameterized.expand([
        param("log level",   [ '--vvv' ], { 'log_level': 'DEBUG' }),
    ])
    def test_args(self, _, args_, expected):
        actual = args.parse(args_)

        # We're happy to just assert that the expected args are contained
        # in the actual ones.
        subset = { k: v for k, v in actual.items() if k in expected }
        self.assertDictEqual(subset, expected)