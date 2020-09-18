import sys
import os
import logging
from datetime import datetime

import argparse
#import croniter

# todo: restore this when we're a proper package again
#from crony.manifest import __manifest__
# ... and get rid of this
__manifest__ = {
    'pkgname': 'crony',
    'version': '1.0.0',
    'description': 'A simple CLI program to analyse crontabs for executions in given periods.'
}

# todo: read passed filename, stdin, or passed named user/group crontabs

# todo: tests:
#       getting version     - fine

_datetime_format = "%Y-%m-%d %H:%M:%S"

# https://stackoverflow.com/questions/25470844/specify-format-for-input-arguments-argparse-python
# TODO: be more permissive here?
def valid_datetime(s):
    try:
        return datetime.strptime(s, _datetime_format)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date: '{s}'.")

def get_version():
    return __manifest__['pkgname'] + ' ' + __manifest__['version']

def main():
    parser = argparse.ArgumentParser(description=__manifest__['description'])
    def add_argument(*args, exclude_metavar=True, **kwargs):
        if exclude_metavar:
            kwargs['metavar'] = '\b'
        parser.add_argument(*args, **kwargs)


    add_argument(
        '--version',
        '-v',
        action='version',
        version=__manifest__['pkgname'] + ' ' + __manifest__['version'],
        exclude_metavar=False
    )

    add_argument(
        '--start',
        '-s',
        default=datetime.now(),
        type=valid_datetime,
        help="The datetime to start analysing from (YYYY-MM-DD HH:MM:SS), defaults to the current datetime"
    )
    add_argument(
        '--end',
        '-e',
        default=datetime.now(),
        type=valid_datetime,
        help="The datetime to stop analysing to (YYYY-MM-DD HH:MM:SS), defaults to the current datetime"
    )

    add_argument(
        '--file',
        '-f',
        help="The path to a crontab to analyse"
    )
    add_argument(
        '--user',
        '-u',
        help="The user whose crontab is to be analysed"
    )
    add_argument(
        '--group',
        '-g',
        help="The group whose crontab is to be analysed"
    )

    if sys.__stdin__.isatty():
        pass
        # todo : parse args
    else:
        crontab = sys.stdin.read()
        # todo use this!
        # https://pypi.org/project/python-crontab/
        print(crontab)

    # TODO: Implement the following:
    # you must have either:
    #   have passed the crontab via stdin
    #   or have exactly 1 of (file, user, group) passed

    # on failure to do this, call:
    #parser.error('hello')


    args = parser.parse_args()


    # todo: print these nicely as a header (and indicate the time delta)
    print(args.start)
    print(args.end)



if __name__ == '__main__':
    main()