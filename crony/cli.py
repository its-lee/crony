import sys
import os
import logging
from datetime import datetime
import argparse

from crontab import CronTab

import crony.analyser
import crony.manifest

# todo: print full crontab line on output (or maybe make this configurable?):
# compactness level?
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

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Initialise log levels
LOG_LEVELS = {
    'v' * (i + 1): v for i, v in enumerate([ 'WARNING', 'INFO', 'DEBUG' ])
}

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
        return datetime.strptime(s, DEFAULT_DATE_FORMAT)
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
    log_level = [ v for k, v in LOG_LEVELS.items() if k in pargs and pargs[k] ]
    log_level = log_level[0] if log_level else logging.ERROR
    root_logger.setLevel(log_level)

def _build_header(pargs):
    """Build the header

    Args:
        pargs (dict): The parsed args
    """
    begin = pargs['begin'].strftime(DEFAULT_DATE_FORMAT)
    end = pargs['end'].strftime(DEFAULT_DATE_FORMAT)

    additions = []
    if pargs['include_disabled']:
        additions.append('disabled included')
    if pargs['exclude_occurrences']:
        additions.append('occurrences excluded')

    additions_text = f"({', '.join(additions)})" if additions else ''
    return f"{pargs['source']}: {begin} -> {end} {additions_text}"

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

    # Find jobs occurring in the provided datetime range:
    for job in crony.analyser.get_job_occurrences(**pargs):
        # Output the job, with a format based on provided options
        line = None
        if pargs['exclude_occurrences']:
            line = job.command
        else:
            occurrence_count = len(job.occurrences)
            s = '' if occurrence_count == 1 else 's'
            line = f"{job.command} - ran {occurrence_count} time{s}"

        print(line)


def main():
    """The application entry point
    """
    try:
        parser = argparse.ArgumentParser(description=crony.manifest.description)
        def arg(*args, group=None, **kwargs):
            to = group or parser
            to.add_argument(*args, **kwargs)

        # Version output:
        version = crony.manifest.pkgname + ' ' + crony.manifest.version
        arg('--version', '-V', action='version', version=version)

        # Logging options:
        logging_group = parser.add_mutually_exclusive_group()
        for k, v in LOG_LEVELS.items():
            arg(f"--{k}", default='', action='store_true', group=logging_group, help=f"Log at the {v.lower()} level")

        # Time range:
        dt = { 'default': datetime.now(), 'type': _valid_datetime }
        arg('--begin', '-b', **dt, help="The datetime to begin at (YYYY-MM-DD HH:MM:SS), defaults to the current datetime")
        arg('--end', '-e', **dt, help="The datetime to end at (YYYY-MM-DD HH:MM:SS), defaults to the current datetime")

        # Crontab reference - only allow 0 or 1 to remove any ambiguity:
        crontab_group = parser.add_mutually_exclusive_group()
        arg('--file', '-f', group=crontab_group, help="The path to a crontab to be analysed")
        arg('--user', '-u', group=crontab_group, help="The user whose crontab is to be analysed")

        # Analysis options:
        arg('--include-disabled', '-d', action='store_true', help="Also analyse disabled cron jobs")

        # Output options:
        arg('--exclude-header', '-m', action='store_true', help="Exclude the header from the output")
        arg('--exclude-occurrences', '-o', action='store_true', help="Exclude occurrences from the output")

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
