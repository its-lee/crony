import sys
import os
import logging
from datetime import datetime
import argparse

import crony.core
import crony.manifest
from crony.levelledoption import LevelledOption

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

_LOG_LEVELS = LevelledOption('v', [
    'WARNING',
    'INFO',
    'DEBUG'
], default='ERROR')

_DETAIL_LEVELS = LevelledOption('d', [
    crony.core.DetailLevel.COUNT.name,
    crony.core.DetailLevel.FULL.name
], default=crony.core.DetailLevel.NONE.name)

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
        return datetime.strptime(s, crony.core.DEFAULT_DATE_FORMAT)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid datetime: '{s}'.")

def _init_logging(args):
    """Initialise logging

    Args:
        args (dict): The parsed args
    """
    root_logger = logging.getLogger()

    # Set up the stderr log handler:
    formatter = logging.Formatter('%(asctime)s | %(name)25s | %(levelname)5s | %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set the root/global log level:
    root_logger.setLevel(_LOG_LEVELS.parse(args))

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
        _DETAIL_LEVELS.add_to_parser(parser, 'Output at the {level} level')

        parsed_args = vars(parser.parse_args())
        _init_logging(parsed_args)
        crony.core.run(**parsed_args)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        _logger.exception("An error has been encountered:")
        sys.exit(1)

if __name__ == '__main__':
    main()
