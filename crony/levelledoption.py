import sys

class LevelledOption:
    """Helper class to implement an argparse arguments which can have logically incrementing levels
    of effect.

    For example, log verbosity:
        --v     Log at the WARNING level
        --vv    Log at the INFO level
        --vvv   Log at the DEBUG level

    This would require constructing a LevelledOption via:
        LevelledOption('v', ['WARNING', 'INFO', 'DEBUG'])
    """

    def __init__(self, char, values):
        """Initialiser

        Args:
            char (str): The character used at the CLI
            values (iterable): The incrementing values taken for each additional char used at the CLI
        """
        self.levels = {
            char * (i + 1): v for i, v in enumerate(values)
        }

    def add_to_parser(self, parser, help_format, default=''):
        """Request the parser to add the associated arguments.

        Args:
            parser (argparse.ArgumentParser): The argument parser
            help_format (string): The help format, can use a {level} template parameter to emit that
                level in the help string.
        """
        group = parser.add_mutually_exclusive_group()
        for k, v in self.levels.items():
            group.add_argument(
                f"--{k}",
                default=default,
                action='store_true',
                help=help_format.format(level=v.lower())
            )

    def parse(self, pargs, default=None):
        """Get the value of the parsed LevelledOption, with a defined default.

        Args:
            pargs (dict): The parsed arguments
            default (any, optional): The default value if nothing is passed. Defaults to None.

        Returns:
            any: The value inferred, or default
        """
        value = [v for k, v in self.levels.items() if k in pargs and pargs[k]]
        return value[0] if value else default
