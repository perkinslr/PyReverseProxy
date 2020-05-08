import sys

from .click import cli
from .proxy import run
import click.core
click.core.Exit = SystemExit


def __main__(argv=sys.argv):
    from twisted.python.log import startLogging
    startLogging(sys.stderr)
    configuration = cli.main(argv, standalone_mode=False).obj
    return run(configuration)


if __name__=='__main__':
    argv = sys.argv
    argv[0] = __package__
    
    raise SystemExit(__main__(argv))


