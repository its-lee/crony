import sys
import os
import logging
from datetime import datetime
from enum import Enum

from crontab import CronTab

import crony.analyser

_logger = logging.getLogger(__name__)

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class DetailLevel(Enum):
    NONE = 0
    COUNT = 1
    FULL = 2

def _parse_crontab(**kwargs):
    """Parse crontab-related args

    Args:
        kwargs (dict): Keyword args

    Returns:
        tuple: A tuple of (human readable crontab source, crontab.CronTab)
    """
    if sys.stdin.isatty():
        _input = kwargs.get('input')
        _user = kwargs.get('user')
        if _input:
            return ('input', CronTab(tabfile=_input))
        elif _user:
            return (f"user:{_user}", CronTab(user=_user))
        else:
            # In the case of none of them being passed, we default to the current user.
            return ('user:current', CronTab(user=True))
    else:
        # If we're not a tty, then try to read a crontab from stdin.
        return ('stdin', CronTab(tab=sys.stdin.read()))

def _stringize_datetime(dt):
    """Convert a datetime to the default format used

    Args:
        dt (datetime.datetime): A datetime object to format

    Returns:
        str: The formatted datetime
    """
    return dt.strftime(DEFAULT_DATE_FORMAT)

def _build_header(**kwargs):
    """Build the header

    Args:
        kwargs (dict): Keyword args
    """
    return f"For {kwargs['source']}: {_stringize_datetime(kwargs['begin'])} -> {_stringize_datetime(kwargs['end'])}"

def run(**kwargs):
    """Run the program based on kwargs

    Args:
        kwargs (dict): Keyword args
    """
    # Parse args:
    (kwargs['source'], kwargs['crontab']) = _parse_crontab(**kwargs)

    # Print the header if not excluded:
    if not kwargs['exclude_header']:
        print(_build_header(**kwargs))
        print()

    # Get the detail level, the default is None, so no detail.
    detail_level = DetailLevel[_DETAIL_LEVELS.parse(kwargs)]

    # Find jobs occurring in the provided datetime range:
    for job in crony.analyser.get_job_occurrences(**kwargs):
        # Print the command / whole line based on provided options
        print(job.command if kwargs['only_command'] else job.line)

        # Also supply any other configured detail:
        if detail_level.value >= DetailLevel.COUNT.value:
            print(f"\tOccurrences: {len(job.occurrences)}")

        if detail_level.value >= DetailLevel.FULL.value:
            for occurrence in job.occurrences:
                print("\t\t" + _stringize_datetime(occurrence))
