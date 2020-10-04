from datetime import datetime
import unittest

from parameterized import parameterized, param

from crony import cli

def _write_temp_crontab(tab):
    filepath = "/tmp/test-crontab-" + str(datetime.timestamp(datetime.now()))
    with open(filepath, "w") as f:
        f.write(tab)
    return filepath

simple_filepath = _write_temp_crontab("* * * * * woof")

class CliTest(unittest.TestCase):
    @parameterized.expand([
        param("simple", f"--file={simple_filepath} --begin=\"2020-01-01 00:00:00\" --end=\"2020-02-01 01:23:45\"")
    ])
    def test_cli_doesnt_die(self, _, args):
        cli.main(args.split(" "))