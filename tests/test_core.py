from datetime import datetime
import unittest
import shlex

from parameterized import parameterized, param

from crony import core

from tests.util import write_temp_crontab, to_datetime

simple_filepath = write_temp_crontab([ 
    "* * * * * woof",
    "0 0 1 1 0 should_rarely_run"    # We want this for coverage, to show a line shouldn't be emitted in that case.
])

simple_args = { "file": simple_filepath, "begin": "2020-01-01 00:00:00", "end": "2020-01-01 01:23:45" }

class CoreTest(unittest.TestCase):
    # TODO: thorough tests here
    @parameterized.expand([
        param("detail level none", { **simple_args, "detail_level": core.DetailLevel.NONE }),
        param("detail level count", { **simple_args, "detail_level": core.DetailLevel.COUNT }),
        param("detail level full", { **simple_args, "detail_level": core.DetailLevel.FULL }),

        param("has a job which won't run", { "file": simple_filepath, "begin": "2020-01-01 01:23:45", "end": "2020-01-01 01:24:45" }),
    ])
    def test_core_doesnt_die(self, _, kwargs):
        # Convert to actual datetime objects
        for key in [ "begin", "end" ]:
            if key in kwargs:
                kwargs[key] = to_datetime(kwargs[key])

        # Ensure defaults are present, and allow them to be overriden in the same way as on the command line.
        base_kwargs = {
            "detail_level": core.DetailLevel.NONE,
            "include_disabled": False,
            "exclude_header": False,
            "only_command": False
        }
        core.run(**{ **base_kwargs, **kwargs })