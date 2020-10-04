from datetime import datetime
import unittest

from crony import cli

def _write_temp_crontab(tab):
    filepath = "/tmp/test-crontab-" + str(datetime.timestamp(datetime.now()))
    with open(filepath, "w") as f:
        f.write(tab)
    return filepath

class CliTest(unittest.TestCase):
    def test_cli_doesnt_die(self):
        filepath = _write_temp_crontab("* * * * * woof")

        cli.main({
            "file": filepath,
            "begin": datetime(2020, 1, 1, 0, 0, 0, 0),
            "end": datetime(2020, 2, 1, 0, 0, 0, 0)
        })