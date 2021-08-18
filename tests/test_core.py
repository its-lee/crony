from datetime import datetime
import unittest
import shlex
import itertools
import io

from parameterized import parameterized, param

from crony import core

from tests.util import write_temp_crontab, to_datetime

_SIMPLE_FILEPATH = write_temp_crontab(
    [
        "* * * * * woof",
        "0 0 1 1 0 should_rarely_run",  # We want this for coverage, to show a line shouldn't be emitted in that case.
    ]
)

# Don't make the date range too large, else when testing will full output, there will be too much output
# in the test runner to make sense of anything!
_SIMPLE_ARGS = {
    "file": _SIMPLE_FILEPATH,
    "begin": to_datetime("2020-01-01 00:00:00"),
    "end": to_datetime("2020-01-01 00:23:45"),
}

_BOOLEAN_VALUES = [True, False]


def _permute(*dimensions):
    # In addition to the permutations, the first item in the tuple must be a name,
    # preferably somewhat linked to the permutation.
    return [
        ("_".join([str(p) for p in perm]), *perm)
        for perm in itertools.product(*dimensions)
    ]


def _run(opts):
    """Do core.run, but with the output redirected to a return value

    Args:
        opts (dict): The run options

    Returns:
        str: The output normally presented to the user
    """
    stream = io.StringIO()
    core.run(stream=stream, **opts)
    return stream.getvalue()


class CoreTest(unittest.TestCase):
    @parameterized.expand(
        [
            param(
                "detail level none",
                {**_SIMPLE_ARGS, "detail_level": core.DetailLevel.NONE},
            ),
            param(
                "detail level count",
                {**_SIMPLE_ARGS, "detail_level": core.DetailLevel.COUNT},
            ),
            param(
                "detail level full",
                {**_SIMPLE_ARGS, "detail_level": core.DetailLevel.FULL},
            ),
            param(
                "has a job which won't run",
                {
                    "file": _SIMPLE_FILEPATH,
                    "begin": to_datetime("2020-01-01 01:23:45"),
                    "end": to_datetime("2020-01-01 01:24:45"),
                },
            ),
            param(
                "stdin emulation",
                {
                    "tab": "* * * * * awoo",
                    "begin": to_datetime("2020-01-01 00:00:00"),
                    "end": to_datetime("2020-01-01 00:23:45"),
                },
            ),
        ]
    )
    def test_core_doesnt_die(self, _, kwargs):
        # Ensure defaults are present, and allow them to be overriden in the same way as on the command line.
        base_kwargs = {
            "detail_level": core.DetailLevel.NONE,
            "include_disabled": False,
            "exclude_header": False,
            "only_command": False,
        }
        _run({**base_kwargs, **kwargs})

    @parameterized.expand(
        _permute(
            list(core.DetailLevel), _BOOLEAN_VALUES, _BOOLEAN_VALUES, _BOOLEAN_VALUES
        )
    )
    def test_core_doesnt_die_with_all_permutations(
        self, _, detail_level, include_disabled, exclude_header, only_command
    ):
        _run(
            {
                "detail_level": detail_level,
                "include_disabled": include_disabled,
                "exclude_header": exclude_header,
                "only_command": only_command,
                **_SIMPLE_ARGS,
            }
        )
