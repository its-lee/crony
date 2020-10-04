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

        cli.main([ 
            f"--file={filepath}",
            f"--begin=\"2020-01-01 00:00:00\"",
            f"--end=\"2020-02-01 01:23:45\""
        ])