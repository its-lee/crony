from datetime import datetime
import unittest
import shlex

from parameterized import parameterized, param

from crony import cli
from tests.util import write_temp_crontab

_SIMPLE_FILEPATH = write_temp_crontab(["* * * * * woof"])

# Don't do anything crazy here - the correct level of testing is on core.py, as cli.py translates errors etc to exit codes,
# which aren't very testable.
#   The main reason for this test is just to get coverage.
class CliTest(unittest.TestCase):
    @parameterized.expand(
        [
            param(
                "simple",
                f'--file={_SIMPLE_FILEPATH} --begin="2020-01-01 00:00:00" --end="2020-02-01 01:23:45"',
            )
        ]
    )
    def test_cli_doesnt_die(self, _, args):
        cli.main(shlex.split(args))
