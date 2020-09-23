import sys
import os
import logging
from datetime import datetime
import argparse

import dateparser

import crony.core
import crony.manifest
from crony.levelledoption import LevelledOption

_logger = logging.getLogger(__name__)

_NOW = datetime.now()

_LOG_LEVELS = LevelledOption('v', [
    'WARNING',
    'INFO',
    'DEBUG'
], default='ERROR')

_DETAIL_LEVELS = LevelledOption('d', [
    crony.core.DetailLevel.COUNT.name,
    crony.core.DetailLevel.FULL.name
], default=crony.core.DetailLevel.NONE.name)

def _valid_datetime(s):
    """Convert an argparse arg to a datetime.

    From https://stackoverflow.com/questions/25470844/specify-format-for-input-arguments-argparse-python

    The preferred, most reliable format to use is DEFAULT_DATE_FORMAT and this the one
    which is checked first. However, other formats (relative & absolute) are permitted
    by dateparser.parse().

    In the case that the dateparser package dies, the following is honestly good enough
    for us!
        datetime.strptime(s, crony.core.DEFAULT_DATE_FORMAT)

    Args:
        s (str): A datetime str to parse

    Raises:
        argparse.ArgumentTypeError: Raised on invalid datetime

    Returns:
        datetime: The parsed datetime
    """
    try:
        # It took some digging to work out what's actually meant when passing
        # the date_formats parameter. The docs make it sound like *only* the
        # formats in date_formats are permitted, but it's actually a known format which
        # you inject into the parsing algorithm to attempt before using fallback
        # techniques.
        #
        # It turns out that's essentially what we want.
        #
        # It allows a preferred, reliable absolute datetime format to be attempted
        # *before* using any fallback techniques which *might* be able to generate
        # a datetime object, but may have done so using an unclear/unknowable
        # format which the user then clearly didn't intend - the principle of least
        # surprise.
        #
        # We'd rather users in that case to use our reliable format and for us to
        # know that's the format which will be used - the principle of least surprise.
        #
        # The code below indicates the following parsing order is used, which we're
        # okay with:
        #   - timestamp (numeric) - fine, that's understandable by a user.
        #   - relative formats - fine, it's not going accidentally catch other
        #     absolute formats, and we want these to work.
        #   - our reliable absolute format - good, that's what we want.
        #   - then any absolute fallbacks - meh, but allows for some flexibility
        #     in absolute formats passed.
        #
        # From https://github.com/scrapinghub/dateparser/blob/v0.3.4/dateparser/date.py,
        # in _DateLanguageParser._parse:
        #
        # for parser in (
        #     self._try_timestamp,
        #     self._try_freshness_parser,
        #     self._try_given_formats,
        #     self._try_dateutil_parser,
        #     self._try_hardcoded_formats,
        # ):
        dt = dateparser.parse(s, date_formats=[
            crony.core.DEFAULT_DATE_FORMAT
        ])
        if not dt:
            raise ValueError(
                "The following could not be parsed to a datetime: '{s}'.")
        return dt
    except Exception:
        message = f"Invalid datetime: '{s}'."
        _logger.exception(message)
        raise argparse.ArgumentTypeError(message)

def _add_begin_end_argument(parser, begin_end, options):
    help_ = 'the datetime to {begin_end} at, defaults to the current datetime. The preferred format is (YYYY-MM-DD HH:MM:SS), however - other relative and absolute formats are permitted'
    parser.add_argument(
        *options,
        default=_NOW,
        type=_valid_datetime,
        metavar='\b',
        help=help_.format(type=type)
    )

def parse(args=None):
    """Parse program args

    Args:
        args (list, optional): When defaulted, uses the arguments entered at the terminal, else uses
                               those passed.
    Returns:
        dict: The parsed arguments
    """
    parser = argparse.ArgumentParser(description=crony.manifest.description)

    # Version output:
    parser.add_argument(
        '--version', '-V',
        action='version',
        version=f"{crony.manifest.pkgname}@{crony.manifest.version}"
    )

    # Logging options:
    _LOG_LEVELS.add_to_parser(parser, 'log at the {level} level')

    # Datetime range:
    _add_begin_end_argument(parser, 'begin', ['--begin', '-b'])
    _add_begin_end_argument(parser, 'end', ['--end', '-e'])

    # Crontab reference - only allow 0 or 1 to remove any ambiguity:
    crontab_group = parser.add_mutually_exclusive_group()
    crontab_group.add_argument(
        '--file', '-f',
        metavar='\b',
        help="the path to a crontab to be analysed"
    )
    crontab_group.add_argument(
        '--user', '-u',
        metavar='\b',
        help="the user whose crontab is to be analysed"
    )

    # Disabled options:
    parser.add_argument(
        '--include-disabled', '-i',
        action='store_true',
        help="also analyse disabled cron jobs"
    )

    # Output options:
    parser.add_argument(
        '--exclude-header', '-x',
        action='store_true',
        help="exclude the header from the output"
    )

    parser.add_argument(
        '--only-command', '-c',
        action='store_true',
        help="only show the command, not the full line"
    )

    _DETAIL_LEVELS.add_to_parser(parser, 'output at the {level} level')

    args = vars(parser.parse_args())
    args['log_level'] = _LOG_LEVELS.parse(args)
    args['detail_level'] = crony.core.DetailLevel[_DETAIL_LEVELS.parse(args)]
    args['tab'] = None if sys.stdin.isatty() else sys.stdin.read()

    return args
