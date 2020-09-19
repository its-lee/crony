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
#   from croniter import croniter_range
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

def _run(parser):
    # Parse args:
    pargs = vars(parser.parse_args())
    (pargs['source'], pargs['crontab']) = parse_crontab(parser, pargs)

    # Print the header if not excluded:
    if not pargs['exclude_header']:
        print(f"{pargs['source']}: {pargs['begin']} - {pargs['end']}")
        print()

    # Find jobs scheduled in the provided datetime range:
    for job in crony.analyser.get_scheduled_jobs(**pargs):
        # Output the job, with a format based on provided options
        line = None
        if pargs['exclude_occurrences']:
            line = job['command']
        else:
            s = '' if job['occurrence'] == 1 else 's'
            line = f"{job['command']} - ran {job['occurrence']} time{s}"

        print(line)
    

def main():
    try:
        parser = argparse.ArgumentParser(description=crony.manifest.description)
        def arg(*args, exclude_metavar=True, **kwargs):
            if exclude_metavar:
                kwargs['metavar'] = '\b'
            parser.add_argument(*args, **kwargs)

        version = crony.manifest.pkgname + ' ' + crony.manifest.version
        arg('--version', '-v', action='version', version=version, exclude_metavar=False)
        arg('--exclude-header', '-m', action='store_true', help="Exclude the header from the output")
        arg('--exclude-occurrences', '-m', action='store_true', help="Exclude occurrences from the output")        
        dt = { 'default': datetime.now(), 'type': _valid_datetime }
        arg('--begin', '-b', **dt, help="The datetime to begin at (YYYY-MM-DD HH:MM:SS), defaults to the current datetime")
        arg('--end', '-e', **dt, help="The datetime to end at (YYYY-MM-DD HH:MM:SS), defaults to the current datetime")
        arg('--file', '-f', help="The path to a crontab to be analysed")
        arg('--user', '-u', help="The user whose crontab is to be analysed")

        _run(parser)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        logging.exception("An error has been encountered:")
        sys.exit(1)

if __name__ == '__main__':
    main()