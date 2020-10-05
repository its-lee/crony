import sys
import os
import logging
from datetime import datetime

import crony.core
import crony.manifest
import crony.args

# TODO: Release automation (start by documenting the steps required)
# TODO: test all options, all usages
# TODO: make official release and update README installation section

_logger = logging.getLogger(__name__)

def _init_logging():
    """Initialise logging
    """
    # Set up the stderr log handler:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(name)25s | %(levelname)5s | %(message)s"
    ))
    logging.getLogger().addHandler(handler)

def main(args=None):
    """The application entry point
    """
    try:
        _init_logging()

        parsed_args = crony.args.parse(args)

        # Configure the log level to that passed
        logging.getLogger().setLevel(parsed_args["log_level"])

        # Run the main program
        crony.core.run(**parsed_args)

    except KeyboardInterrupt:   # pragma: no cover
        sys.exit(0)
    except Exception:   # pragma: no cover
        _logger.exception("An error has been encountered:")
        sys.exit(1)

if __name__ == "__main__":
    main()  # pragma: no cover
