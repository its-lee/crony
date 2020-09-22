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

def _parse_crontab(file=None, user=None, **kwargs):
    """Parse crontab-related args

    Args:
        file (str): A file name containing a crontab
        user (str): A user name to fetch a crontab for

    Returns:
        tuple: A tuple of (human readable crontab source, crontab.CronTab)
    """
    if not sys.stdin.isatty():
        # If we're not a tty, then try to read a crontab from stdin.
        return ('stdin', CronTab(tab=sys.stdin.read()))

    # Else, infer from the supplied args
    if file:
        return ('input', CronTab(tabfile=file))
    elif user:
        return (f"user:{user}", CronTab(user=user))
    else:
        # In the case of none of them being passed, we default to the current user.
        return ('user:current', CronTab(user=True))

def _stringize_datetime(dt):
    """Convert a datetime to the default format used

    Args:
        dt (datetime): A datetime object to format

    Returns:
        str: The formatted datetime
    """
    return dt.strftime(DEFAULT_DATE_FORMAT)

def _build_header(source=None, begin=None, end=None, **kwargs):
    """Build the header

    Args:
        source (str): The crontab source specifier
        begin (datetime): The begin datetime
        end (datetime): The end datetime
    """
    return f"For {source}: {_stringize_datetime(begin)} -> {_stringize_datetime(end)}"

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
