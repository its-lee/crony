import sys
import os
import logging
from datetime import datetime
import argparse

from crony.analyser import CronTabSource, analyse
from crony.manifest import __manifest__

# https://stackoverflow.com/questions/25470844/specify-format-for-input-arguments-argparse-python
# TODO: be more permissive here?
def _valid_datetime(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid datetime: '{s}'.")

def _parse_args(parser):
    args = parser.parse_args()

    crontab = None
    if sys.__stdin__.isatty():
        # Resolve some ambiguity in the case that both crontab references are passed:
        if args.input and args.user:
            parser.error("Only one of 'input' or 'user' should be passed")

        if args.input:
            crontab = CronTabSource('input', tabfile=args.input)
        elif args.user:
            crontab = CronTabSource(f"user:{args.user}", user=args.user)
        else:
            # In the case of none of them being passed, we default to the current user.
            crontab = CronTabSource('user:current', user=True)
    else:
        # If we're not a tty, then try to read a crontab from stdin.
        crontab = CronTabSource('stdin', tab=sys.stdin.read())

    if not crontab:
        parser.error("A reference to a crontab must be passed")

    return {
        'crontab': crontab,
        'begin': args.begin,
        'end': args.end,
        'exclude_metadata': args.exclude_metadata
    }

def main():
    try:
        parser = argparse.ArgumentParser(description=__manifest__['description'])
        def add_argument(*args, exclude_metavar=True, **kwargs):
            if exclude_metavar:
                kwargs['metavar'] = '\b'
            parser.add_argument(*args, **kwargs)

        add_argument('--version', '-v',
            action='version',
            version=__manifest__['pkgname'] + ' ' + __manifest__['version'],
            exclude_metavar=False
        )
        add_argument('--exclude-metadata', '-m', 
            help="Exclude metadata from the output",
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

        parsed_args = _parse_args(parser)
        analyse(**parsed_args)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        logging.exception("An error has been encountered:")
        sys.exit(1)

if __name__ == '__main__':
    main()