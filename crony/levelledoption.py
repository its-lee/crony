import sys

class LevelledOption:
    """Helper class to implement an argparse arguments which can have logically incrementing levels
    of effect.

    For example, log verbosity:
        -v     Log at the WARNING level
        -vv    Log at the INFO level
        -vvv   Log at the DEBUG level

    This would require constructing a LevelledOption via:
        LevelledOption('v', ['WARNING', 'INFO', 'DEBUG'])
    """

    def __init__(self, char, values, default=None):
        """Initialiser

        Args:
            char (str): The character used at the CLI
            values (iterable): The incrementing values taken for each additional char used at the CLI
            default (any): The fallback value when parsing if no relevant option has been passed
        """
        self.levels = {
            char * (i + 1): v for i, v in enumerate(values)
        }
        self.default = default

    def add_to_parser(self, parser, help_format):
        """Request the parser to add the associated arguments.

        Args:
            parser (argparse.ArgumentParser): The argument parser
            help_format (string): The help format, can use a {level} template parameter to emit that
                level in the help string.
        """
        group = parser.add_mutually_exclusive_group()
        for k, v in self.levels.items():
            group.add_argument(
                f"-{k}",
                default='',
                action='store_true',
                help=help_format.format(level=v.lower())
            )

    def parse(self, pargs):
        """Get the value of the parsed LevelledOption, with a defined default.

        Args:
            pargs (dict): The parsed arguments

        Returns:
            any: The value inferred, or default
        """
        value = [v for k, v in self.levels.items() if k in pargs and pargs[k]]
        return value[0] if value else self.default
