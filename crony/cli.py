import sys
import os
import logging
from datetime import datetime

import crony.core
import crony.manifest
import crony.args

# todo: travis unit tests + badge
# https://pypi.org/project/parameterized/
# travis ci:

# remove requirements/* ?
# remove tox.ini if we're not using it!

# tests:
# @hourly / Users/dog/full-barkup - abc > /dev/null 2 > &1  # Full hourly barkup
# * * * * * / Users/dog/scan-dog-files > /dev/null 2 > &1 # Check dog files for erroars

# make official release and update README installation section
# TODO: Handle this - "59 11 0 0 0" which is an invalid cron line - we should probably update the code to emit this better
        
# TODO: test things like @hourly etc
# TODO: test: --- this is done - leaving here as this is what we wanna test!
# TODO: test all options, all usages
# TODO: Address all TODO-s

_logger = logging.getLogger(__name__)

def _init_logging():
    """Initialise logging
    """
    # Set up the stderr log handler:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(name)25s | %(levelname)5s | %(message)s'
    ))
    logging.getLogger().addHandler(handler)

def main():
    """The application entry point
    """
    try:
        _init_logging()

        args = crony.args.parse()

        # Configure the log level to that passed
        logging.getLogger().setLevel(args['log_level'])
        # Run the main program
        crony.core.run(**args)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        _logger.exception("An error has been encountered:")
        sys.exit(1)

if __name__ == '__main__':
    main()
