import sys
import os
import logging
from datetime import datetime
import argparse

from crontab import CronTab

import crony.analyser
import crony.manifest

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

def parse_crontab(parser, pargs):
    if sys.__stdin__.isatty():
        # Resolve some ambiguity in the case that both crontab references are passed:
        if pargs['input'] and pargs['user']:
            parser.error("Only one of 'input' or 'user' should be passed")
            return None

        if pargs['input']:
            return ('input', CronTab(tabfile=pargs['input']))
        elif pargs['user']:
            return (f"user:{pargs['user']}", CronTab(user=pargs['user']))
        else:
            # In the case of none of them being passed, we default to the current user.
            return ('user:current', CronTab(user=True))
    else:
        # If we're not a tty, then try to read a crontab from stdin.
        return ('stdin', CronTab(tab=sys.stdin.read()))

def main():
    try:
        parser = argparse.ArgumentParser(description=crony.manifest.description)
        def add_argument(*args, exclude_metavar=True, **kwargs):
            if exclude_metavar:
                kwargs['metavar'] = '\b'
            parser.add_argument(*args, **kwargs)

        add_argument('--version', '-v',
            action='version',
            version=crony.manifest.pkgname + ' ' + crony.manifest.version,
            exclude_metavar=False
        )
        add_argument('--exclude-header', '-m', 
            help="Exclude the header from the output",
            action='store_true'
        )
        add_argument('--exclude-occurrences', '-m', 
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

        pargs = vars(parser.parse_args())
        (pargs['source'], pargs['crontab']) = parse_crontab(parser, pargs)
        crony.analyser.analyse(**pargs)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        logging.exception("An error has been encountered:")
        sys.exit(1)

if __name__ == '__main__':
    main()