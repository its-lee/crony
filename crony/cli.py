import sys
import os
import logging
from datetime import datetime
import argparse

from crony.analyser import CronTabSource, analyse
from crony.manifest import __manifest__

# todo: debug logging (+ control of this via the command line --v, --vv, --vvv)

# todo: test:
# general behaviour in all cases
# time equal to the end point
#   https://pypi.org/project/croniter/#iterating-over-a-range-using-cron
#   range = croniter_range(args.begin, args.end, ret_type=datetime.datetime)
#   len(range)

# From https://stackoverflow.com/questions/25470844/specify-format-for-input-arguments-argparse-python
def _valid_datetime(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid datetime: '{s}'.")

def _parse_args(parser):
    args = parser.parse_args()

    args.crontab = None
    if sys.__stdin__.isatty():
        # Resolve some ambiguity in the case that both crontab references are passed:
        if args.input and args.user:
            parser.error("Only one of 'input' or 'user' should be passed")

        if args.input:
            args.crontab = CronTabSource('input', tabfile=args.input)
        elif args.user:
            args.crontab = CronTabSource(f"user:{args.user}", user=args.user)
        else:
            # In the case of none of them being passed, we default to the current user.
            args.crontab = CronTabSource('user:current', user=True)
    else:
        # If we're not a tty, then try to read a crontab from stdin.
        args.crontab = CronTabSource('stdin', tab=sys.stdin.read())

    if not args.crontab:
        parser.error("A reference to a crontab must be passed")

    return args

def main():
    try:
        parser = argparse.ArgumentParser(description=__manifest__['description'])
        def add_argument(*args, **kwargs):
            parser.add_argument(*args, **kwargs)

        add_argument('--version', '-v',
            action='version',
            version=__manifest__['pkgname'] + ' ' + __manifest__['version']
        )
        add_argument('--exclude-header', '-h',
            help="Exclude the header from the output",
            action='store_true'
        )
        add_argument('--exclude-occurrences', '-o',
            help="Exclude occurrences from the output",
            action='store_true'
        )
        dt = { 'default': datetime.now(), 'type': _valid_datetime }
        add_argument('--begin', '-b',
            help="The datetime to begin at (YYYY-MM-DD HH:MM:SS), defaults to the current datetime",
            **dt
        )
        add_argument('--end', '-e',
            help="The datetime to end at (YYYY-MM-DD HH:MM:SS), defaults to the current datetime",
            **dt
        )
        add_argument('--file', '-f',
            help="The path to a crontab to be analysed"
        )
        add_argument('--user', '-u',
            help="The user whose crontab is to be analysed"
        )

        kwargs = vars(_parse_args(parser))
        analyse(**kwargs)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        logging.exception("An error has been encountered:")
        sys.exit(1)

if __name__ == '__main__':
    main()