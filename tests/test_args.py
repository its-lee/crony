import argparse
import unittest

from parameterized import parameterized, param

from crony import args

class ArgsTest(unittest.TestCase):
    # TODO: More tests here
    @parameterized.expand([
        param("no default, no value",   [ '--vvv' ], { 'log_level': 'DEBUG' }),
    ])
    def test_args(self, _, args_, expected_args):
        parsed_args = args.parse(args_)

        # We're happy to just assert that the expected args are contained
        # in the actual ones. This can be done via dict <=
        # 
        # From https://stackoverflow.com/questions/21058230/how-to-assert-a-dict-contains-another-dict-without-assertdictcontainssubset-in-p
        #
        # users = {'id': 28027, 'email': 'chungs.lama@gmail.com','created_at': '2005-02-13'}
        # data = {"email": "chungs.lama@gmail.com"}
        # self.assertGreaterEqual(user.items(), data.items())

        self.assertGreaterEqual(parsed_args, expected_args)