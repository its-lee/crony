import sys
import os
import logging
from datetime import datetime
from enum import Enum
import argparse

from crontab import CronTab

import crony.analyser
import crony.manifest
from crony.levelledoption import LevelledOption

# output-level help text: 'Output at the {level} level'
# todo: replace --exclude-occurrences & remove it by output-levels
# todo: make detail levels an enum
# compactness level?
# todo: split files up
# todo: missing docblocks

# todo: print another format which is just all the datetimes each job would have run.
# todo: anything else after playing around with?
# todo: put required python versions in setup.py
# todo: add requirements on python & dependencies
# todo: relative date formats might be good? https://stackoverflow.com/questions/39091969/parsing-human-readable-relative-times
# todo: test all options

# todo: travis unit tests + badge



# travis ci:
# follow:
#  - https://docs.travis-ci.com/user/tutorial/
#  - https://docs.travis-ci.com/user/languages/python/#dependency-management
# if you need to have a requirements.txt - use https://stackoverflow.com/questions/26900328/install-dependencies-from-setup-py


# todo: test: --- this is done - leaving here as this is what we wanna test!
# all options
# general behaviour in all cases
# time equal to the end point
#   from croniter import croniter_range
#   https://pypi.org/project/croniter/#iterating-over-a-range-using-cron
#   range = croniter_range(args.begin, args.end, ret_type=datetime.datetime)
#   len(range)

_logger = logging.getLogger(__name__)

_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_LOG_LEVELS = LevelledOption('v', [
    'WARNING',
    'INFO',
    'DEBUG'
])

class DetailLevel(Enum):
    NONE = 0
    COUNT = 1
    FULL = 2

_DETAIL_LEVELS = LevelledOption('d', DetailLevel.__members__.keys())

# From https://stackoverflow.com/questions/25470844/specify-format-for-input-arguments-argparse-python
def _valid_datetime(s):
    """Convert datetime-typed argparse args to datetime.datetime

    Args:
        s (str): A datetime str passed to argparse

    Raises:
        argparse.ArgumentTypeError: Raised on invalid datetime

    Returns:
        datetime.datetime: The parsed datetime
    """
    try:
        return datetime.strptime(s, _DEFAULT_DATE_FORMAT)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid datetime: '{s}'.")

def parse_crontab(pargs):
    """Parse crontab-related args

    Args:
        pargs (dict): The parsed arguments

    Returns:
        tuple: A tuple of (human readable crontab source, crontab.CronTab)
    """
    if sys.stdin.isatty():
        _input = pargs.get('input')
        _user = pargs.get('user')
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

def _init_logging(pargs):
    """Initialise logging

    Args:
        pargs (dict): The parsed args
    """
    root_logger = logging.getLogger()

    # Set up the stderr log handler:
    formatter = logging.Formatter('%(asctime)s | %(name)25s | %(levelname)5s | %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set the root/global log level - this can be configured by the user if need be:
    log_level = _LOG_LEVELS.parse(pargs, logging.ERROR)
    root_logger.setLevel(log_level)

def _stringize_datetime(dt):
    """Convert a datetime to the default format used

    Args:
        dt (datetime.datetime): A datetime object to format

    Returns:
        str: The formatted datetime
    """
    return dt.strftime(_DEFAULT_DATE_FORMAT)

def _build_header(pargs):
    """Build the header

    Args:
        pargs (dict): The parsed args
    """
    return f"For {pargs['source']}: {_stringize_datetime(pargs['begin'])} -> {_stringize_datetime(pargs['end'])}"

def _run(pargs):
    """Run the program based on parsed args

    Args:
        pargs (dict): The parsed args
    """
    # Parse args:
    (pargs['source'], pargs['crontab']) = parse_crontab(pargs)

    # Print the header if not excluded:
    if not pargs['exclude_header']:
        print(_build_header(pargs))
        print()

    # Get the detail level, the default is None, so no detail.
    detail_level = DetailLevel[_DETAIL_LEVELS.parse(pargs)]
    print(detail_level)

    # Find jobs occurring in the provided datetime range:
    for job in crony.analyser.get_job_occurrences(**pargs):
        # Print the command / whole line based on provided options
        print(job.command if pargs['only_command'] else job.line)

        if detail_level.name == 'COUNT' or detail_level.name == 'FULL':
            print(f"\tOccurrences: {len(job.occurrences)}")

        if detail_level.name == 'FULL':
            for occurrence in job.occurrences:
                print("\t\t" + _stringize_datetime(occurrence))

def main():
    """The application entry point
    """
    try:
        parser = argparse.ArgumentParser(description=crony.manifest.description)

        # Version output:
        version = crony.manifest.pkgname + ' ' + crony.manifest.version
        parser.add_argument('--version', '-V', action='version', version=version)

        # Logging options:
        _LOG_LEVELS.add_to_parser(parser, 'Log at the {level} level')

        # Time range:
        dt = { 'default': datetime.now(), 'type': _valid_datetime }
        parser.add_argument('--begin', '-b', **dt, help="The datetime to begin at (YYYY-MM-DD HH:MM:SS), defaults to the current datetime")
        parser.add_argument('--end', '-e', **dt, help="The datetime to end at (YYYY-MM-DD HH:MM:SS), defaults to the current datetime")

        # Crontab reference - only allow 0 or 1 to remove any ambiguity:
        crontab_group = parser.add_mutually_exclusive_group()
        crontab_group.add_argument('--file', '-f', help="The path to a crontab to be analysed")
        crontab_group.add_argument('--user', '-u', help="The user whose crontab is to be analysed")

        # Disabled options:
        parser.add_argument('--include-disabled', '-d', action='store_true', help="Also analyse disabled cron jobs")

        # Output options:
        parser.add_argument('--exclude-header', '-m', action='store_true', help="Exclude the header from the output")
        parser.add_argument('--only-command', '-c', action='store_true', help="Only show the command, not the full line")
        _DETAIL_LEVELS.add_to_parser(parser, 'Output at the {level} level', default=DetailLevel.NONE)

        pargs = vars(parser.parse_args())
        _init_logging(pargs)
        _run(pargs)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        _logger.exception("An error has been encountered:")
        sys.exit(1)

if __name__ == '__main__':
    main()
